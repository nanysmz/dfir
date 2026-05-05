from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from dfir_pericia.workflow import build_dashboard_workflow_context


def dashboard_callback(request, context):
    tone_map = {
        "ready": {
            "badge": _("Listo"),
            "badge_class": "bg-primary-600 text-white dark:bg-primary-500 dark:text-white",
            "card_class": "border-primary-300 bg-white shadow-sm dark:border-primary-700 dark:bg-base-900",
            "panel_class": "border-primary-200 bg-primary-50 dark:border-primary-900 dark:bg-primary-950/40",
            "cta_variant": "primary",
        },
        "in_progress": {
            "badge": _("En curso"),
            "badge_class": "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-200",
            "card_class": "border-orange-300 bg-white shadow-sm dark:border-orange-800 dark:bg-base-900",
            "panel_class": "border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950/40",
            "cta_variant": "primary",
        },
        "blocked": {
            "badge": _("Bloqueado"),
            "badge_class": "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-200",
            "card_class": "border-red-200 bg-white dark:border-red-900 dark:bg-base-900",
            "panel_class": "border-red-200 bg-red-50 dark:border-red-950 dark:bg-red-950/30",
            "cta_variant": "secondary",
        },
        "completed": {
            "badge": _("Completado"),
            "badge_class": "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200",
            "card_class": "border-emerald-200 bg-white/90 dark:border-emerald-900 dark:bg-base-900/80",
            "panel_class": "border-emerald-200 bg-emerald-50 dark:border-emerald-950 dark:bg-emerald-950/30",
            "cta_variant": "secondary",
        },
        "upcoming": {
            "badge": _("Siguiente"),
            "badge_class": "bg-base-200 text-base-700 dark:bg-base-800 dark:text-base-200",
            "card_class": "border-base-200 bg-white dark:border-base-800 dark:bg-base-900",
            "panel_class": "border-base-200 bg-base-50 dark:border-base-800 dark:bg-base-950/40",
            "cta_variant": "secondary",
        },
    }
    context.update(
        {
            "workflow_checklist": [
                _("Crear primero el caso pericial y guardarlo."),
                _("Cargar luego los documentos y puntos solicitados del caso."),
                _(
                    "Antes de crear un plan de analisis, debe existir al menos "
                    "un punto de pericia reusable en el catalogo."
                ),
                _(
                    "Los resultados por dispositivo y las respuestas por punto "
                    "pueden completarse de manera parcial mas adelante."
                ),
            ],
        }
    )
    context.update(build_dashboard_workflow_context())
    for card in context["workflow_stage_cards"]:
        card.update(tone_map[card["state"]])
    return context


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
