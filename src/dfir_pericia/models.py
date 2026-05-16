from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from .analysis_playbooks import (
    build_suggested_playbook_actions,
    build_structured_actions,
    build_technique_action_label,
    classify_requested_point_text,
    normalize_structured_actions,
)


def default_dict() -> dict:
    return {}


def default_list() -> list:
    return []


REPORT_MINIMUM_SECTION_TYPES = {
    "object",
    "obtained_information",
    "conclusions",
}

STANDARD_REPORT_SECTION_DEFINITIONS = (
    {
        "section_type": "object",
        "order": 1,
        "title": "Objeto",
        "structured_data": {"template_origin": "standard", "content_mode": "manual"},
    },
    {
        "section_type": "offered_elements",
        "order": 2,
        "title": "Elementos ofrecidos",
        "structured_data": {
            "template_origin": "standard",
            "content_mode": "derived_editable",
            "suggested_source": "evidence_items",
        },
    },
    {
        "section_type": "tools",
        "order": 3,
        "title": "Herramientas",
        "structured_data": {"template_origin": "standard", "content_mode": "manual"},
    },
    {
        "section_type": "methodology",
        "order": 4,
        "title": "Metodología",
        "structured_data": {"template_origin": "standard", "content_mode": "manual"},
    },
    {
        "section_type": "obtained_information",
        "order": 5,
        "title": "Información obtenida",
        "structured_data": {
            "template_origin": "standard",
            "content_mode": "derived_editable",
            "suggested_source": "device_analysis_results",
        },
    },
    {
        "section_type": "conclusions",
        "order": 6,
        "title": "Conclusiones",
        "structured_data": {"template_origin": "standard", "content_mode": "manual"},
    },
    {
        "section_type": "evidence",
        "order": 7,
        "title": "Evidencia",
        "structured_data": {"template_origin": "standard", "content_mode": "manual"},
    },
    {
        "section_type": "annex",
        "order": 8,
        "title": "Anexo",
        "structured_data": {"template_origin": "standard", "content_mode": "manual"},
    },
)


def report_section_has_substantive_content(section) -> bool:
    content = str(getattr(section, "content", "") or "").strip()
    if content:
        return True
    structured_data = getattr(section, "structured_data", None)
    if not isinstance(structured_data, dict):
        return False
    generated_content = str(structured_data.get("generated_content") or "").strip()
    return bool(generated_content)


class EvidenceFile(models.Model):
    IDENTITY_SCOPE_GLOBAL = "global"

    class FileKind(models.TextChoices):
        TEXT = "text", "Text"
        HTML = "html", "HTML"
        PDF = "pdf", "PDF"
        DOC = "doc", "DOC"
        DOCX = "docx", "DOCX"
        IMAGE = "image", "Image"
        UNKNOWN = "unknown", "Unknown"

    identity_scope = models.CharField(
        max_length=255,
        default=IDENTITY_SCOPE_GLOBAL,
        db_index=True,
    )
    source_path = models.CharField(max_length=1024)
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
        verbose_name = "archivo de evidencia"
        verbose_name_plural = "archivos de evidencia"
        constraints = [
            models.UniqueConstraint(
                fields=("identity_scope", "source_path"),
                name="unique_evidence_file_identity_scope_source_path",
            )
        ]

    def __str__(self) -> str:
        return self.display_name or self.source_path

    @classmethod
    def case_identity_scope(cls, pericia_case_id: int | None) -> str:
        if pericia_case_id:
            return f"case:{pericia_case_id}"
        return cls.IDENTITY_SCOPE_GLOBAL

    def scoped_pericia_case_id(self) -> int | None:
        raw_scope = str(self.identity_scope or "").strip()
        if not raw_scope.startswith("case:"):
            return None
        try:
            return int(raw_scope.split(":", 1)[1])
        except (TypeError, ValueError):
            return None

    def scoped_pericia_case(self):
        scoped_case_id = self.scoped_pericia_case_id()
        if scoped_case_id is None:
            return None
        return PericiaCase.objects.filter(pk=scoped_case_id).first()

    def identity_scope_label(self) -> str:
        scoped_case = self.scoped_pericia_case()
        if scoped_case is not None:
            return f"{scoped_case.case_reference} / scope pericial"
        if self.identity_scope == self.IDENTITY_SCOPE_GLOBAL:
            return "Global / sin scope pericial"
        return self.identity_scope

    def associated_evidence_items(self):
        primary_ids = list(self.case_evidence_items.values_list("pk", flat=True))
        linked_ids = list(self.linked_evidence_items.values_list("pk", flat=True))
        unique_ids = list(dict.fromkeys(primary_ids + linked_ids))
        return EvidenceItem.objects.filter(pk__in=unique_ids).select_related(
            "pericia_case"
        ).order_by("pericia_case__case_reference", "label", "id")

    def associated_pericia_cases(self):
        item_ids = list(self.associated_evidence_items().values_list("pericia_case_id", flat=True))
        unique_case_ids = list(dict.fromkeys(item_ids))
        scoped_case_id = self.scoped_pericia_case_id()
        if scoped_case_id is not None:
            unique_case_ids = list(dict.fromkeys([scoped_case_id, *unique_case_ids]))
        return PericiaCase.objects.filter(pk__in=unique_case_ids).order_by("case_reference")

    def homonymous_records(self):
        return (
            EvidenceFile.objects.filter(display_name=self.display_name)
            .exclude(pk=self.pk)
            .exclude(identity_scope=self.identity_scope, source_path=self.source_path)
            .order_by("display_name", "identity_scope", "source_path")
        )


