from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_EXPECTED_OUTPUTS = (
    "ruta completa",
    "archivo fuente",
    "contexto de coincidencia",
    "fechas y metadatos",
)


@dataclass(frozen=True)
class TaxonomyGroup:
    code: str
    label: str
    keywords: tuple[str, ...]
    default_actions: tuple[str, ...]


@dataclass(frozen=True)
class StructuredActionTemplate:
    label: str
    action_family: str
    path_scope: tuple[str, ...]
    file_kinds: tuple[str, ...]
    search_mode: str
    terms: tuple[str, ...]
    notes: str = ""
    expected_outputs: tuple[str, ...] = DEFAULT_EXPECTED_OUTPUTS


TAXONOMY_GROUPS: tuple[TaxonomyGroup, ...] = (
    TaxonomyGroup(
        code="threat_intrusion",
        label="Deteccion de amenazas e intrusion",
        keywords=("malware", "spyware", "troyano", "intrusion", "phishing", "mitm", "ataque"),
        default_actions=(
            "Revisar indicadores de malware e intrusion",
            "Correlacionar artefactos de ejecucion y persistencia",
            "Documentar vectores de ataque y trazas tecnicas",
        ),
    ),
    TaxonomyGroup(
        code="illicit_multimedia",
        label="Material ilicito o multimedia relevante",
        keywords=("pornografia", "masi", "ilicit", "imagen", "video", "audio", "multimedia"),
        default_actions=(
            "Buscar material multimedia relevante",
            "Clasificar archivos sensibles por tipo y ubicacion",
            "Preservar muestras representativas para informe",
        ),
    ),
    TaxonomyGroup(
        code="activity_timeline",
        label="Reconstruccion de actividad y cronologia",
        keywords=("acceso", "log", "actividad", "cronologia", "horario", "fecha", "impres"),
        default_actions=(
            "Reconstruir actividad reciente y cronologia",
            "Revisar logs, timestamps y sesiones",
            "Relacionar fechas, horarios y eventos relevantes",
        ),
    ),
    TaxonomyGroup(
        code="file_recovery_analysis",
        label="Recuperacion, extraccion y analisis de archivos",
        keywords=("archivo", "documentacion", "documento", "recuper", "elimin", "extraccion"),
        default_actions=(
            "Buscar archivos y documentos vinculados al punto",
            "Recuperar elementos eliminados si existen",
            "Analizar contenido y metadata de archivos relevantes",
        ),
    ),
    TaxonomyGroup(
        code="communications_social",
        label="Comunicacion, mensajeria y redes sociales",
        keywords=("whatsapp", "sms", "mensaje", "mensajeria", "llamada", "redes", "voip", "contacto"),
        default_actions=(
            "Revisar comunicaciones y mensajeria",
            "Extraer contactos, llamadas y actividad social",
            "Correlacionar mensajes con archivos y tiempos relevantes",
        ),
    ),
    TaxonomyGroup(
        code="credentials_access",
        label="Credenciales, cuentas y acceso",
        keywords=("credencial", "cuenta", "correo", "autocompletado", "usuario", "perfil", "desbloqueo", "remoto"),
        default_actions=(
            "Buscar correos, cuentas y credenciales almacenadas",
            "Identificar usuarios, perfiles y formularios de autocompletado",
            "Revisar accesos remotos y mecanismos de autenticacion",
        ),
    ),
    TaxonomyGroup(
        code="programs_anonymization",
        label="Programas, artefactos de ejecucion y anonimización",
        keywords=("programa", "instalado", "ejecutado", "anonimiz", "p2p", "software"),
        default_actions=(
            "Inventariar programas instalados y ejecutados",
            "Identificar herramientas P2P, remotas o de anonimización",
            "Relacionar software detectado con actividad del caso",
        ),
    ),
    TaxonomyGroup(
        code="fraud_financial",
        label="Transferencia, fraude y trazas economicas",
        keywords=("transferencia", "wallet", "billetera", "cbu", "cuenta destino", "fraude", "geolocalizacion", "ip"),
        default_actions=(
            "Rastrear transferencias, billeteras y cuentas destino",
            "Extraer IPs, CBU, geolocalizacion y trazas economicas",
            "Consolidar evidencia vinculada a fraude y movimientos",
        ),
    ),
    TaxonomyGroup(
        code="other_relevant",
        label="Hallazgos relevantes adicionales",
        keywords=("otro dato", "relevante", "hallazgo"),
        default_actions=(
            "Registrar hallazgos relevantes no previstos",
            "Consolidar observaciones tecnicas complementarias",
        ),
    ),
)

