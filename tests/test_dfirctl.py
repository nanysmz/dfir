from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DFIRCTL = REPO_ROOT / "bin" / "dfirctl"


def test_dfirctl_help_mentions_stop_alias():
    result = subprocess.run(
        ["bash", str(DFIRCTL), "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--down, --stop" in result.stdout


def _make_docker_mock(tmp_path):
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    docker_mock = fake_bin / "docker"
    docker_mock.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"${DFIRCTL_DOCKER_LOG}\"\n"
        "exit 0\n",
        encoding="utf-8",
    )
    docker_mock.chmod(docker_mock.stat().st_mode | stat.S_IXUSR)
    return fake_bin


def test_dfirctl_stop_calls_docker_compose_down(tmp_path):
    fake_bin = _make_docker_mock(tmp_path)
    docker_log = tmp_path / "docker.log"

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    env["DFIRCTL_DOCKER_LOG"] = str(docker_log)

    result = subprocess.run(
        ["bash", str(DFIRCTL), "--stop"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert docker_log.read_text(encoding="utf-8").splitlines() == ["compose down"]


def test_dfirctl_restart_reconfigures_and_starts_with_same_volumes(tmp_path):
    fake_bin = _make_docker_mock(tmp_path)
    docker_log = tmp_path / "docker.log"

    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    output_dir.mkdir()

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    env["DFIRCTL_DOCKER_LOG"] = str(docker_log)

    result = subprocess.run(
        [
            "bash",
            str(DFIRCTL),
            "--restart",
            "--no-build",
            "--foreground",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert docker_log.read_text(encoding="utf-8").splitlines() == [
        "compose down",
        "image inspect dfir-app:local",
        "compose up",
    ]


def test_dfirctl_output_creates_directory_if_missing(tmp_path):
    fake_bin = _make_docker_mock(tmp_path)
    docker_log = tmp_path / "docker.log"

    input_dir = tmp_path / "in"
    input_dir.mkdir()
    output_dir = tmp_path / "out" / "new_case"   # does not exist yet

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    env["DFIRCTL_DOCKER_LOG"] = str(docker_log)

    result = subprocess.run(
        [
            "bash",
            str(DFIRCTL),
            "--no-build",
            "--foreground",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_dir.is_dir(), "output directory should have been created"