class PericiaPoint(models.Model):
    class PointFamily(models.TextChoices):
        TEXT_EMAIL_SEARCH = "text_email_search", "Busqueda de correo en texto"
        TEXT_KEYWORD_SEARCH = "text_keyword_search", "Busqueda de palabras en texto"
        IMAGE_CHARACTERISTIC_DETECTION = (
            "image_characteristic_detection",
            "Deteccion de caracteristicas en imagen",
        )

    class MatchingMode(models.TextChoices):
        EXACT = "exact", "Exacto"
        DOMAIN = "domain", "Dominio"
        REGEX = "regex", "Regex"
        ANY = "any", "Cualquier termino"
        ALL = "all", "Todos los terminos"
        PHRASE = "phrase", "Frase"
        LABEL = "label", "Etiqueta"

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
        verbose_name = "punto de pericia"
        verbose_name_plural = "puntos de pericia"

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
        if self.matching_mode == self.MatchingMode.REGEX:
            value = self.parameters.get("pattern") or value
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
        pattern = str(self.parameters.get("pattern") or "").strip()
        has_terms = isinstance(terms, list) and any(str(term).strip() for term in terms)
        if self.matching_mode == self.MatchingMode.REGEX:
            if not pattern and not has_terms:
                errors.setdefault("parameters", []).append(
                    "Keyword regex points require 'pattern' or a non-empty 'terms' list."
                )
            return
        if not has_terms:
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


class PericiaCase(models.Model):
    class Status(models.TextChoices):
        INTAKE = "intake", "Ingreso"
        EVIDENCE_REGISTERED = "evidence_registered", "Evidencia registrada"
        ANALYSIS_IN_PROGRESS = "analysis_in_progress", "Analisis en curso"
        REPORT_IN_PROGRESS = "report_in_progress", "Informe en curso"
        COMPLETED = "completed", "Completado"
        BLOCKED = "blocked", "Bloqueado"

    case_reference = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    authority_name = models.CharField(max_length=255, blank=True)
    authority_unit = models.CharField(max_length=255, blank=True)
    jurisdiction = models.CharField(max_length=255, blank=True)
    report_date = models.DateField(blank=True, null=True)
    analyst_name = models.CharField(max_length=255, blank=True)
    analyst_badge = models.CharField(max_length=128, blank=True)
    summary = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.INTAKE,
    )
    metadata = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "caso pericial"
        verbose_name_plural = "casos periciales"

    def __str__(self) -> str:
        return self.case_reference

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ensure_standard_report_sections()
        if not getattr(self, "_skip_status_refresh", False):
            self.refresh_workflow_status()

    def ensure_standard_report_sections(self) -> None:
        if not self.pk:
            return

        existing_sections = list(self.report_sections.all())
        existing_by_type = {section.section_type: section for section in existing_sections}
        used_orders = {section.order for section in existing_sections}
        next_order = max(used_orders or {0}) + 1

        for definition in STANDARD_REPORT_SECTION_DEFINITIONS:
            section_type = str(definition["section_type"])
            title = str(definition["title"])
            structured_defaults = dict(definition.get("structured_data") or {})
            section = existing_by_type.get(section_type)
            if section is None:
                desired_order = int(definition["order"])
                order = desired_order if desired_order not in used_orders else next_order
                used_orders.add(order)
                next_order = max(next_order, order + 1)
                ReportSection.objects.create(
                    pericia_case=self,
                    section_type=section_type,
                    order=order,
                    title=title,
                    structured_data=structured_defaults,
                )
                continue

            updated_fields: list[str] = []
            if not str(section.title or "").strip():
                section.title = title
                updated_fields.append("title")
            current_structured = (
                dict(section.structured_data)
                if isinstance(section.structured_data, dict)
                else {}
            )
            merged_structured = dict(current_structured)
            for key, value in structured_defaults.items():
                merged_structured.setdefault(key, value)
            if merged_structured != current_structured:
                section.structured_data = merged_structured
                updated_fields.append("structured_data")
            if updated_fields:
                section.save(update_fields=updated_fields)

    def report_sections_ready_for_completion(self) -> bool:
        sections = list(self.report_sections.all())
        if not sections:
            return False
        types_with_content = {
            section.section_type
            for section in sections
            if str(section.title or "").strip()
            and report_section_has_substantive_content(section)
        }
        return REPORT_MINIMUM_SECTION_TYPES.issubset(types_with_content)

    def refresh_workflow_status(self) -> str:
        derived = self._derive_status()
        if self.status != derived:
            self.status = derived
            self._skip_status_refresh = True
            try:
                super().save(update_fields=["status"])
            finally:
                self._skip_status_refresh = False
        return self.status

    def _derive_status(self) -> str:
        point_statuses = set(self.requested_points.values_list("status", flat=True))
        response_statuses = set(
            self.requested_point_responses.values_list("status", flat=True)
        )
        evidence_registered = self.evidence_items.filter(
            Q(source_path__gt="")
            | Q(evidence_file__isnull=False)
            | Q(acquisition_status__in=[
                EvidenceItem.AcquisitionStatus.RECEIVED,
                EvidenceItem.AcquisitionStatus.ACQUIRED,
                EvidenceItem.AcquisitionStatus.PARTIAL,
                EvidenceItem.AcquisitionStatus.NOT_ACQUIRED,
                EvidenceItem.AcquisitionStatus.NOT_ACCESSIBLE,
            ])
        ).exists()

        if (
            RequestedPoint.Status.BLOCKED in point_statuses
            or RequestedPointResponse.Status.BLOCKED in response_statuses
        ):
            return self.Status.BLOCKED
        if self.report_sections_ready_for_completion():
            return self.Status.COMPLETED
        if self.requested_point_responses.exists():
            return self.Status.REPORT_IN_PROGRESS
        if self.analysis_plans.exists():
            return self.Status.ANALYSIS_IN_PROGRESS
        if evidence_registered:
            return self.Status.EVIDENCE_REGISTERED
        return self.Status.INTAKE


