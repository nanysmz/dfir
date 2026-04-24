from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from dfir_pericia.models import PericiaPoint


@pytest.mark.django_db
def test_pericia_point_validates_email_search_configuration():
    point = PericiaPoint(
        name="Buscar correo exacto",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
        scope={"file_kinds": ["text", "html"]},
    )

    point.save()

    assert point.slug == "buscar-correo-exacto"


@pytest.mark.django_db
def test_pericia_point_rejects_keyword_search_without_terms():
    point = PericiaPoint(
        name="Palabras clave vacias",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": []},
    )

    with pytest.raises(ValidationError, match="non-empty 'terms' list"):
        point.full_clean()


@pytest.mark.django_db
def test_pericia_point_validates_image_detection_threshold():
    point = PericiaPoint(
        name="Imagenes con personas",
        point_family=PericiaPoint.PointFamily.IMAGE_CHARACTERISTIC_DETECTION,
        matching_mode=PericiaPoint.MatchingMode.LABEL,
        parameters={"target_labels": ["person"], "min_confidence": 0.8},
    )

    point.full_clean()