TAXONOMY_GROUP_MAP = {group.code: group for group in TAXONOMY_GROUPS}

CATALOG_ENTRIES: tuple[dict[str, object], ...] = (
    {
        "code": "01",
        "title": "Detección de malware (troyanos, spyware, etc.) y análisis de intrusión.",
        "groups": ("threat_intrusion",),
        "keywords": ("malware", "spyware", "troyanos", "intrusion"),
    },
    {
        "code": "02",
        "title": "Detección de material ilícito (incluyendo pornografía infantil o M.A.S.I.).",
        "groups": ("illicit_multimedia",),
        "keywords": ("material ilicito", "pornografia", "masi"),
    },
    {
        "code": "03",
        "title": "Detección de material multimedia relevante (imágenes, videos, audios) vinculado a la investigación.",
        "groups": ("illicit_multimedia",),
        "keywords": ("material multimedia", "imagenes", "videos", "audios"),
    },
    {
        "code": "04",
        "title": "Determinación de accesos y logs de cuentas (IP, fechas, horarios).",
        "groups": ("activity_timeline", "credentials_access"),
        "keywords": ("accesos", "logs", "cuentas", "horarios"),
    },
    {
        "code": "05",
        "title": "Determinación de actividad reciente y última actividad registrada.",
        "groups": ("activity_timeline",),
        "keywords": ("actividad reciente", "ultima actividad"),
    },
    {
        "code": "06",
        "title": "Determinación de eliminación de archivos y recuperación de los mismos.",
        "groups": ("file_recovery_analysis",),
        "keywords": ("eliminacion", "recuperacion"),
    },
    {
        "code": "07",
        "title": "Determinación de existencia de aplicaciones de mensajería y uso para distribución de material.",
        "groups": ("communications_social",),
        "keywords": ("mensajeria", "distribucion de material"),
    },
    {
        "code": "08",
        "title": "Determinación de existencia de software para desbloqueo de dispositivos.",
        "groups": ("credentials_access",),
        "keywords": ("desbloqueo", "software"),
    },
    {
        "code": "09",
        "title": "Determinación de fechas de impresiones realizadas.",
        "groups": ("activity_timeline",),
        "keywords": ("impresiones",),
    },
    {
        "code": "10",
        "title": "Determinación de programas instalados y ejecutados, incluyendo herramientas de anonimización.",
        "groups": ("programs_anonymization",),
        "keywords": ("programas instalados", "anonimizacion"),
    },
    {
        "code": "11",
        "title": "Determinación de transferencia de archivos (P2P, descargas directas, chat, correo).",
        "groups": ("fraud_financial", "communications_social", "programs_anonymization"),
        "keywords": ("transferencia de archivos", "descargas", "chat", "correo", "p2p"),
    },
    {
        "code": "12",
        "title": "Determinación de uso de billeteras virtuales.",
        "groups": ("fraud_financial",),
        "keywords": ("billeteras virtuales", "wallet"),
    },
    {
        "code": "13",
        "title": "Determinación de uso de software de acceso remoto.",
        "groups": ("credentials_access", "programs_anonymization"),
        "keywords": ("acceso remoto",),
    },
    {
        "code": "14",
        "title": "Determinación de vectores de ataque (phishing, MITM, malware).",
        "groups": ("threat_intrusion",),
        "keywords": ("vectores de ataque", "phishing", "mitm"),
    },
    {
        "code": "15",
        "title": "Extracción de información específica (CBU, cuentas destino, IPs, geolocalización).",
        "groups": ("fraud_financial",),
        "keywords": ("cbu", "cuentas destino", "ips", "geolocalizacion"),
    },
    {
        "code": "16",
        "title": "Extracción y análisis integral de archivos (incluyendo eliminados).",
        "groups": ("file_recovery_analysis",),
        "keywords": ("analisis integral de archivos", "incluyendo eliminados"),
    },
    {
        "code": "17",
        "title": "Identificación de archivos o documentación específica vinculada a personas o entidades.",
        "groups": ("file_recovery_analysis",),
        "keywords": ("documentacion especifica", "personas", "entidades"),
    },
    {
        "code": "18",
        "title": "Identificación de contactos, llamadas, mensajes y actividad en redes sociales.",
        "groups": ("communications_social",),
        "keywords": ("contactos", "llamadas", "mensajes", "redes sociales"),
    },
    {
        "code": "19",
        "title": "Identificación de correos electrónicos, credenciales almacenadas y formularios de autocompletado.",
        "groups": ("credentials_access",),
        "keywords": ("correos electronicos", "credenciales", "autocompletado"),
    },
    {
        "code": "20",
        "title": "Identificación de documentación de terceros utilizada en posibles fraudes.",
        "groups": ("fraud_financial", "file_recovery_analysis"),
        "keywords": ("documentacion de terceros", "fraudes"),
    },
    {
        "code": "21",
        "title": "Identificación de programas P2P instalados.",
        "groups": ("programs_anonymization",),
        "keywords": ("programas p2p",),
    },
    {
        "code": "22",
        "title": "Identificación de usuarios de los dispositivos y perfiles de uso.",
        "groups": ("credentials_access",),
        "keywords": ("usuarios de los dispositivos", "perfiles de uso"),
    },
    {
        "code": "23",
        "title": "Obtención de cualquier otro dato relevante para la investigación.",
        "groups": ("other_relevant",),
        "keywords": ("otro dato relevante",),
    },
    {
        "code": "24",
        "title": "Recuperación de comunicaciones (SMS, WhatsApp, redes sociales, VoIP).",
        "groups": ("communications_social", "illicit_multimedia"),
        "keywords": ("sms", "whatsapp", "redes sociales", "voip", "comunicaciones"),
    },
    {
        "code": "25",
        "title": "Recuperación de evidencia vinculada a fraudes (capturas, transferencias, logs).",
        "groups": ("fraud_financial", "activity_timeline"),
        "keywords": ("fraudes", "capturas", "transferencias", "logs"),
    },
)