class PericiaDocument(models.Model):
    class DocumentType(models.TextChoices):
        JUDICIAL_REQUEST = "judicial_request", "Requerimiento judicial"
        TECHNICAL_REPORT = "technical_report", "Informe tecnico"
        ACTA_APERTURA = "acta_apertura", "Acta de apertura"
        ANNEX = "annex", "Anexo"
        OTHER = "other", "Otro"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices)
    file_path = models.CharField(max_length=1024, blank=True)
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "created_at", "id"]
        verbose_name = "documento pericial"
        verbose_name_plural = "documentos periciales"

    def __str__(self) -> str:
        return self.title


class RequestedPoint(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En curso"
        ANSWERED = "answered", "Respondido"
        PARTIALLY_ANSWERED = "partially_answered", "Respondido parcialmente"
        BLOCKED = "blocked", "Bloqueado"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="requested_points",
    )
    order = models.PositiveIntegerField()
    short_label = models.CharField(max_length=255, blank=True)
    literal_text = models.TextField()
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "order", "id"]
        verbose_name = "punto solicitado"
        verbose_name_plural = "puntos solicitados"
        constraints = [
            models.UniqueConstraint(
                fields=("pericia_case", "order"),
                name="unique_requested_point_order_per_case",
            )
        ]

    def __str__(self) -> str:
        return self.short_label or f"Punto {self.order}"

    def save(self, *args, **kwargs):
        metadata = self.metadata if isinstance(self.metadata, dict) else {}
        metadata["taxonomy_groups"] = self.derived_taxonomy_groups()
        self.metadata = metadata
        super().save(*args, **kwargs)
        if not getattr(self, "_skip_status_refresh", False):
            self.refresh_progress_status()
        self.pericia_case.refresh_workflow_status()

    def delete(self, *args, **kwargs):
        case = self.pericia_case
        super().delete(*args, **kwargs)
        case.refresh_workflow_status()

    def refresh_progress_status(self) -> str:
        derived = self._derive_status()
        if self.status != derived:
            self.status = derived
            self._skip_status_refresh = True
            try:
                super().save(update_fields=["status"])
            finally:
                self._skip_status_refresh = False
        return self.status

    def _derive_status(self) -> str:
        response = getattr(self, "responses", None)
        if response is not None:
            statuses = list(response.values_list("status", flat=True))
            if RequestedPointResponse.Status.BLOCKED in statuses:
                return self.Status.BLOCKED
            if RequestedPointResponse.Status.ANSWERED in statuses:
                return self.Status.ANSWERED
            if RequestedPointResponse.Status.PARTIALLY_ANSWERED in statuses:
                return self.Status.PARTIALLY_ANSWERED
            if RequestedPointResponse.Status.IN_PROGRESS in statuses:
                return self.Status.IN_PROGRESS
        if self.analysis_plans.exists():
            return self.Status.IN_PROGRESS
        return self.Status.PENDING

    def derived_taxonomy_groups(self) -> list[dict[str, object]]:
        source_text = " ".join(
            part for part in [self.short_label.strip(), self.literal_text.strip()] if part
        )
        return classify_requested_point_text(source_text)


