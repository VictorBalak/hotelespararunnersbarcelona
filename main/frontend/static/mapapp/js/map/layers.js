import {
  HOTEL_COLOR_EXPRESSION,
  HOTEL_STROKE,
} from "./config.js";
import { routeDrawGradient } from "./animations.js";
import { emptyFeatureCollection } from "./geojson.js";
import { openHotelPanel } from "./panel.js";


function wireRouteTooltip(map) {
  const tooltip = document.getElementById("route-tooltip");

  map.on("mousemove", "routes-line", (event) => {
    const feature = event.features && event.features[0];
    const name = feature?.properties?.display_name || "Barcelona route";

    tooltip.textContent = name;
    tooltip.style.transform = `translate(${event.point.x + 14}px, ${event.point.y + 14}px)`;
    tooltip.classList.add("is-visible");
    map.getCanvas().style.cursor = "crosshair";
  });

  map.on("mouseleave", "routes-line", () => {
    tooltip.classList.remove("is-visible");
    map.getCanvas().style.cursor = "";
  });
}

function addRouteLayer(map, routes) {
  map.addSource("routes", {
    type: "geojson",
    data: routes,
    lineMetrics: true,
  });

  map.addLayer({
    id: "routes-line",
    type: "line",
    source: "routes",
    layout: {
      "line-cap": "round",
      "line-join": "round",
    },
    paint: {
      "line-gradient": routeDrawGradient(0),
      "line-opacity": 0.94,
      "line-width": [
        "interpolate",
        ["linear"],
        ["zoom"],
        10,
        3,
        14,
        6,
        17,
        10,
      ],
    },
  });
}

function addHotelLayer(map) {
  map.addSource("hotels", {
    type: "geojson",
    data: emptyFeatureCollection(),
  });

  map.addLayer({
    id: "hotels-circle",
    type: "circle",
    source: "hotels",
    paint: {
      "circle-color": HOTEL_COLOR_EXPRESSION,
      "circle-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        10,
        4,
        13,
        6,
        16,
        9,
      ],
      "circle-stroke-color": HOTEL_STROKE,
      "circle-stroke-width": 1.8,
      "circle-opacity": 0.94,
    },
  });
}

function addSelectedHotelLayer(map) {
  map.addSource("selected-hotel", {
    type: "geojson",
    data: emptyFeatureCollection(),
  });

  map.addLayer({
    id: "selected-hotel",
    type: "circle",
    source: "selected-hotel",
    paint: {
      "circle-color": HOTEL_COLOR_EXPRESSION,
      "circle-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        10,
        7,
        13,
        11,
        16,
        15,
      ],
      "circle-stroke-color": HOTEL_STROKE,
      "circle-stroke-width": 3,
    },
  });
}

function wireHotelEvents(map) {
  map.on("mouseenter", "hotels-circle", () => {
    map.getCanvas().style.cursor = "pointer";
  });

  map.on("mouseleave", "hotels-circle", () => {
    map.getCanvas().style.cursor = "";
  });

  map.on("click", "hotels-circle", (event) => {
    if (event.features && event.features[0]) {
      openHotelPanel(map, event.features[0]);
    }
  });
}

export function addDataLayers(map, routes) {
  // Las rutas se anaden antes que los hoteles para que los puntos queden encima.
  addRouteLayer(map, routes);
  addHotelLayer(map);
  addSelectedHotelLayer(map);
  wireHotelEvents(map);
  wireRouteTooltip(map);
}