CATALOG_ACTION_TEMPLATES: dict[str, tuple[StructuredActionTemplate, ...]] = {
    "21": (
        StructuredActionTemplate(
            label="Buscar indicadores de software P2P en ActividadReciente",
            action_family="keyword_search",
            path_scope=("ActividadReciente",),
            file_kinds=("html",),
            search_mode="any",
            terms=("torrent", "emule", "p2p", "utorrent", "bittorrent", "ares"),
            notes="Revisar actividad reciente y referencias a software P2P instalado o utilizado.",
        ),
    ),
    "19": (
        StructuredActionTemplate(
            label="Buscar cuentas y credenciales en CuentaGmail",
            action_family="keyword_search",
            path_scope=("CuentaGmail",),
            file_kinds=("html", "text", "json"),
            search_mode="any",
            terms=("@gmail.com", "@hotmail.com", "correo", "email", "login", "password"),
            notes="Priorizar cuentas, credenciales almacenadas y formularios de autocompletado.",
        ),
    ),
    "16": (
        StructuredActionTemplate(
            label="Analizar documentos de ArchivosOfimatica",
            action_family="keyword_search",
            path_scope=("ArchivosOfimatica",),
            file_kinds=("doc", "docx", "text"),
            search_mode="any",
            terms=(),
            notes="Cruzar palabras clave del punto con nombres, contenido y metadata documental.",
        ),
        StructuredActionTemplate(
            label="Analizar PDFs de ArchivosPDF",
            action_family="keyword_search",
            path_scope=("ArchivosPDF",),
            file_kinds=("pdf", "text"),
            search_mode="any",
            terms=(),
            notes="Extraer contenido y metadata relevante de archivos PDF.",
        ),
    ),
    "24": (
        StructuredActionTemplate(
            label="Buscar comunicaciones en Usuarios",
            action_family="keyword_search",
            path_scope=("Usuarios",),
            file_kinds=("html", "text", "json"),
            search_mode="any",
            terms=("whatsapp", "sms", "mensaje", "chat", "telegram", "voip"),
            notes="Detectar conversaciones, historiales y artefactos de mensajeria.",
        ),
        StructuredActionTemplate(
            label="Buscar rastros de comunicaciones en ActividadReciente",
            action_family="keyword_search",
            path_scope=("ActividadReciente",),
            file_kinds=("html", "text", "json"),
            search_mode="any",
            terms=("whatsapp", "sms", "mensaje", "chat", "telegram", "voip"),
            notes="Correlacionar accesos recientes a servicios de mensajeria.",
        ),
    ),
    "03": (
        StructuredActionTemplate(
            label="Inventariar multimedia relevante en Imagenes",
            action_family="image_detection",
            path_scope=("Imagenes",),
            file_kinds=("image",),
            search_mode="label",
            terms=("imagen", "captura", "foto"),
            notes="Inventariar imagenes relevantes para la investigacion.",
        ),
        StructuredActionTemplate(
            label="Inventariar multimedia relevante en ImagenesVideos",
            action_family="image_detection",
            path_scope=("ImagenesVideos",),
            file_kinds=("image", "video"),
            search_mode="label",
            terms=("video", "captura", "multimedia"),
            notes="Priorizar evidencia audiovisual y nombres/etiquetas de archivo.",
        ),
    ),
    "06": (
        StructuredActionTemplate(
            label="Revisar PapeleraReciclaje por archivos eliminados relevantes",
            action_family="inventory_search",
            path_scope=("PapeleraReciclaje",),
            file_kinds=("*",),
            search_mode="any",
            terms=(),
            notes="Inventariar archivos eliminados y aplicar palabras clave del punto.",
        ),
    ),
}


