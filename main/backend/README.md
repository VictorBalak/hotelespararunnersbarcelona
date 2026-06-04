# Backend

Este directorio contiene la parte ejecutable del proyecto: configuracion Django, app del mapa, datos y scripts de preparacion. Las plantillas y estaticos estan en `../frontend/`.

## Carpetas principales

- `config/`: configuracion Django y rutas HTTP globales.
- `mapapp/`: app Django del mapa. Las vistas quedan en `views.py` y la lectura y procesado GeoJSON en `geojson_services.py`.
- `data/`: GeoJSONs y Excels.
- `scripts/`: tareas de preparacion de datos.

## Contrato de la app

La aplicacion consiste de una sola pagina y dos endpoints locales:

- `/`: pagina del mapa.
- `/api/hotels.geojson`: hoteles con puntuacion y otros campos.
- `/api/routes.geojson`: rutas de running.


