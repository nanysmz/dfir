from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def default_dict() -> dict:
    return {}


def default_list() -> list:
    return []


class EvidenceFile(models.Model):
    class FileKind(models.TextChoices):
        TEXT = "text", "Text"
        HTML = "html", "HTML"
        PDF = "pdf", "PDF"
        DOC = "doc", "DOC"
        DOCX = "docx", "DOCX"
        IMAGE = "image", "Image"
        UNKNOWN = "unknown", "Unknown"

    source_path = models.CharField(max_length=1024, unique=True)
    display_name = models.CharField(max_length=255)
    file_kind = models.CharField(
        max_length=32,
        choices=FileKind.choices,
        default=FileKind.UNKNOWN,
    )
    sha256 = models.CharField(max_length=64, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["source_path"]

    def __str__(self) -> str:
        return self.display_name or self.source_path


class PericiaPoint(models.Model):
    class PointFamily(models.TextChoices):
        TEXT_EMAIL_SEARCH = "text_email_search", "Text email search"
        TEXT_KEYWORD_SEARCH = "text_keyword_search", "Text keyword search"
        IMAGE_CHARACTERISTIC_DETECTION = (
            "image_characteristic_detection",
            "Image characteristic detection",
        )

    class MatchingMode(models.TextChoices):
        EXACT = "exact", "Exact"
        DOMAIN = "domain", "Domain"
        REGEX = "regex", "Regex"
        ANY = "any", "Any term"
        ALL = "all", "All terms"
        PHRASE = "phrase", "Phrase"
        LABEL = "label", "Label"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    point_family = models.CharField(max_length=64, choices=PointFamily.choices)
    matching_mode = models.CharField(max_length=32, choices=MatchingMode.choices)
    parameters = models.JSONField(default=default_dict, blank=True)
    scope = models.JSONField(default=default_dict, blank=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        errors: dict[str, list[str]] = {}

        if not isinstance(self.parameters, dict):
            errors.setdefault("parameters", []).append(
                "Parameters must be a JSON object."
            )
        if not isinstance(self.scope, dict):
            errors.setdefault("scope", []).append("Scope must be a JSON object.")

        if errors:
            raise ValidationError(errors)

        if self.point_family == self.PointFamily.TEXT_EMAIL_SEARCH:
            self._validate_email_search(errors)
        elif self.point_family == self.PointFamily.TEXT_KEYWORD_SEARCH:
            self._validate_keyword_search(errors)
        elif self.point_family == self.PointFamily.IMAGE_CHARACTERISTIC_DETECTION:
            self._validate_image_detection(errors)

        if errors:
            raise ValidationError(errors)

    def _validate_email_search(self, errors: dict[str, list[str]]) -> None:
        allowed_modes = {
            self.MatchingMode.EXACT,
            self.MatchingMode.DOMAIN,
            self.MatchingMode.REGEX,
        }
        if self.matching_mode not in allowed_modes:
            errors.setdefault("matching_mode", []).append(
                "Email search points require exact, domain, or regex mode."
            )
        value = self.parameters.get("value")
        if not value:
            errors.setdefault("parameters", []).append(
                "Email search points require a non-empty 'value'."
            )

    def _validate_keyword_search(self, errors: dict[str, list[str]]) -> None:
        allowed_modes = {
            self.MatchingMode.ANY,
            self.MatchingMode.ALL,
            self.MatchingMode.PHRASE,
            self.MatchingMode.REGEX,
        }
        if self.matching_mode not in allowed_modes:
            errors.setdefault("matching_mode", []).append(
                "Keyword search points require any, all, phrase, or regex mode."
            )
        terms = self.parameters.get("terms")
        if not isinstance(terms, list) or not [
            term for term in terms if str(term).strip()
        ]:
            errors.setdefault("parameters", []).append(
                "Keyword search points require a non-empty 'terms' list."
            )

    def _validate_image_detection(self, errors: dict[str, list[str]]) -> None:
        if self.matching_mode != self.MatchingMode.LABEL:
            errors.setdefault("matching_mode", []).append(
                "Image characteristic points currently require label mode."
            )
        targets = self.parameters.get("target_labels")
        if not isinstance(targets, list) or not [
            label for label in targets if str(label).strip()
        ]:
            errors.setdefault("parameters", []).append(
                "Image characteristic points require 'target_labels'."
            )
        threshold = self.parameters.get("min_confidence", 0.0)
        if not isinstance(threshold, (float, int)) or not 0 <= float(threshold) <= 1:
            errors.setdefault("parameters", []).append(
                "'min_confidence' must be a number between 0 and 1."
            )


class PericiaExecution(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    pericia_point = models.ForeignKey(
        PericiaPoint,
        on_delete=models.PROTECT,
        related_name="executions",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    scope_snapshot = models.JSONField(default=default_dict, blank=True)
    engine_metadata = models.JSONField(default=default_dict, blank=True)
    analyzed_files_count = models.PositiveIntegerField(default=0)
    unsupported_files_count = models.PositiveIntegerField(default=0)
    failed_files_count = models.PositiveIntegerField(default=0)
    matched_files_count = models.PositiveIntegerField(default=0)
    findings_count = models.PositiveIntegerField(default=0)
    unsupported_files = models.JSONField(default=default_list, blank=True)
    failed_files = models.JSONField(default=default_list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.pericia_point.name} @ {self.started_at.isoformat()}"


class PericiaFinding(models.Model):
    execution = models.ForeignKey(
        PericiaExecution,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    pericia_point = models.ForeignKey(
        PericiaPoint,
        on_delete=models.PROTECT,
        related_name="findings",
    )
    evidence_file = models.ForeignKey(
        EvidenceFile,
        on_delete=models.PROTECT,
        related_name="findings",
    )
    matched_value = models.TextField()
    context = models.TextField(blank=True)
    confidence = models.FloatField(null=True, blank=True)
    extraction_metadata = models.JSONField(default=default_dict, blank=True)
    engine_metadata = models.JSONField(default=default_dict, blank=True)
    source_locator = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.pericia_point.name}: {self.matched_value}"
