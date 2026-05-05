from __future__ import annotations

import re

from .extractors import ExtractionResult, NormalizedImageContent, NormalizedTextContent
from .models import PericiaPoint

EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def match_pericia_point(
    pericia_point: PericiaPoint,
    extraction_result: ExtractionResult,
) -> list[dict]:
    if extraction_result.status != "supported":
        return []

    if pericia_point.point_family == PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH:
        return match_email_search(pericia_point, extraction_result.content)
    if pericia_point.point_family == PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH:
        return match_keyword_search(pericia_point, extraction_result.content)
    if (
        pericia_point.point_family
        == PericiaPoint.PointFamily.IMAGE_CHARACTERISTIC_DETECTION
    ):
        return match_image_characteristics(pericia_point, extraction_result.content)
    return []


def match_email_search(
    pericia_point: PericiaPoint,
    content: NormalizedTextContent | NormalizedImageContent | None,
) -> list[dict]:
    if not isinstance(content, NormalizedTextContent):
        return []

    findings: list[dict] = []
    target = str(pericia_point.parameters.get("value", "")).strip()
    text = content.text

    if pericia_point.matching_mode == PericiaPoint.MatchingMode.REGEX:
        pattern = re.compile(target, re.IGNORECASE)
        for match in pattern.finditer(text):
            findings.append(
                _text_finding(
                    match.group(0),
                    match.start(),
                    match.end(),
                    text,
                    content.metadata,
                )
            )
        return findings

    emails = list(EMAIL_PATTERN.finditer(text))
    normalized_target = target.lower().lstrip("@")
    for match in emails:
        value = match.group(0)
        email_value = value.lower()
        if (
            pericia_point.matching_mode == PericiaPoint.MatchingMode.EXACT
            and email_value == target.lower()
        ):
            findings.append(
                _text_finding(
                    value,
                    match.start(),
                    match.end(),
                    text,
                    content.metadata,
                )
            )
        elif (
            pericia_point.matching_mode == PericiaPoint.MatchingMode.DOMAIN
            and email_value.endswith(f"@{normalized_target}")
        ):
            findings.append(
                _text_finding(
                    value,
                    match.start(),
                    match.end(),
                    text,
                    content.metadata,
                )
            )
    return findings


def match_keyword_search(
    pericia_point: PericiaPoint,
    content: NormalizedTextContent | NormalizedImageContent | None,
) -> list[dict]:
    text_content, metadata = _keyword_search_payload(content)
    if text_content is None:
        return []

    findings: list[dict] = []
    text = text_content
    lower_text = text.lower()
    terms = [
        str(term).strip()
        for term in pericia_point.parameters.get("terms", [])
        if str(term).strip()
    ]

    if pericia_point.matching_mode == PericiaPoint.MatchingMode.REGEX:
        patterns = terms[:]
        explicit_pattern = str(pericia_point.parameters.get("pattern") or "").strip()
        if explicit_pattern:
            patterns.insert(0, explicit_pattern)
        for term in patterns:
            pattern = re.compile(term, re.IGNORECASE)
            for match in pattern.finditer(text):
                findings.append(
                    _text_finding(
                        match.group(0), match.start(), match.end(), text, metadata
                    )
                )
        return findings

    if pericia_point.matching_mode == PericiaPoint.MatchingMode.PHRASE:
        for term in terms:
            start = lower_text.find(term.lower())
            while start >= 0:
                end = start + len(term)
                findings.append(
                    _text_finding(text[start:end], start, end, text, metadata)
                )
                start = lower_text.find(term.lower(), end)
        return findings

    matched_terms = []
    for term in terms:
        positions = []
        start = lower_text.find(term.lower())
        while start >= 0:
            end = start + len(term)
            positions.append((start, end))
            if pericia_point.matching_mode == PericiaPoint.MatchingMode.ANY:
                findings.append(
                    _text_finding(text[start:end], start, end, text, metadata)
                )
            start = lower_text.find(term.lower(), end)
        if positions:
            matched_terms.append((term, positions))

    if pericia_point.matching_mode == PericiaPoint.MatchingMode.ALL and len(
        matched_terms
    ) == len(terms):
        for term, positions in matched_terms:
            for start, end in positions:
                findings.append(_text_finding(term, start, end, text, metadata))
    return findings


def match_image_characteristics(
    pericia_point: PericiaPoint,
    content: NormalizedTextContent | NormalizedImageContent | None,
) -> list[dict]:
    if not isinstance(content, NormalizedImageContent):
        return []

    findings: list[dict] = []
    targets = {
        str(label).strip().lower()
        for label in pericia_point.parameters.get("target_labels", [])
        if str(label).strip()
    }
    threshold = float(pericia_point.parameters.get("min_confidence", 0.0))

    for label in content.labels:
        label_name = str(label.get("label", "")).strip()
        confidence = float(label.get("confidence", 0.0))
        if label_name.lower() in targets and confidence >= threshold:
            findings.append(
                {
                    "matched_value": label_name,
                    "context": content.ocr_text[:240],
                    "confidence": confidence,
                    "source_locator": {
                        "label": label_name,
                        "threshold": threshold,
                    },
                    "extraction_metadata": content.metadata,
                    "engine_metadata": {"engine": "image-label-placeholder"},
                }
            )
    return findings


def _text_finding(
    matched_value: str,
    start: int,
    end: int,
    text: str,
    metadata: dict,
) -> dict:
    window_start = max(0, start - 60)
    window_end = min(len(text), end + 60)
    context = text[window_start:window_end].strip()
    return {
        "matched_value": matched_value,
        "context": context,
        "confidence": None,
        "source_locator": {"start": start, "end": end},
        "extraction_metadata": metadata,
        "engine_metadata": {"engine": "normalized-text-matcher"},
    }


def _keyword_search_payload(
    content: NormalizedTextContent | NormalizedImageContent | None,
) -> tuple[str | None, dict]:
    if isinstance(content, NormalizedTextContent):
        return content.text, content.metadata
    if isinstance(content, NormalizedImageContent):
        combined_text = "\n".join(
            [
                str(content.ocr_text or "").strip(),
                "\n".join(
                    str(label.get("label", "")).strip()
                    for label in content.labels
                    if str(label.get("label", "")).strip()
                ),
            ]
        ).strip()
        return combined_text or None, content.metadata
    return None, {}