def _normalize_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9áéíóúñü@._-]+", str(text).lower()))


def classify_requested_point_text(text: str) -> list[dict[str, object]]:
    normalized = _normalize_text(text)
    if not normalized:
        return []

    matched_codes: list[str] = []
    catalog_codes: list[str] = []

    for entry in CATALOG_ENTRIES:
        title = _normalize_text(str(entry["title"]))
        keywords = [_normalize_text(keyword) for keyword in entry.get("keywords", ())]
        if title and title in normalized or any(keyword and keyword in normalized for keyword in keywords):
            catalog_codes.append(str(entry["code"]))
            for code in entry["groups"]:
                if str(code) not in matched_codes:
                    matched_codes.append(str(code))

    if not matched_codes:
        for group in TAXONOMY_GROUPS:
            normalized_keywords = [_normalize_text(keyword) for keyword in group.keywords]
            if any(keyword and keyword in normalized for keyword in normalized_keywords):
                matched_codes.append(group.code)

    if not matched_codes:
        matched_codes.append("other_relevant")

    results = []
    for code in matched_codes:
        group = TAXONOMY_GROUP_MAP.get(code)
        if group is None:
            continue
        results.append(
            {
                "code": group.code,
                "label": group.label,
                "catalog_points": [item for item in catalog_codes],
            }
        )
    return results


def _catalog_codes_for_text(text: str) -> list[str]:
    normalized = _normalize_text(text)
    codes: list[str] = []
    if not normalized:
        return codes
    for entry in CATALOG_ENTRIES:
        title = _normalize_text(str(entry["title"]))
        keywords = [_normalize_text(keyword) for keyword in entry.get("keywords", ())]
        if title and title in normalized or any(keyword and keyword in normalized for keyword in keywords):
            codes.append(str(entry["code"]))
    return codes


def build_suggested_playbook_actions(
    requested_point_text: str,
    *,
    pericia_point_name: str = "",
    point_family: str = "",
) -> list[str]:
    actions: list[str] = []
    seen: set[str] = set()

    for template in _structured_action_templates_for_text(requested_point_text):
        key = template.label.lower()
        if key in seen:
            continue
        seen.add(key)
        actions.append(template.label)

    for group in classify_requested_point_text(requested_point_text):
        group_definition = TAXONOMY_GROUP_MAP.get(str(group["code"]))
        if group_definition is None:
            continue
        for action in group_definition.default_actions:
            key = action.lower()
            if key in seen:
                continue
            seen.add(key)
            actions.append(action)

    technique_action = build_technique_action_label(
        pericia_point_name=pericia_point_name,
        point_family=point_family,
    )
    if technique_action:
        key = technique_action.lower()
        if key not in seen:
            actions.insert(0, technique_action)

    return actions


def build_technique_action_label(*, pericia_point_name: str = "", point_family: str = "") -> str:
    name = str(pericia_point_name or "").strip()
    if name:
        return f"Ejecutar tecnica reusable: {name}"

    point_family = str(point_family or "").strip()
    family_map = {
        "text_email_search": "Ejecutar busqueda de correos en texto",
        "text_keyword_search": "Ejecutar busqueda de palabras clave",
        "image_characteristic_detection": "Ejecutar deteccion de caracteristicas en imagen",
    }
    return family_map.get(point_family, "")


