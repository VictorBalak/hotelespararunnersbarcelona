# Estructura del proyecto

El proyecto esta organizado alrededor de una app Django sencilla. La primera pantalla es el mapa; el codigo ejecutable vive en `main/backend/` y los assets web viven en `main/frontend/`.

## Raiz

- `README.md`: guia global del proyecto.
- `docs/`: documentacion estable en español.
- `main/`: aplicacion principal, separada en backend y frontend.
- `main/backend/`: aplicacion Django y flujo de datos.
- `main/frontend/`: plantillas HTML y archivos estaticos del mapa.

## Backend

- `main/backend/config/settings.py`: configuracion local de Django.
- `main/backend/config/urls.py`: rutas HTTP principales.
- `main/backend/manage.py`: entrada de comandos Django.
- `main/backend/mapapp/views.py`: vistas HTTP finas.
- `main/backend/mapapp/geojson_services.py`: lectura, validacion y enriquecimiento GeoJSON.
- `main/frontend/templates/mapapp/index.html`: estructura HTML del mapa, panel lateral y leyenda.
- `main/frontend/static/mapapp/css/map.css`: estilos del mapa y del panel.
- `main/frontend/static/mapapp/js/map.js`: punto de entrada del mapa.
- `main/frontend/static/mapapp/js/map/`: modulos JS separados por responsabilidad.

## Modulos JavaScript

- `config.js`: colores, limites de puntuacion y parametros del mapa.
- `style.js`: estilo base de MapLibre y teselas externas.
- `geojson.js`: carga de GeoJSON, bounds y helpers de colecciones.
- `layers.js`: capas de rutas, hoteles y hotel seleccionado.
- `panel.js`: apertura/cierre del panel lateral y relleno de datos.
- `legend.js`: leyenda sincronizada con los rangos de puntuacion.
- `animations.js`: animacion inicial de rutas y hoteles.
- `formatters.js`: formateo de puntuaciones, distancias, reviews y coordenadas.
- `dom.js`: mensajes de error del mapa.

## Flujo de datos

Los datos se preparan en `main/backend/data/`, pasan por los scripts de `main/backend/scripts/` y se exponen en la app con endpoints GeoJSON locales. La vista HTML no lee Excel directamente.
