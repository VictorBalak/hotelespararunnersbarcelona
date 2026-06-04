from __future__ import annotations

from django.apps import AppConfig


class MapappConfig(AppConfig):
    """Configuracion de la app que sirve el mapa interactivo."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "mapapp"