class AnalysisPlan(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planificado"
        RUNNING = "running", "En ejecucion"
        COMPLETED = "completed", "Completado"
        SKIPPED = "skipped", "Omitido"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="analysis_plans",
    )
    requested_point = models.ForeignKey(
        RequestedPoint,
        on_delete=models.PROTECT,
        related_name="analysis_plans",
    )
    pericia_point = models.ForeignKey(
        PericiaPoint,
        on_delete=models.PROTECT,
        related_name="analysis_plans",
    )
    label = models.CharField(max_length=255, blank=True)
    strategy_notes = models.TextField(blank=True)
    analysis_targets = models.JSONField(default=default_list, blank=True)
    scope_snapshot = models.JSONField(default=default_dict, blank=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "requested_point__order", "id"]
        verbose_name = "plan de analisis"
        verbose_name_plural = "planes de analisis"

    def __str__(self) -> str:
        return self.label or f"Plan {self.pericia_case.case_reference}"

    def clean(self):
        errors: dict[str, list[str]] = {}
        if self.requested_point_id and self.pericia_case_id:
            if self.requested_point.pericia_case_id != self.pericia_case_id:
                errors.setdefault("requested_point", []).append(
                    "El punto solicitado debe pertenecer al mismo caso."
                )
        if not isinstance(self.analysis_targets, list):
            errors.setdefault("analysis_targets", []).append(
                "Analysis targets must be a JSON list."
            )
        if not isinstance(self.scope_snapshot, dict):
            errors.setdefault("scope_snapshot", []).append(
                "Scope snapshot must be a JSON object."
            )
        playbook = self.scope_snapshot.get("analysis_playbook")
        if playbook is not None:
            if not isinstance(playbook, dict):
                errors.setdefault("scope_snapshot", []).append(
                    "Analysis playbook must be a JSON object."
                )
            else:
                actions = playbook.get("actions", [])
                if not isinstance(actions, list):
                    errors.setdefault("scope_snapshot", []).append(
                        "Analysis playbook actions must be a JSON list."
                    )
                else:
                    for index, action in enumerate(actions, start=1):
                        if not isinstance(action, dict):
                            errors.setdefault("scope_snapshot", []).append(
                                f"Analysis playbook action #{index} must be a JSON object."
                            )
                            continue
                        if not str(action.get("label") or "").strip():
                            errors.setdefault("scope_snapshot", []).append(
                                f"Analysis playbook action #{index} requires a label."
                            )
                        if not isinstance(action.get("path_scope", []), list):
                            errors.setdefault("scope_snapshot", []).append(
                                f"Analysis playbook action #{index} requires a path_scope list."
                            )
                        if not isinstance(action.get("file_kinds", []), list):
                            errors.setdefault("scope_snapshot", []).append(
                                f"Analysis playbook action #{index} requires a file_kinds list."
                            )
                        search_criteria = action.get("search_criteria")
                        if not isinstance(search_criteria, dict):
                            errors.setdefault("scope_snapshot", []).append(
                                f"Analysis playbook action #{index} requires search_criteria."
                            )
                        elif not isinstance(search_criteria.get("terms", []), list):
                            errors.setdefault("scope_snapshot", []).append(
                                f"Analysis playbook action #{index} requires search_criteria.terms as a list."
                            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.scope_snapshot = self.build_scope_snapshot()
        self.full_clean()
        super().save(*args, **kwargs)
        self.requested_point.refresh_progress_status()
        self.pericia_case.refresh_workflow_status()

    def delete(self, *args, **kwargs):
        point = self.requested_point
        case = self.pericia_case
        super().delete(*args, **kwargs)
        point.refresh_progress_status()
        case.refresh_workflow_status()

    def build_scope_snapshot(self) -> dict:
        scope_snapshot = self.scope_snapshot if isinstance(self.scope_snapshot, dict) else {}
        search_terms = self.search_terms
        execution_actions = self.execution_actions
        taxonomy_groups = self.taxonomy_groups
        technique_label = build_technique_action_label(
            pericia_point_name=getattr(self.pericia_point, "name", ""),
            point_family=getattr(self.pericia_point, "point_family", ""),
        )

        if "search_terms" not in scope_snapshot or search_terms:
            scope_snapshot["search_terms"] = search_terms
        else:
            scope_snapshot.setdefault("search_terms", [])

        if execution_actions:
            scope_snapshot["execution_actions"] = execution_actions
        elif "execution_actions" not in scope_snapshot:
            scope_snapshot["execution_actions"] = build_suggested_playbook_actions(
                self.requested_point_text,
                pericia_point_name=getattr(self.pericia_point, "name", ""),
                point_family=getattr(self.pericia_point, "point_family", ""),
            )

        structured_actions = scope_snapshot.get("structured_actions")
        if isinstance(structured_actions, list):
            actions = normalize_structured_actions(
                structured_actions,
                pericia_point_id=self.pericia_point_id,
                pericia_point_name=getattr(self.pericia_point, "name", ""),
                point_family=getattr(self.pericia_point, "point_family", ""),
                analysis_targets=list(self.analysis_targets or []),
            )
        else:
            actions = build_structured_actions(
                self.requested_point_text,
                pericia_point_id=self.pericia_point_id,
                pericia_point_name=getattr(self.pericia_point, "name", ""),
                point_family=getattr(self.pericia_point, "point_family", ""),
                search_terms=search_terms,
                analysis_targets=list(self.analysis_targets or []),
                raw_actions=scope_snapshot.get("execution_actions", []),
            )
        scope_snapshot["structured_actions"] = actions

        scope_snapshot["analysis_playbook"] = {
            "requested_point_summary": str(self.requested_point),
            "requested_point_text": self.requested_point_text,
            "taxonomy_groups": taxonomy_groups,
            "actions": actions,
            "primary_technique": {
                "id": self.pericia_point_id,
                "name": getattr(self.pericia_point, "name", ""),
                "point_family": getattr(self.pericia_point, "point_family", ""),
                "action_label": technique_label,
            },
            "target_count": len(self.analysis_targets or []),
        }
        return scope_snapshot

    @property
    def requested_point_text(self) -> str:
        point = getattr(self, "requested_point", None)
        if point is None:
            return ""
        return " ".join(
            part
            for part in [
                str(getattr(point, "short_label", "") or "").strip(),
                str(getattr(point, "literal_text", "") or "").strip(),
            ]
            if part
        )

    @property
    def search_terms(self) -> list[str]:
        snapshot = self.scope_snapshot if isinstance(self.scope_snapshot, dict) else {}
        terms = snapshot.get("search_terms")
        if isinstance(terms, list):
            return [str(term).strip() for term in terms if str(term).strip()]

        parameters = (
            self.pericia_point.parameters
            if getattr(self.pericia_point, "parameters", None) and isinstance(self.pericia_point.parameters, dict)
            else {}
        )
        terms = parameters.get("terms")
        if isinstance(terms, list):
            return [str(term).strip() for term in terms if str(term).strip()]
        return []

    @property
    def taxonomy_groups(self) -> list[dict[str, object]]:
        point = getattr(self, "requested_point", None)
        if point is not None:
            groups = point.derived_taxonomy_groups()
            if groups:
                return groups
        return classify_requested_point_text(self.requested_point_text)

    @property
    def execution_actions(self) -> list[str]:
        snapshot = self.scope_snapshot if isinstance(self.scope_snapshot, dict) else {}
        actions = snapshot.get("execution_actions")
        if isinstance(actions, list):
            return [str(action).strip() for action in actions if str(action).strip()]
        return build_suggested_playbook_actions(
            self.requested_point_text,
            pericia_point_name=getattr(self.pericia_point, "name", ""),
            point_family=getattr(self.pericia_point, "point_family", ""),
        )

    @property
    def playbook_actions(self) -> list[dict[str, object]]:
        snapshot = self.scope_snapshot if isinstance(self.scope_snapshot, dict) else self.build_scope_snapshot()
        playbook = snapshot.get("analysis_playbook")
        if not isinstance(playbook, dict):
            return []
        actions = playbook.get("actions")
        if not isinstance(actions, list):
            return []
        return actions


class EvidenceItem(models.Model):
    class Role(models.TextChoices):
        ORIGINAL_DEVICE = "original_device", "Original device"
        FORENSIC_IMAGE = "forensic_image", "Forensic image"
        WORKING_COPY = "working_copy", "Working copy"
        LOGICAL_EXTRACTION = "logical_extraction", "Logical extraction"
        REPORT_OUTPUT = "report_output", "Report output"
        OTHER = "other", "Other"

    class AcquisitionStatus(models.TextChoices):
        RECEIVED = "received", "Received"
        IDENTIFIED = "identified", "Identified"
        ACQUIRED = "acquired", "Acquired"
        PARTIAL = "partial", "Partial"
        NOT_ACQUIRED = "not_acquired", "Not acquired"
        NOT_ACCESSIBLE = "not_accessible", "Not accessible"

    DEVICE_DESCRIPTION_METADATA_KEYS = (
        "device_class",
        "device_type",
        "device_interface",
        "device_brand",
        "device_model",
        "device_capacity_gb",
        "technical_notes",
    )

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="evidence_items",
    )
    parent_item = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="derived_items",
        null=True,
        blank=True,
    )
    evidence_file = models.ForeignKey(
        EvidenceFile,
        on_delete=models.PROTECT,
        related_name="case_evidence_items",
        null=True,
        blank=True,
    )
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=32, choices=Role.choices)
    acquisition_status = models.CharField(
        max_length=32,
        choices=AcquisitionStatus.choices,
        default=AcquisitionStatus.RECEIVED,
    )
    identifier = models.CharField(max_length=255, blank=True)
    serial_number = models.CharField(max_length=255, blank=True)
    source_path = models.CharField(max_length=1024, blank=True)
    sha256 = models.CharField(max_length=64, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    evidence_files = models.ManyToManyField(
        EvidenceFile,
        blank=True,
        related_name="linked_evidence_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "created_at", "id"]
        verbose_name = "elemento de evidencia"
        verbose_name_plural = "elementos de evidencia"

    def __str__(self) -> str:
        return self.label

    def clean(self):
        errors: dict[str, list[str]] = {}
        if (
            self.role == self.Role.WORKING_COPY
            and self.parent_item_id is None
        ):
            errors.setdefault("parent_item", []).append(
                "Las copias de trabajo deben vincularse a un elemento de evidencia de origen."
            )
        if self.parent_item_id and self.parent_item.pericia_case_id != self.pericia_case_id:
            errors.setdefault("parent_item", []).append(
                "El elemento padre debe pertenecer al mismo caso."
            )
        if self.evidence_file_id and self.evidence_file.source_path == "":
            errors.setdefault("evidence_file", []).append(
                "El archivo de evidencia principal debe ser valido."
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.pericia_case.refresh_workflow_status()

    def delete(self, *args, **kwargs):
        case = self.pericia_case
        super().delete(*args, **kwargs)
        case.refresh_workflow_status()

    def associated_evidence_files(self):
        ids: list[int] = []
        if self.evidence_file_id:
            ids.append(self.evidence_file_id)
        ids.extend(self.evidence_files.values_list("pk", flat=True))
        unique_ids = list(dict.fromkeys(ids))
        return EvidenceFile.objects.filter(pk__in=unique_ids).order_by("source_path")

    def primary_source_record(self):
        primary = self.sources.filter(role=EvidenceItemSource.Role.PRIMARY).first()
        if primary is not None:
            return primary
        return self.sources.order_by("position", "created_at", "id").first()

    def supporting_source_records(self):
        return self.sources.exclude(role=EvidenceItemSource.Role.PRIMARY).order_by(
            "position", "created_at", "id"
        )

    def known_source_paths(self) -> list[str]:
        paths: list[str] = []
        source_path = str(self.source_path or "").strip()
        if source_path:
            paths.append(source_path)
        if self.evidence_file_id and self.evidence_file.source_path:
            paths.append(str(self.evidence_file.source_path).strip())
        paths.extend(
            str(path).strip()
            for path in self.sources.values_list("source_path", flat=True)
            if str(path).strip()
        )
        return list(dict.fromkeys(paths))

    @property
    def offered_item_data(self) -> dict[str, str]:
        metadata = self.metadata if isinstance(self.metadata, dict) else {}
        return {
            "device_class": str(metadata.get("device_class") or "").strip(),
            "device_type": str(
                metadata.get("device_type")
                or metadata.get("tipo_dispositivo")
                or ""
            ).strip(),
            "device_interface": str(
                metadata.get("device_interface")
                or metadata.get("interfaz")
                or ""
            ).strip(),
            "device_brand": str(metadata.get("device_brand") or "").strip(),
            "device_model": str(metadata.get("device_model") or "").strip(),
            "serial_number": str(self.serial_number or "").strip(),
            "device_capacity_gb": str(
                metadata.get("device_capacity_gb")
                or metadata.get("capacity_gb")
                or ""
            ).strip(),
            "technical_notes": str(
                metadata.get("technical_notes")
                or metadata.get("observaciones_tecnicas")
                or ""
            ).strip(),
        }

    @property
    def offered_item_description(self) -> str:
        data = self.offered_item_data
        parts = ["Una (01)"]
        if data["device_class"]:
            parts.append(data["device_class"])
        if data["device_type"]:
            parts.append(f"tipo {data['device_type']}")
        if data["device_interface"]:
            parts.append(f"conexion {data['device_interface']}")
        if data["device_brand"]:
            parts.append(f"marca {data['device_brand']}")
        if data["device_model"]:
            parts.append(f"modelo {data['device_model']}")
        if data["serial_number"]:
            parts.append(f"numero de serie {data['serial_number']}")
        if data["device_capacity_gb"]:
            parts.append(f"de {data['device_capacity_gb']} GB de capacidad")
        description = ", ".join(
            part for part in parts if part and part != "Una (01)"
        )
        if description:
            return f"Una (01) {description}."
        if data["technical_notes"]:
            return data["technical_notes"]
        return "Una (01) unidad ofrecida sin descripcion tecnica completa."


class EvidenceItemSource(models.Model):
    class Role(models.TextChoices):
        PRIMARY = "primary", "Fuente principal"
        SUPPORTING = "supporting", "Fuente asociada"

    class SourceKind(models.TextChoices):
        FILE = "file", "Archivo"
        DIRECTORY = "directory", "Carpeta"

    evidence_item = models.ForeignKey(
        EvidenceItem,
        on_delete=models.CASCADE,
        related_name="sources",
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    source_kind = models.CharField(max_length=16, choices=SourceKind.choices)
    source_path = models.CharField(max_length=1024)
    position = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["evidence_item", "position", "created_at", "id"]
        verbose_name = "fuente de evidencia del dispositivo"
        verbose_name_plural = "fuentes de evidencia del dispositivo"
        constraints = [
            models.UniqueConstraint(
                fields=("evidence_item", "source_path"),
                name="unique_evidence_item_source_path",
            ),
            models.UniqueConstraint(
                fields=("evidence_item",),
                condition=Q(role="primary"),
                name="unique_primary_source_per_evidence_item",
            ),
        ]

    def __str__(self) -> str:
        return self.source_path


class DeviceAnalysisResult(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        ANALYZED = "analyzed", "Analizado"
        PARTIALLY_ANALYZED = "partially_analyzed", "Analizado parcialmente"
        NOT_ANALYZABLE = "not_analyzable", "No analizable"
        INACCESSIBLE = "inaccessible", "Inaccesible"
        FOLLOW_UP_REQUIRED = "follow_up_required", "Seguimiento requerido"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="device_analysis_results",
    )
    evidence_item = models.ForeignKey(
        EvidenceItem,
        on_delete=models.PROTECT,
        related_name="analysis_results",
    )
    overview = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    technical_reason = models.TextField(blank=True)
    follow_up_recommendation = models.TextField(blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["pericia_case", "started_at", "id"]
        verbose_name = "resultado de analisis por dispositivo"
        verbose_name_plural = "resultados de analisis por dispositivo"
        constraints = [
            models.UniqueConstraint(
                fields=("pericia_case", "evidence_item"),
                name="unique_device_analysis_per_case_evidence",
            )
        ]

    def __str__(self) -> str:
        return f"{self.pericia_case.case_reference} - {self.evidence_item.label}"

    def clean(self):
        errors: dict[str, list[str]] = {}
        if self.evidence_item_id and self.evidence_item.pericia_case_id != self.pericia_case_id:
            errors.setdefault("evidence_item", []).append(
                "El elemento de evidencia debe pertenecer al mismo caso."
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class PericiaExecution(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En ejecucion"
        COMPLETED = "completed", "Completada"
        FAILED = "failed", "Fallida"

    pericia_point = models.ForeignKey(
        PericiaPoint,
        on_delete=models.PROTECT,
        related_name="executions",
    )
    analysis_plan = models.ForeignKey(
        AnalysisPlan,
        on_delete=models.PROTECT,
        related_name="executions",
        null=True,
        blank=True,
    )
    device_analysis_result = models.ForeignKey(
        DeviceAnalysisResult,
        on_delete=models.PROTECT,
        related_name="executions",
        null=True,
        blank=True,
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
        verbose_name = "ejecucion de pericia"
        verbose_name_plural = "ejecuciones de pericia"

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
    device_analysis_result = models.ForeignKey(
        DeviceAnalysisResult,
        on_delete=models.SET_NULL,
        related_name="findings",
        null=True,
        blank=True,
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
        verbose_name = "hallazgo de pericia"
        verbose_name_plural = "hallazgos de pericia"

    def __str__(self) -> str:
        return f"{self.pericia_point.name}: {self.matched_value}"

    @property
    def line_fragment(self) -> dict:
        source_locator = self.source_locator if isinstance(self.source_locator, dict) else {}
        fragment = source_locator.get("line_fragment")
        if isinstance(fragment, dict):
            return fragment
        return {}

    @property
    def contextual_fragment(self) -> dict:
        fragment = self.line_fragment
        if fragment:
            return fragment
        context = str(self.context or "").strip()
        if not context:
            return {}
        return {
            "window": 0,
            "matched_line_number": None,
            "matched_line_index": 0,
            "lines": [
                {
                    "line_number": 1,
                    "text": line,
                    "is_match": index == 0,
                }
                for index, line in enumerate(context.splitlines() or [context])
            ],
        }


class PreservedArtifact(models.Model):
    class ArtifactKind(models.TextChoices):
        EXTRACTED_FILE = "extracted_file", "Archivo extraido"
        SCREENSHOT = "screenshot", "Captura"
        REPORT_SAMPLE = "report_sample", "Muestra para informe"
        REPORT_ATTACHMENT = "report_attachment", "Adjunto de informe"
        OTHER = "other", "Otro"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="preserved_artifacts",
    )
    evidence_item = models.ForeignKey(
        EvidenceItem,
        on_delete=models.PROTECT,
        related_name="preserved_artifacts",
    )
    source_finding = models.ForeignKey(
        PericiaFinding,
        on_delete=models.SET_NULL,
        related_name="preserved_artifacts",
        null=True,
        blank=True,
    )
    artifact_kind = models.CharField(max_length=32, choices=ArtifactKind.choices)
    display_name = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=1024)
    sha256 = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "created_at", "id"]
        verbose_name = "artefacto preservado"
        verbose_name_plural = "artefactos preservados"

    def __str__(self) -> str:
        return self.display_name

    def clean(self):
        errors: dict[str, list[str]] = {}
        if self.evidence_item_id and self.evidence_item.pericia_case_id != self.pericia_case_id:
            errors.setdefault("evidence_item", []).append(
                "El elemento de evidencia debe pertenecer al mismo caso."
            )
        if self.source_finding_id:
            associated_ids = set(
                self.evidence_item.associated_evidence_files().values_list("pk", flat=True)
            )
            if self.source_finding.evidence_file_id not in associated_ids:
                errors.setdefault("source_finding", []).append(
                    "El hallazgo de origen debe provenir de un archivo asociado al elemento de evidencia."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class RequestedPointResponse(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En curso"
        ANSWERED = "answered", "Respondida"
        PARTIALLY_ANSWERED = "partially_answered", "Respondida parcialmente"
        BLOCKED = "blocked", "Bloqueada"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="requested_point_responses",
    )
    requested_point = models.ForeignKey(
        RequestedPoint,
        on_delete=models.PROTECT,
        related_name="responses",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    summary = models.TextField(blank=True)
    technical_observations = models.TextField(blank=True)
    rationale = models.TextField(blank=True)
    metadata = models.JSONField(default=default_dict, blank=True)
    device_analysis_results = models.ManyToManyField(
        DeviceAnalysisResult,
        blank=True,
        related_name="requested_point_responses",
    )
    executions = models.ManyToManyField(
        PericiaExecution,
        blank=True,
        related_name="requested_point_responses",
    )
    findings = models.ManyToManyField(
        PericiaFinding,
        blank=True,
        related_name="requested_point_responses",
    )
    preserved_artifacts = models.ManyToManyField(
        PreservedArtifact,
        blank=True,
        related_name="requested_point_responses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "requested_point__order", "id"]
        verbose_name = "respuesta a punto solicitado"
        verbose_name_plural = "respuestas a puntos solicitados"
        constraints = [
            models.UniqueConstraint(
                fields=("pericia_case", "requested_point"),
                name="unique_response_per_case_requested_point",
            )
        ]

    def __str__(self) -> str:
        return f"{self.pericia_case.case_reference} - punto {self.requested_point.order}"

    def clean(self):
        errors: dict[str, list[str]] = {}
        if self.requested_point_id and self.requested_point.pericia_case_id != self.pericia_case_id:
            errors.setdefault("requested_point", []).append(
                "El punto solicitado debe pertenecer al mismo caso."
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.requested_point.refresh_progress_status()
        self.pericia_case.refresh_workflow_status()

    def delete(self, *args, **kwargs):
        point = self.requested_point
        case = self.pericia_case
        super().delete(*args, **kwargs)
        point.refresh_progress_status()
        case.refresh_workflow_status()


class ReportSection(models.Model):
    class SectionType(models.TextChoices):
        OBJECT = "object", "Objeto"
        OFFERED_ELEMENTS = "offered_elements", "Elementos ofrecidos"
        TOOLS = "tools", "Herramientas"
        METHODOLOGY = "methodology", "Metodologia"
        OBTAINED_INFORMATION = "obtained_information", "Informacion obtenida"
        CONCLUSIONS = "conclusions", "Conclusiones"
        EVIDENCE = "evidence", "Evidencia"
        ANNEX = "annex", "Anexo"

    pericia_case = models.ForeignKey(
        PericiaCase,
        on_delete=models.CASCADE,
        related_name="report_sections",
    )
    section_type = models.CharField(max_length=32, choices=SectionType.choices)
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    structured_data = models.JSONField(default=default_dict, blank=True)
    responses = models.ManyToManyField(
        RequestedPointResponse,
        blank=True,
        related_name="report_sections",
    )
    device_analysis_results = models.ManyToManyField(
        DeviceAnalysisResult,
        blank=True,
        related_name="report_sections",
    )
    preserved_artifacts = models.ManyToManyField(
        PreservedArtifact,
        blank=True,
        related_name="report_sections",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pericia_case", "order", "id"]
        verbose_name = "seccion del informe"
        verbose_name_plural = "secciones del informe"
        constraints = [
            models.UniqueConstraint(
                fields=("pericia_case", "order"),
                name="unique_report_section_order_per_case",
            )
        ]

    def __str__(self) -> str:
        return self.title

    def suggested_content(self) -> str:
        if self.section_type == self.SectionType.OFFERED_ELEMENTS:
            descriptions = [
                str(item.offered_item_description or "").strip()
                for item in self.pericia_case.evidence_items.order_by("created_at", "id")
                if str(item.offered_item_description or "").strip()
            ]
            return "\n".join(descriptions)

        if self.section_type == self.SectionType.OBTAINED_INFORMATION:
            lines: list[str] = []
            results = self.pericia_case.device_analysis_results.select_related(
                "evidence_item"
            ).order_by("evidence_item__label", "id")
            for result in results:
                overview = str(result.overview or "").strip()
                if not overview:
                    continue
                evidence_label = str(
                    getattr(getattr(result, "evidence_item", None), "label", "") or ""
                ).strip()
                if evidence_label:
                    lines.append(f"{evidence_label}: {overview}")
                else:
                    lines.append(overview)
            return "\n\n".join(lines)

        return ""

    def clean(self):
        if not isinstance(self.structured_data, dict):
            raise ValidationError(
                {"structured_data": ["Structured data must be a JSON object."]}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.pericia_case.refresh_workflow_status()

    def delete(self, *args, **kwargs):
        case = self.pericia_case
        super().delete(*args, **kwargs)
        case.refresh_workflow_status()
