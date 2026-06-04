"""Servicios de lectura y preparacion de GeoJSON para la pagina del mapa.

Este modulo concentra el acceso a los datos locales para que las vistas Django
solo tengan que renderizar la pagina o devolver JSON. La aplicacion no consulta
APIs externas: lee los archivos preparados en ``main/backend/data``.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from django.http import Http404


DATA_DIR = Path(__file__).resolve().parents[1] / "data"

HOTELS_LOCATION_PATH = DATA_DIR / "barcelona_hotels_location.geojson"
HOTELS_ENRICHMENT_PATH = DATA_DIR / "barcelona_hotels_enriched.geojson"
ROUTES_GEOJSON_PATH = DATA_DIR / "barcelona_routes_location.geojson"

HOTEL_PANEL_ENRICHMENT_FIELDS = (
    "booking",
    "hotel_rating",
    "average_review_score",
    "review_count",
    "hotel_rating_label",
    "review_summary",
)


def load_feature_collection(path: Path) -> dict[str, Any]:
    """Carga un GeoJSON y valida que tenga formato ``FeatureCollection``."""

    if not path.exists():
        raise Http404(f"No existe el archivo GeoJSON: {path.name}")

    with path.open(encoding="utf-8-sig") as file:
        data = json.load(file)

    if data.get("type") != "FeatureCollection":
        raise Http404(f"Formato GeoJSON no soportado: {path.name}")

    return data


def feature_identity(feature: dict[str, Any]) -> str:
    """Obtiene una clave estable para unir datos de un mismo hotel."""

    properties = feature.get("properties") or {}
    return str(properties.get("@id") or properties.get("name") or "").strip()


def with_hotel_panel_enrichment(data: dict[str, Any]) -> dict[str, Any]:
    """Anade al GeoJSON base los campos que necesita el panel lateral."""

    hotels = copy.deepcopy(data)

    if not HOTELS_ENRICHMENT_PATH.exists():
        return hotels

    enrichment = load_feature_collection(HOTELS_ENRICHMENT_PATH)
    enrichment_by_key = {
        key: feature.get("properties") or {}
        for feature in enrichment.get("features", [])
        if (key := feature_identity(feature))
    }

    # Solo copiamos los campos del panel para mantener separado el contrato del
    # mapa base y el GeoJSON enriquecido.
    for feature in hotels.get("features", []):
        key = feature_identity(feature)
        properties = feature.setdefault("properties", {})
        enrichment_properties = enrichment_by_key.get(key, {})

        for field in HOTEL_PANEL_ENRICHMENT_FIELDS:
            if field in enrichment_properties and enrichment_properties[field] is not None:
                properties[field] = enrichment_properties[field]

    return hotels


def with_route_display_names(data: dict[str, Any]) -> dict[str, Any]:
    """Garantiza que cada ruta tenga un nombre visible para el tooltip."""

    enriched = copy.deepcopy(data)

    for index, feature in enumerate(enriched.get("features", []), start=1):
        properties = feature.setdefault("properties", {})
        explicit_name = properties.get("name") or properties.get("route_name")
        properties["display_name"] = explicit_name or f"Ruta de Barcelona {index}"

    return enriched


def get_hotels_geojson() -> dict[str, Any]:
    """Devuelve los hoteles listos para pintar en el mapa."""

    return with_hotel_panel_enrichment(load_feature_collection(HOTELS_LOCATION_PATH))


def get_routes_geojson() -> dict[str, Any]:
    """Devuelve las rutas con nombres preparados para interaccion de hover."""

    return with_route_display_names(load_feature_collection(ROUTES_GEOJSON_PATH))
