import { MAP_VIEW } from "./map/config.js";
import { showMapError } from "./map/dom.js";
import { fetchGeojson, fitToData } from "./map/geojson.js";
import { addDataLayers } from "./map/layers.js";
import { renderScoreLegend } from "./map/legend.js";
import { closeHotelPanel } from "./map/panel.js";
import { createBaseStyle } from "./map/style.js";
import { startMapIntro } from "./map/animations.js";


async function initMap() {
  if (!window.maplibregl) {
    showMapError("Map library could not be loaded.");
    return;
  }

  renderScoreLegend();

  const urls = document.body.dataset;
  const map = new window.maplibregl.Map({
    attributionControl: false,
    center: MAP_VIEW.center,
    container: "map",
    maxBounds: MAP_VIEW.maxBounds,
    minZoom: MAP_VIEW.minZoom,
    pitchWithRotate: false,
    style: createBaseStyle(),
    zoom: MAP_VIEW.zoom,
  });

  map.addControl(new window.maplibregl.NavigationControl({ showCompass: false }), "top-left");
  map.addControl(new window.maplibregl.AttributionControl({ compact: true }), "bottom-right");

  document.getElementById("panel-close").addEventListener("click", () => {
    closeHotelPanel(map);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeHotelPanel(map);
    }
  });

  map.on("load", async () => {
    try {
      const [hotels, routes] = await Promise.all([
        fetchGeojson(urls.hotelsUrl),
        fetchGeojson(urls.routesUrl),
      ]);

      addDataLayers(map, routes);
      fitToData(map, [hotels, routes], MAP_VIEW.fitMaxZoom);
      startMapIntro(map, hotels);
    } catch (error) {
      showMapError(error.message);
    }
  });
}

window.addEventListener("DOMContentLoaded", initMap);
