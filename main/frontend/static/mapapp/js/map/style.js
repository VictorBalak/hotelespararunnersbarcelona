import { MAP_STYLE_COLORS } from "./config.js";


export function createBaseStyle() {
  return {
    version: 8,
    name: "Barcelona running map",
    glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
    sources: {
      openmaptiles: {
        type: "vector",
        url: "https://tiles.openfreemap.org/planet",
      },
    },
    layers: [
      {
        id: "background",
        type: "background",
        paint: {
          "background-color": MAP_STYLE_COLORS.background,
        },
      },
      {
        id: "water",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "water",
        paint: {
          "fill-color": MAP_STYLE_COLORS.water,
        },
      },
      {
        id: "parks",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "park",
        paint: {
          "fill-color": MAP_STYLE_COLORS.parks,
          "fill-opacity": 0.72,
        },
      },
      {
        id: "buildings",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "building",
        minzoom: 14,
        paint: {
          "fill-color": MAP_STYLE_COLORS.buildings,
          "fill-opacity": 0.7,
        },
      },
      {
        id: "streets-casing",
        type: "line",
        source: "openmaptiles",
        "source-layer": "transportation",
        paint: {
          "line-color": MAP_STYLE_COLORS.streetCasing,
          "line-opacity": 0.95,
          "line-width": [
            "interpolate",
            ["linear"],
            ["zoom"],
            10,
            1.4,
            14,
            4.2,
            17,
            10,
          ],
        },
      },
      {
        id: "streets",
        type: "line",
        source: "openmaptiles",
        "source-layer": "transportation",
        paint: {
          "line-color": MAP_STYLE_COLORS.streets,
          "line-opacity": 1,
          "line-width": [
            "interpolate",
            ["linear"],
            ["zoom"],
            10,
            0.8,
            14,
            2.6,
            17,
            7,
          ],
        },
      },
      {
        id: "place-labels",
        type: "symbol",
        source: "openmaptiles",
        "source-layer": "place",
        minzoom: 9,
        layout: {
          "text-field": ["coalesce", ["get", "name:latin"], ["get", "name"]],
          "text-font": ["Noto Sans Regular"],
          "text-size": [
            "interpolate",
            ["linear"],
            ["zoom"],
            10,
            11,
            14,
            14,
          ],
        },
        paint: {
          "text-color": MAP_STYLE_COLORS.text,
          "text-halo-color": MAP_STYLE_COLORS.background,
          "text-halo-width": 1.2,
        },
      },
    ],
  };
}
