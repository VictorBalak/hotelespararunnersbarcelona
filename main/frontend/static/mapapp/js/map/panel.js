import {
  formatCoordinates,
  formatDistance,
  formatReviewRating,
  formatRoutes,
  formatScore,
} from "./formatters.js";
import { emptyFeatureCollection } from "./geojson.js";


function setExternalLink(link, url, text, unavailableText) {
  link.textContent = url ? text : unavailableText;

  if (url) {
    link.href = url;
    link.classList.remove("is-disabled");
    link.removeAttribute("aria-disabled");
    return;
  }

  link.removeAttribute("href");
  link.classList.add("is-disabled");
  link.setAttribute("aria-disabled", "true");
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

export function openHotelPanel(map, feature) {
  const properties = feature.properties || {};
  const panel = document.getElementById("hotel-panel");
  const titleLink = document.getElementById("hotel-title-link");
  const bookingLink = document.getElementById("hotel-booking");
  const locationLink = document.getElementById("hotel-location");
  const summaryBlock = document.getElementById("hotel-summary-block");
  const summaryText = document.getElementById("hotel-summary");
  const hotelName = properties.name || "Unnamed hotel";
  const coordinates = formatCoordinates(feature.geometry?.coordinates);
  const reviewSummary = (properties.review_summary || "").trim();

  setExternalLink(titleLink, properties.booking, hotelName, hotelName);
  setExternalLink(bookingLink, properties.booking, "Open Booking", "Booking unavailable");
  setText("hotel-score", formatScore(properties.running_accessibility_score));
  setText(
    "hotel-rating",
    formatReviewRating(properties.hotel_rating, properties.hotel_rating_label),
  );
  setText("hotel-distance", formatDistance(properties.nearest_route_m));
  setText("hotel-routes", formatRoutes(properties.nearby_routes_count));

  if (coordinates) {
    setExternalLink(locationLink, coordinates.mapsUrl, coordinates.text, "No coordinates");
  } else {
    setExternalLink(locationLink, "", "", "No coordinates");
  }

  summaryText.textContent = reviewSummary;
  summaryBlock.hidden = !reviewSummary;

  map.getSource("selected-hotel").setData({
    type: "FeatureCollection",
    features: [feature],
  });

  panel.classList.add("is-open");
  panel.setAttribute("aria-hidden", "false");

  if (feature.geometry?.coordinates) {
    // Al centrar el hotel se reserva hueco visual para que el panel no lo tape.
    map.easeTo({
      center: feature.geometry.coordinates,
      duration: 300,
      padding: window.innerWidth > 720 ? { right: 360 } : { bottom: 220 },
    });
  }
}

export function closeHotelPanel(map) {
  const panel = document.getElementById("hotel-panel");
  panel.classList.remove("is-open");
  panel.setAttribute("aria-hidden", "true");

  if (map.getSource("selected-hotel")) {
    map.getSource("selected-hotel").setData(emptyFeatureCollection());
  }
}
