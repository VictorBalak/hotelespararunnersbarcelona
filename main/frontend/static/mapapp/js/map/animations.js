import {
  HOTEL_REVEAL_DURATION_MS,
  ROUTE_COLOR,
  ROUTE_DRAW_DURATION_MS,
} from "./config.js";
import { cloneFeatureCollection } from "./geojson.js";


export function routeDrawGradient(progress) {
  const clampedProgress = Math.max(0, Math.min(progress, 1));

  return [
    "step",
    ["line-progress"],
    ROUTE_COLOR,
    clampedProgress,
    "rgba(202, 237, 66, 0)",
  ];
}

function routeVisibleGradient() {
  return [
    "interpolate",
    ["linear"],
    ["line-progress"],
    0,
    ROUTE_COLOR,
    1,
    ROUTE_COLOR,
  ];
}

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function easeOutCubic(progress) {
  return 1 - Math.pow(1 - progress, 3);
}

function shuffledFeatures(features) {
  const shuffled = [...features];

  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
  }

  return shuffled;
}

function animateRouteDraw(map) {
  if (prefersReducedMotion()) {
    map.setPaintProperty("routes-line", "line-gradient", routeVisibleGradient());
    return;
  }

  const start = performance.now();

  function drawFrame(now) {
    const rawProgress = Math.min((now - start) / ROUTE_DRAW_DURATION_MS, 1);
    const easedProgress = easeOutCubic(rawProgress);

    map.setPaintProperty("routes-line", "line-gradient", routeDrawGradient(easedProgress));

    if (rawProgress < 1) {
      window.requestAnimationFrame(drawFrame);
      return;
    }

    map.setPaintProperty("routes-line", "line-gradient", routeVisibleGradient());
  }

  window.requestAnimationFrame(drawFrame);
}

function revealHotelsRandomly(map, hotels) {
  const source = map.getSource("hotels");
  const allFeatures = hotels.features || [];

  if (!source || !allFeatures.length) {
    return;
  }

  if (prefersReducedMotion()) {
    source.setData(hotels);
    return;
  }

  const randomizedFeatures = shuffledFeatures(allFeatures);
  const start = performance.now();

  function revealFrame(now) {
    const rawProgress = Math.min((now - start) / HOTEL_REVEAL_DURATION_MS, 1);
    const easedProgress = easeOutCubic(rawProgress);
    const visibleCount = Math.ceil(easedProgress * randomizedFeatures.length);

    source.setData(cloneFeatureCollection(hotels, randomizedFeatures.slice(0, visibleCount)));

    if (rawProgress < 1) {
      window.requestAnimationFrame(revealFrame);
      return;
    }

    source.setData(hotels);
  }

  window.requestAnimationFrame(revealFrame);
}

export function startMapIntro(map, hotels) {
  // La intro separa visualmente las rutas y los hoteles sin cambiar los datos.
  animateRouteDraw(map);
  revealHotelsRandomly(map, hotels);
}
