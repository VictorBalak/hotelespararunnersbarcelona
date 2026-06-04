export async function fetchGeojson(url) {
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Could not load ${url}`);
  }

  return response.json();
}

export function emptyFeatureCollection() {
  return {
    type: "FeatureCollection",
    features: [],
  };
}

export function cloneFeatureCollection(collection, features) {
  return {
    ...collection,
    features,
  };
}

function addCoordinateToBounds(bounds, coordinate) {
  if (
    Array.isArray(coordinate) &&
    coordinate.length >= 2 &&
    typeof coordinate[0] === "number" &&
    typeof coordinate[1] === "number"
  ) {
    bounds.extend(coordinate);
    return;
  }

  if (Array.isArray(coordinate)) {
    coordinate.forEach((child) => addCoordinateToBounds(bounds, child));
  }
}

export function fitToData(map, collections, maxZoom) {
  const bounds = new window.maplibregl.LngLatBounds();

  collections.forEach((collection) => {
    (collection.features || []).forEach((feature) => {
      addCoordinateToBounds(bounds, feature.geometry.coordinates);
    });
  });

  if (!bounds.isEmpty()) {
    // El padding reserva espacio para el panel lateral en escritorio.
    map.fitBounds(bounds, {
      duration: 0,
      maxZoom,
      padding: {
        top: 64,
        right: window.innerWidth > 720 ? 470 : 42,
        bottom: 92,
        left: 64,
      },
    });
  }
}