def build_structured_actions(
    requested_point_text: str,
    *,
    pericia_point_id: int | None = None,
    pericia_point_name: str = "",
    point_family: str = "",
    search_terms: list[str] | None = None,
    analysis_targets: list[str] | None = None,
    raw_actions: list[str] | None = None,
) -> list[dict[str, object]]:
    search_terms = [str(term).strip() for term in (search_terms or []) if str(term).strip()]
    analysis_targets = [str(target).strip() for target in (analysis_targets or []) if str(target).strip()]
    templates = _structured_action_templates_for_text(requested_point_text)
    actions: list[dict[str, object]] = []

    if templates:
        for index, template in enumerate(templates, start=1):
            terms = list(template.terms) or list(search_terms)
            actions.append(
                {
                    "order": index,
                    "label": template.label,
                    "action_family": template.action_family,
                    "path_scope": list(template.path_scope),
                    "file_kinds": list(template.file_kinds),
                    "search_criteria": {
                        "mode": template.search_mode,
                        "terms": terms,
                    },
                    "expected_outputs": list(template.expected_outputs),
                    "notes": template.notes,
                    "pericia_point_id": pericia_point_id,
                    "pericia_point_name": pericia_point_name,
                    "point_family": point_family,
                    "targets": list(analysis_targets),
                }
            )

    if not actions:
        raw_actions = [str(action).strip() for action in (raw_actions or []) if str(action).strip()]
        if not raw_actions:
            suggested = build_suggested_playbook_actions(
                requested_point_text,
                pericia_point_name=pericia_point_name,
                point_family=point_family,
            )
            raw_actions = suggested or [build_technique_action_label(pericia_point_name=pericia_point_name, point_family=point_family) or "Ejecutar analisis relevante"]

        for index, action_label in enumerate(raw_actions, start=1):
            actions.append(
                {
                    "order": index,
                    "label": action_label,
                    "action_family": _infer_action_family_from_family(point_family),
                    "path_scope": ["*"],
                    "file_kinds": ["*"],
                    "search_criteria": {
                        "mode": _infer_search_mode(point_family),
                        "terms": list(search_terms),
                    },
                    "expected_outputs": list(DEFAULT_EXPECTED_OUTPUTS),
                    "notes": "",
                    "pericia_point_id": pericia_point_id,
                    "pericia_point_name": pericia_point_name,
                    "point_family": point_family,
                    "targets": list(analysis_targets),
                }
            )

    return actions


def normalize_structured_actions(
    actions: list[dict[str, object]] | tuple[dict[str, object], ...],
    *,
    pericia_point_id: int | None = None,
    pericia_point_name: str = "",
    point_family: str = "",
    analysis_targets: list[str] | None = None,
) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    analysis_targets = [str(target).strip() for target in (analysis_targets or []) if str(target).strip()]
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            continue
        label = str(action.get("label") or "").strip()
        if not label:
            continue
        search_criteria = action.get("search_criteria")
        if not isinstance(search_criteria, dict):
            search_criteria = {}
        normalized.append(
            {
                "order": int(action.get("order") or index),
                "label": label,
                "action_family": str(action.get("action_family") or _infer_action_family_from_family(point_family)),
                "path_scope": [str(value).strip() for value in action.get("path_scope", []) if str(value).strip()] or ["*"],
                "file_kinds": [str(value).strip() for value in action.get("file_kinds", []) if str(value).strip()] or ["*"],
                "search_criteria": {
                    "mode": str(search_criteria.get("mode") or _infer_search_mode(point_family)),
                    "terms": [str(value).strip() for value in search_criteria.get("terms", []) if str(value).strip()],
                },
                "expected_outputs": [
                    str(value).strip() for value in action.get("expected_outputs", []) if str(value).strip()
                ] or list(DEFAULT_EXPECTED_OUTPUTS),
                "notes": str(action.get("notes") or "").strip(),
                "pericia_point_id": action.get("pericia_point_id") or pericia_point_id,
                "pericia_point_name": str(action.get("pericia_point_name") or pericia_point_name),
                "point_family": str(action.get("point_family") or point_family),
                "targets": [str(value).strip() for value in action.get("targets", []) if str(value).strip()] or list(analysis_targets),
            }
        )
    return normalized


def _structured_action_templates_for_text(text: str) -> list[StructuredActionTemplate]:
    templates: list[StructuredActionTemplate] = []
    for code in _catalog_codes_for_text(text):
        templates.extend(CATALOG_ACTION_TEMPLATES.get(code, ()))
    return templates


def _infer_action_family_from_family(point_family: str) -> str:
    mapping = {
        "text_email_search": "email_search",
        "text_keyword_search": "keyword_search",
        "image_characteristic_detection": "image_detection",
    }
    return mapping.get(str(point_family or "").strip(), "generic_search")


def _infer_search_mode(point_family: str) -> str:
    family = str(point_family or "").strip()
    if family == "image_characteristic_detection":
        return "label"
    if family == "text_email_search":
        return "exact"
    return "any"
