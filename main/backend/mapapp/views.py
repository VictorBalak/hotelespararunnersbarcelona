"""Vistas HTTP de la aplicacion principal del mapa."""

from __future__ import annotations

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .geojson_services import get_hotels_geojson, get_routes_geojson


@require_GET
def map_view(request):
    """Renderiza la pagina unica del prototipo."""

    return render(request, "mapapp/index.html")


@require_GET
def hotels_geojson(request):
    """Endpoint GeoJSON con los hoteles y los campos del panel lateral."""

    return JsonResponse(
        get_hotels_geojson(),
        json_dumps_params={"ensure_ascii": False},
    )


@require_GET
def routes_geojson(request):
    """Endpoint GeoJSON con las rutas de running preparadas para el mapa."""

    return JsonResponse(
        get_routes_geojson(),
        json_dumps_params={"ensure_ascii": False},
    )
