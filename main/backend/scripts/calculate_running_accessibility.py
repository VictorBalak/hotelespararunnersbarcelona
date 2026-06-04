"""Calcula puntuaciones de accesibilidad runner para hoteles de Barcelona.

El script lee puntos de hoteles y lineas de rutas, reproyecta ambos datasets a
EPSG:25831 para calcular distancias en metros y escribe el GeoJSON de hoteles
puntuado de nuevo en EPSG:4326 para que el mapa web pueda consumirlo.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"

DEFAULT_HOTELS_PATH = DATA_DIR / "barcelona_hotels_location.geojson"
DEFAULT_ROUTES_PATH = DATA_DIR / "barcelona_routes_location.geojson"
DEFAULT_OUTPUT_PATH = DEFAULT_HOTELS_PATH

SOURCE_CRS = "EPSG:4326"
METRIC_CRS = "EPSG:25831"
DEFAULT_DISTANCE_THRESHOLD_M = 1000.0
DEFAULT_TOTAL_ROUTES = 4

ROUTE_ID_COLUMNS = ("route_id", "route", "route_name", "name", "id")
SCORED_FIELDS = (
    "nearest_route_m",
    "nearby_routes_count",
    "closeness_score",
    "variety_score",
    "running_accessibility_score",
    "running_category",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate Running Accessibility Score for Barcelona hotels."
    )
    parser.add_argument(
        "--hotels",
        type=Path,
        default=DEFAULT_HOTELS_PATH,
        help=f"Hotel point GeoJSON path. Default: {DEFAULT_HOTELS_PATH}",
    )
    parser.add_argument(
        "--routes",
        type=Path,
        default=DEFAULT_ROUTES_PATH,
        help=f"Running route GeoJSON path. Default: {DEFAULT_ROUTES_PATH}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=(
            "Output scored hotel GeoJSON path. "
            f"Default overwrites the hotel file: {DEFAULT_OUTPUT_PATH}"
        ),
    )
    parser.add_argument(
        "--threshold-m",
        type=float,
        default=DEFAULT_DISTANCE_THRESHOLD_M,
        help="Distance threshold in meters for closeness and variety scores.",
    )
    parser.add_argument(
        "--total-routes",
        type=int,
        default=DEFAULT_TOTAL_ROUTES,
        help="Total number of distinct running routes used as the variety denominator.",
    )
    return parser.parse_args()


def load_geojson(path: Path, label: str) -> gpd.GeoDataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{label} GeoJSON not found: {path}")

    gdf = gpd.read_file(path)
    if gdf.empty:
        raise ValueError(f"{label} GeoJSON has no features: {path}")

    if gdf.crs is None:
        # Estos GeoJSON se guardan como longitud/latitud. Si falta el CRS, lo
        # fijamos para que la reproyeccion metrica posterior sea fiable.
        gdf = gdf.set_crs(SOURCE_CRS)

    valid_geometry = gdf.geometry.notna() & ~gdf.geometry.is_empty
    if not valid_geometry.all():
        removed = len(gdf) - int(valid_geometry.sum())
        print(f"Skipping {removed} {label.lower()} feature(s) without geometry.")
        gdf = gdf.loc[valid_geometry].copy()

    return gdf


def first_existing_column(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    available = set(columns)
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def add_route_unit_column(routes: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, str | None]:
    """Anade una columna estable para contar rutas distintas.

    Si el origen tiene identificador de ruta, se cuentan IDs unicos. Si no lo
    tiene, cada geometria cuenta como unidad de ruta. El archivo actual de rutas
    de Barcelona no tiene un campo route-id, por eso se mantiene este fallback.
    """

    routes = routes.copy()
    route_id_column = first_existing_column(routes.columns, ROUTE_ID_COLUMNS)

    if route_id_column is None:
        routes["_route_unit"] = routes.index.astype(str)
    else:
        routes["_route_unit"] = routes[route_id_column].fillna(routes.index.astype(str))

    return routes, route_id_column


def classify_running_score(score: float) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Acceptable"
    if score >= 20:
        return "Poor"
    return "Very poor"


def to_json_value(value: object) -> object:
    """Convierte escalares de pandas/numpy a valores compatibles con JSON."""

    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def calculate_scores(
    hotels: gpd.GeoDataFrame,
    routes: gpd.GeoDataFrame,
    threshold_m: float,
    total_routes: int,
) -> gpd.GeoDataFrame:
    if threshold_m <= 0:
        raise ValueError("--threshold-m must be greater than 0.")
    if total_routes <= 0:
        raise ValueError("--total-routes must be greater than 0.")

    # Reproyectamos a EPSG:25831 para que distancias y buffers esten en metros,
    # una unidad adecuada para Barcelona.
    hotels_metric = hotels.to_crs(METRIC_CRS)
    routes_metric = routes.to_crs(METRIC_CRS)
    routes_metric, route_id_column = add_route_unit_column(routes_metric)

    if len(routes_metric) != total_routes and route_id_column is None:
        print(
            "Warning: route file has "
            f"{len(routes_metric)} geometries but --total-routes is {total_routes}. "
            "Nearby counts will be capped at the configured route total."
        )

    # Distancia de cada hotel a la ruta mas cercana.
    routes_union = routes_metric.geometry.union_all()
    nearest_route_m = hotels_metric.geometry.distance(routes_union)

    # Contamos rutas distintas dentro del umbral cruzando buffers de hoteles con
    # geometria de rutas. El buffer solo se calcula en el CRS metrico.
    hotel_buffers = hotels_metric[["geometry"]].copy()
    hotel_buffers["geometry"] = hotel_buffers.geometry.buffer(threshold_m)
    hotel_buffers["_hotel_index"] = hotel_buffers.index

    nearby_join = gpd.sjoin(
        hotel_buffers[["_hotel_index", "geometry"]],
        routes_metric[["_route_unit", "geometry"]],
        how="left",
        predicate="intersects",
    )

    nearby_counts = (
        nearby_join.dropna(subset=["_route_unit"])
        .groupby("_hotel_index")["_route_unit"]
        .nunique()
    )
    nearby_routes_count = (
        nearby_counts.reindex(hotels_metric.index, fill_value=0)
        .astype(int)
        .clip(upper=total_routes)
    )

    closeness_score = (1 - nearest_route_m / threshold_m).clip(lower=0, upper=1)
    variety_score = (nearby_routes_count / total_routes).clip(lower=0, upper=1)
    running_accessibility_score = 100 * (
        0.8 * closeness_score + 0.2 * variety_score
    )

    # Conservamos la geometria original de hoteles para la salida. Si la entrada
    # no estaba en EPSG:4326, volvemos a longitud/latitud para el mapa web.
    result = hotels.copy()
    if result.crs != SOURCE_CRS:
        result = result.to_crs(SOURCE_CRS)

    result["nearest_route_m"] = nearest_route_m.round(2)
    result["nearby_routes_count"] = nearby_routes_count
    result["closeness_score"] = closeness_score.round(4)
    result["variety_score"] = variety_score.round(4)
    result["running_accessibility_score"] = running_accessibility_score.round(2)
    result["running_category"] = result["running_accessibility_score"].apply(
        classify_running_score
    )

    return result


def write_scored_geojson(
    result: gpd.GeoDataFrame,
    source_hotels_path: Path,
    output_path: Path,
) -> None:
    """Escribe el GeoJSON de hoteles puntuado.

    El flujo por defecto actualiza el GeoJSON original. En ese caso solo se
    modifican las propiedades de puntuacion para preservar propiedades que
    GeoPandas no siempre conserva al reescribir el archivo completo.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_output_path = output_path.with_name(
        f"{output_path.stem}.tmp{output_path.suffix}"
    )
    keep_temp_file = False

    try:
        is_in_place = output_path.resolve() == source_hotels_path.resolve()
        can_preserve_source_json = (
            is_in_place
            and str(result.crs) == SOURCE_CRS
            and source_hotels_path.exists()
        )

        if can_preserve_source_json:
            source_data = json.loads(source_hotels_path.read_text(encoding="utf-8-sig"))
            features = source_data.get("features", [])

            if len(features) == len(result):
                for feature, (_, row) in zip(features, result.iterrows()):
                    properties = feature.setdefault("properties", {})
                    for field in SCORED_FIELDS:
                        properties[field] = to_json_value(row[field])

                temp_output_path.write_text(
                    json.dumps(source_data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            else:
                print(
                    "Warning: source feature count changed during processing; "
                    "falling back to GeoPandas writer."
                )
                result.to_file(temp_output_path, driver="GeoJSON")
        else:
            result.to_file(temp_output_path, driver="GeoJSON")

        try:
            temp_output_path.replace(output_path)
        except PermissionError:
            if not is_in_place:
                raise

            # Algunos editores en Windows bloquean el reemplazo atomico de un
            # archivo abierto, pero permiten escritura normal. Para la actualizacion
            # in-place usamos una escritura directa como segunda opcion.
            output_path.write_text(
                temp_output_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            try:
                temp_output_path.unlink()
            except PermissionError:
                print(f"Warning: could not remove temporary file: {temp_output_path}")
                keep_temp_file = True
    finally:
        if not keep_temp_file and temp_output_path.exists():
            try:
                temp_output_path.unlink()
            except PermissionError:
                print(f"Warning: could not remove temporary file: {temp_output_path}")


def main() -> None:
    args = parse_args()

    hotels = load_geojson(args.hotels, "Hotels")
    routes = load_geojson(args.routes, "Routes")

    result = calculate_scores(
        hotels=hotels,
        routes=routes,
        threshold_m=args.threshold_m,
        total_routes=args.total_routes,
    )

    write_scored_geojson(result, args.hotels, args.output)

    category_counts = result["running_category"].value_counts().sort_index()
    print(f"Saved {len(result)} scored hotels to {args.output}")
    print("Category counts:")
    for category, count in category_counts.items():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
