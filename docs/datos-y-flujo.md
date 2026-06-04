# Datos y flujo de trabajo

La app usa datos locales para mantener el primer prototipo sencillo y reproducible.

## Datasets

- `main/backend/data/barcelona_hotels_location.geojson`: hoteles con geometria `Point` y campos de accesibilidad runner.
- `main/backend/data/barcelona_routes_location.geojson`: rutas de running con geometria de linea.
- `main/backend/data/barcelona_hotels_list.xlsx`: metadatos de hoteles.
- `main/backend/data/barcelona_hotels_reviews.xlsx`: reviews y valoraciones de Booking.
- `main/backend/data/barcelona_hotels_enriched.geojson`: salida enriquecida que alimenta el panel lateral.

## Campos importantes de hoteles

- `name`: nombre visible.
- `booking`: enlace usado para abrir Booking y unir reviews.
- `running_accessibility_score`: puntuacion de 0 a 100 para colorear marcadores.
- `nearest_route_m`: distancia a la ruta mas cercana.
- `nearby_routes_count`: rutas dentro de 1000 metros.
- `hotel_rating`: nota de review.
- `hotel_rating_label`: etiqueta textual de la nota.
- `review_summary`: resumen de las reseñas.

## Orden recomendado

1. Recalcular accesibilidad runner:

```powershell
python main/backend/scripts/calculate_running_accessibility.py
```

2. Regenerar el GeoJSON enriquecido:

```powershell
python main/backend/scripts/build_enriched_hotels_geojson.py
```

## Reglas del prototipo

- El mapa muestra rutas por color y nombre en hover.
- Los detalles de hoteles se abren en panel lateral.
- La leyenda debe seguir los mismos rangos que `HOTEL_COLOR_EXPRESSION`.
- No se debe mostrar ningun campo `ABSA runner-friendly score` salvo peticion explicita.
