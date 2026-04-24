from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
def test_ensure_admin_creates_configured_superuser(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "analyst")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "analyst@example.local")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "change-me")

    call_command("ensure_admin")

    user = get_user_model().objects.get(username="analyst")
    assert user.email == "analyst@example.local"
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password("change-me") is True


@pytest.mark.django_db
def test_ensure_admin_updates_existing_user(monkeypatch):
    User = get_user_model()
    User.objects.create_user(
        username="admin",
        email="old@example.local",
        password="old-password",
    )
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "new@example.local")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "new-password")

    call_command("ensure_admin")

    user = User.objects.get(username="admin")
    assert user.email == "new@example.local"
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password("new-password") is True


@pytest.mark.django_db
def test_ensure_admin_requires_password(monkeypatch):
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)

    with pytest.raises(CommandError, match="DJANGO_SUPERUSER_PASSWORD is required"):
        call_command("ensure_admin")
