"""Rutas HTTP del prototipo Django del mapa de Barcelona."""

from __future__ import annotations

from django.urls import path

from mapapp import views


urlpatterns = [
    # La aplicacion expone una sola pagina y dos endpoints GeoJSON locales.
    path("", views.map_view, name="map"),
    path("api/hotels.geojson", views.hotels_geojson, name="hotels_geojson"),
    path("api/routes.geojson", views.routes_geojson, name="routes_geojson"),
]
