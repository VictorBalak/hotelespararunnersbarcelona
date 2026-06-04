"""Construye el GeoJSON enriquecido de hoteles para la pagina Django del mapa.

El script combina unicamente datasets locales del backend:

- geometria de hoteles y puntuaciones runner desde GeoJSON
- metadatos hoteleros desde el Excel de hoteles
- valoraciones y recuentos desde el Excel de reviews

El campo de resumen de reviews se crea, pero queda vacio salvo que ya exista
contenido previo. Asi se puede rellenar mas tarde con un paso independiente.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"

DEFAULT_HOTELS_GEOJSON = DATA_DIR / "barcelona_hotels_location.geojson"
DEFAULT_HOTELS_WORKBOOK = DATA_DIR / "barcelona_hotels_list.xlsx"
DEFAULT_REVIEWS_WORKBOOK = DATA_DIR / "barcelona_hotels_reviews.xlsx"
DEFAULT_OUTPUT_PATH = DATA_DIR / "barcelona_hotels_enriched.geojson"

METADATA_FIELDS = (
    "booking",
    "website",
    "contact:website",
    "phone",
    "contact:phone",
    "addr:street",
    "addr:housenumber",
    "addr:postcode",
    "addr:neighbourhood",
    "rooms",
    "wheelchair",
    "swimming_pool",
    "internet_access",
)

SCORE_FIELDS = (
    "nearest_route_m",
    "nearby_routes_count",
    "closeness_score",
    "variety_score",
    "running_accessibility_score",
    "running_category",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a local enriched hotel GeoJSON for the map frontend."
    )
    parser.add_argument(
        "--hotels-geojson",
        type=Path,
        default=DEFAULT_HOTELS_GEOJSON,
        help=f"Scored hotel point GeoJSON. Default: {DEFAULT_HOTELS_GEOJSON}",
    )
    parser.add_argument(
        "--hotels-workbook",
        type=Path,
        default=DEFAULT_HOTELS_WORKBOOK,
        help=f"Hotel metadata workbook. Default: {DEFAULT_HOTELS_WORKBOOK}",
    )
    parser.add_argument(
        "--reviews-workbook",
        type=Path,
        default=DEFAULT_REVIEWS_WORKBOOK,
        help=f"Hotel reviews workbook. Default: {DEFAULT_REVIEWS_WORKBOOK}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output enriched GeoJSON path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    return parser.parse_args()


def clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def clean_url(value: Any) -> str | None:
    cleaned = clean_value(value)
    if cleaned is None:
        return None
    text = str(cleaned).strip()
    return text or None


def read_hotels_geojson(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Hotel GeoJSON not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8-sig"))
    features = data.get("features", [])
    if not features:
        raise ValueError(f"Hotel GeoJSON has no features: {path}")
    return data


def load_metadata(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Hotel metadata workbook not found: {path}")

    metadata = pd.read_excel(path)
    if "@id" not in metadata.columns:
        raise ValueError("Hotel metadata workbook must include an '@id' column.")

    metadata = metadata.copy()
    metadata["@id"] = metadata["@id"].astype(str)
    return metadata.set_index("@id", drop=False)


def load_review_stats(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Reviews workbook not found: {path}")

    reviews = pd.read_excel(path, sheet_name="Data")
    if "startUrl" not in reviews.columns:
        raise ValueError("Reviews workbook must include a 'startUrl' column.")

    reviews = reviews.copy()
    reviews["startUrl"] = reviews["startUrl"].map(clean_url)
    reviews = reviews.dropna(subset=["startUrl"])

    review_stats = reviews.groupby("startUrl").agg(
        hotel_rating=("hotelRating", "first"),
        average_review_score=("rating", "mean"),
        review_count=("rating", "count"),
        hotel_rating_label=("hotelRatingLabel", "first"),
    )
    review_stats["average_review_score"] = review_stats["average_review_score"].round(2)
    return review_stats


def load_existing_review_summaries(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8-sig"))
    summaries: dict[str, str] = {}

    for feature in data.get("features", []):
        properties = feature.get("properties") or {}
        summary = clean_url(properties.get("review_summary"))

        if not summary:
            continue

        for key_value in (properties.get("@id"), properties.get("booking")):
            key = clean_url(key_value)
            if key:
                summaries[key] = summary

    return summaries


def enrich_feature(
    feature: dict[str, Any],
    metadata: pd.DataFrame,
    review_stats: pd.DataFrame,
    existing_review_summaries: dict[str, str],
) -> dict[str, Any]:
    properties = feature.setdefault("properties", {})
    hotel_id = clean_url(properties.get("@id"))
    metadata_row = metadata.loc[hotel_id] if hotel_id in metadata.index else None
    metadata_review_summary = ""

    if metadata_row is not None:
        for field in ("name", "stars"):
            properties[field] = clean_value(metadata_row.get(field, properties.get(field)))

        for field in METADATA_FIELDS:
            if field in metadata_row.index:
                properties[field] = clean_value(metadata_row.get(field))

        if "review_summary" in metadata_row.index:
            metadata_review_summary = clean_url(metadata_row.get("review_summary")) or ""

    booking_url = clean_url(properties.get("booking"))
    stats_row = review_stats.loc[booking_url] if booking_url in review_stats.index else None

    if stats_row is not None:
        properties["hotel_rating"] = clean_value(stats_row.get("hotel_rating"))
        properties["average_review_score"] = clean_value(
            stats_row.get("average_review_score")
        )
        properties["review_count"] = clean_value(stats_row.get("review_count"))
        properties["hotel_rating_label"] = clean_value(stats_row.get("hotel_rating_label"))
    else:
        properties["hotel_rating"] = None
        properties["average_review_score"] = None
        properties["review_count"] = 0
        properties["hotel_rating_label"] = None

    for field in SCORE_FIELDS:
        properties[field] = clean_value(properties.get(field))

    properties["review_summary"] = (
        metadata_review_summary
        or existing_review_summaries.get(hotel_id)
        or existing_review_summaries.get(booking_url)
        or ""
    )
    return feature


def write_geojson(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()

    hotels_data = read_hotels_geojson(args.hotels_geojson)
    metadata = load_metadata(args.hotels_workbook)
    review_stats = load_review_stats(args.reviews_workbook)
    existing_review_summaries = load_existing_review_summaries(args.output)

    features = hotels_data["features"]
    for feature in features:
        enrich_feature(feature, metadata, review_stats, existing_review_summaries)

    write_geojson(hotels_data, args.output)

    matched_reviews = sum(
        1
        for feature in features
        if feature.get("properties", {}).get("review_count", 0) > 0
    )
    matched_booking = sum(
        1
        for feature in features
        if feature.get("properties", {}).get("booking")
    )
    matched_summaries = sum(
        1
        for feature in features
        if clean_url(feature.get("properties", {}).get("review_summary"))
    )

    print(f"Saved {len(features)} enriched hotels to {args.output}")
    print(f"Hotels with Booking URLs: {matched_booking}")
    print(f"Hotels with matched reviews: {matched_reviews}")
    print(f"Hotels with review summaries: {matched_summaries}")


if __name__ == "__main__":
    main()
