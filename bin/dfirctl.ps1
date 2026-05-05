param(
    [string]$InputPath,
    [string]$OutputPath,
    [switch]$Build,
    [switch]$Foreground,
    [switch]$NoBuild,
    [switch]$Status,
    [switch]$Down,
    [switch]$Stop,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Assert-Docker {
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) {
        Write-Error "Docker was not found on PATH."
    }
}

function Test-AppImage {
    docker image inspect dfir-app:local *> $null
    return $LASTEXITCODE -eq 0
}

function Resolve-ExistingDirectory([string]$Label, [string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue -PathType Container)) {
        Write-Error "$Label directory does not exist: $PathValue"
    }
    return (Resolve-Path -LiteralPath $PathValue).Path
}

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Select-Folder([string]$Description) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = $Description
    $dialog.ShowNewFolderButton = $false
    $result = $dialog.ShowDialog()
    if ($result -ne [System.Windows.Forms.DialogResult]::OK -or [string]::IsNullOrWhiteSpace($dialog.SelectedPath)) {
        throw "Folder selection canceled."
    }
    return $dialog.SelectedPath
}

function Set-DefaultEnv([string]$Name, [string]$Value) {
    if (-not [Environment]::GetEnvironmentVariable($Name, "Process")) {
        [Environment]::SetEnvironmentVariable($Name, $Value, "Process")
    }
}

function Set-RuntimeEnv([string]$InputDir, [string]$OutputDir) {
    Set-DefaultEnv "CELERY_BROKER_URL" "redis://redis:6379/0"
    Set-DefaultEnv "CELERY_RESULT_BACKEND" "redis://redis:6379/0"
    Set-DefaultEnv "DFIR_WEB_PORT" "8000"
    Set-DefaultEnv "DJANGO_ALLOWED_HOSTS" "localhost,127.0.0.1,0.0.0.0"
    Set-DefaultEnv "DJANGO_DEBUG" "true"
    Set-DefaultEnv "DJANGO_SECRET_KEY" "local-dev-insecure-change-me"
    Set-DefaultEnv "DJANGO_SUPERUSER_EMAIL" "admin@example.local"
    Set-DefaultEnv "DJANGO_SUPERUSER_PASSWORD" "admin"
    Set-DefaultEnv "DJANGO_SUPERUSER_USERNAME" "admin"
    Set-DefaultEnv "POSTGRES_DB" "dfir"
    Set-DefaultEnv "POSTGRES_HOST" "postgres"
    Set-DefaultEnv "POSTGRES_PASSWORD" "dfir"
    Set-DefaultEnv "POSTGRES_PORT" "5432"
    Set-DefaultEnv "POSTGRES_USER" "dfir"
    [Environment]::SetEnvironmentVariable("EVIDENCE_INPUT_HOST_PATH", $InputDir, "Process")
    [Environment]::SetEnvironmentVariable("EVIDENCE_OUTPUT_HOST_PATH", $OutputDir, "Process")
}

Assert-Docker
Set-Location $RootDir

if ($Status) {
    docker compose ps
    exit $LASTEXITCODE
}

if ($Down -or $Stop) {
    docker compose down
    exit $LASTEXITCODE
}

if (-not $InputPath) {
    try {
        $InputPath = Select-Folder "Select the evidence input directory (read-only mount)"
    } catch {
        $InputPath = Read-Host "Evidence input directory mounted read-only"
    }
}

if (-not $OutputPath) {
    try {
        $OutputPath = Select-Folder "Select the evidence output directory (writable mount)"
    } catch {
        $OutputPath = Read-Host "Evidence output directory mounted writable"
    }
}

$InputPath = Resolve-ExistingDirectory "Evidence input" $InputPath
Ensure-Directory $OutputPath
$OutputPath = Resolve-ExistingDirectory "Evidence output" $OutputPath

Set-RuntimeEnv $InputPath $OutputPath

Write-Host "Runtime configuration loaded from process environment."
Write-Host "Input  -> $InputPath mounted at /evidence/input read-only"
Write-Host "Output -> $OutputPath mounted at /evidence/output writable"

if ($Restart) {
    docker compose down
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Build) {
    docker compose build web
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} elseif (-not $NoBuild) {
    if (Test-AppImage) {
        Write-Host "Using existing image dfir-app:local. Pass -Build to rebuild."
    } else {
        Write-Host "Image dfir-app:local not found; building it once."
        docker compose build web
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
} elseif (-not (Test-AppImage)) {
    Write-Error "dfir-app:local image not found. Run .\bin\dfirctl.ps1 -Build first."
}

if ($Foreground) {
    docker compose up
} else {
    docker compose up --detach
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    docker compose ps
    Write-Host "Open http://localhost:8000/health/"
}
