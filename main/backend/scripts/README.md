# Scripts del backend

Estos scripts preparan los datos que utiliza la app Django.

## 1. Puntuacion runner

Calcula distancia a rutas, rutas cercanas y `running_accessibility_score`:

```powershell
python main/backend/scripts/calculate_running_accessibility.py
```

Por defecto lee:

- `main/backend/data/barcelona_hotels_location.geojson`
- `main/backend/data/barcelona_routes_location.geojson`

Y actualiza:

- `main/backend/data/barcelona_hotels_location.geojson`

## 2. GeoJSON enriquecido

Combina localizacion, puntuacion, metadatos y valoraciones:

```powershell
python main/backend/scripts/build_enriched_hotels_geojson.py
```

Por defecto escribe:

- `main/backend/data/barcelona_hotels_enriched.geojson`