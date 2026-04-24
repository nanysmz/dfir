from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from .models import EvidenceFile


@dataclass(slots=True)
class NormalizedTextContent:
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedImageContent:
    labels: list[dict] = field(default_factory=list)
    detections: list[dict] = field(default_factory=list)
    ocr_text: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ExtractionResult:
    status: str
    content_type: str
    content: NormalizedTextContent | NormalizedImageContent | None = None
    metadata: dict = field(default_factory=dict)
    reason: str = ""

    @classmethod
    def unsupported(
        cls, *, content_type: str, reason: str, metadata: dict | None = None
    ):
        return cls(
            status="unsupported",
            content_type=content_type,
            metadata=metadata or {},
            reason=reason,
        )

    @classmethod
    def failed(cls, *, content_type: str, reason: str, metadata: dict | None = None):
        return cls(
            status="failed",
            content_type=content_type,
            metadata=metadata or {},
            reason=reason,
        )

    @classmethod
    def supported(
        cls,
        *,
        content_type: str,
        content: NormalizedTextContent | NormalizedImageContent,
        metadata: dict | None = None,
    ):
        return cls(
            status="supported",
            content_type=content_type,
            content=content,
            metadata=metadata or {},
        )


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._parts.append(data.strip())

    def text(self) -> str:
        return "\n".join(self._parts)


TEXT_SUFFIXES = {
    ".txt": EvidenceFile.FileKind.TEXT,
    ".log": EvidenceFile.FileKind.TEXT,
    ".csv": EvidenceFile.FileKind.TEXT,
}
HTML_SUFFIXES = {".html", ".htm"}
PDF_SUFFIXES = {".pdf"}
OFFICE_SUFFIXES = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}


def infer_file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return EvidenceFile.FileKind.TEXT
    if suffix in HTML_SUFFIXES:
        return EvidenceFile.FileKind.HTML
    if suffix in PDF_SUFFIXES:
        return EvidenceFile.FileKind.PDF
    if suffix in OFFICE_SUFFIXES:
        return (
            EvidenceFile.FileKind.DOCX
            if suffix == ".docx"
            else EvidenceFile.FileKind.DOC
        )
    if suffix in IMAGE_SUFFIXES:
        return EvidenceFile.FileKind.IMAGE
    return EvidenceFile.FileKind.UNKNOWN


def ensure_evidence_file(path: str | Path) -> EvidenceFile:
    path = Path(path)
    stat = path.stat()
    defaults = {
        "display_name": path.name,
        "file_kind": infer_file_kind(path),
        "size_bytes": stat.st_size,
    }
    evidence_file, _ = EvidenceFile.objects.update_or_create(
        source_path=str(path),
        defaults=defaults,
    )
    return evidence_file


def extract_evidence_content(evidence_file: EvidenceFile) -> ExtractionResult:
    path = Path(evidence_file.source_path)
    file_kind = evidence_file.file_kind
    base_metadata = {"source_path": evidence_file.source_path, "file_kind": file_kind}

    if not path.exists():
        return ExtractionResult.failed(
            content_type=file_kind,
            reason="Source file does not exist on disk.",
            metadata=base_metadata,
        )

    if file_kind == EvidenceFile.FileKind.TEXT:
        return _extract_text(path, base_metadata)
    if file_kind == EvidenceFile.FileKind.HTML:
        return _extract_html(path, base_metadata)
    if file_kind in {
        EvidenceFile.FileKind.PDF,
        EvidenceFile.FileKind.DOC,
        EvidenceFile.FileKind.DOCX,
    }:
        return ExtractionResult.unsupported(
            content_type=file_kind,
            reason="Extractor adapter not implemented yet for this document format.",
            metadata=base_metadata,
        )
    if file_kind == EvidenceFile.FileKind.IMAGE:
        return _extract_image(evidence_file, base_metadata)
    return ExtractionResult.unsupported(
        content_type=file_kind,
        reason="No extractor registered for this file type.",
        metadata=base_metadata,
    )


def _extract_text(path: Path, metadata: dict) -> ExtractionResult:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return ExtractionResult.failed(
            content_type="text",
            reason=str(exc),
            metadata=metadata,
        )

    return ExtractionResult.supported(
        content_type="text",
        content=NormalizedTextContent(
            text=text,
            metadata={
                "line_count": len(text.splitlines()),
                "character_count": len(text),
            },
        ),
        metadata=metadata,
    )


def _extract_html(path: Path, metadata: dict) -> ExtractionResult:
    try:
        raw_html = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return ExtractionResult.failed(
            content_type="html",
            reason=str(exc),
            metadata=metadata,
        )

    parser = _HTMLTextExtractor()
    parser.feed(raw_html)
    text = parser.text()
    return ExtractionResult.supported(
        content_type="text",
        content=NormalizedTextContent(
            text=text,
            metadata={
                "source_format": "html",
                "character_count": len(text),
            },
        ),
        metadata=metadata,
    )


def _extract_image(evidence_file: EvidenceFile, metadata: dict) -> ExtractionResult:
    image_metadata = evidence_file.metadata or {}
    return ExtractionResult.supported(
        content_type="image",
        content=NormalizedImageContent(
            labels=image_metadata.get("image_labels", []),
            detections=image_metadata.get("image_detections", []),
            ocr_text=image_metadata.get("ocr_text", ""),
            metadata={
                "source_format": evidence_file.file_kind,
                "analysis_ready": True,
                "placeholder_engine": True,
            },
        ),
        metadata=metadata,
    )
