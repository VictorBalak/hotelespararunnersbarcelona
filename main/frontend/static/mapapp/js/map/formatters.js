export function toNumber(value) {
  if (typeof value === "string") {
    return Number(value.replace(",", "."));
  }

  return Number(value);
}

export function formatScore(value) {
  const score = toNumber(value);
  return Number.isFinite(score) ? `${score.toFixed(0)} / 100` : "No score";
}

export function formatDistance(value) {
  const meters = toNumber(value);

  if (!Number.isFinite(meters)) {
    return "No distance";
  }

  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(2)} km`;
  }

  return `${Math.round(meters)} m`;
}

export function formatRoutes(value) {
  const count = toNumber(value);

  if (!Number.isFinite(count)) {
    return "0 routes";
  }

  return `${count} ${count === 1 ? "route" : "routes"}`;
}

export function formatReviewRating(value, label) {
  const rating = toNumber(value);

  if (!Number.isFinite(rating)) {
    return "No review score";
  }

  const ratingText = `${rating.toFixed(1)} / 10`;
  return label ? `${ratingText} - ${label}` : ratingText;
}

export function formatCoordinates(coordinates) {
  if (
    !Array.isArray(coordinates) ||
    coordinates.length < 2 ||
    !Number.isFinite(Number(coordinates[0])) ||
    !Number.isFinite(Number(coordinates[1]))
  ) {
    return null;
  }

  const longitude = Number(coordinates[0]);
  const latitude = Number(coordinates[1]);
  const text = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;

  return {
    text,
    mapsUrl: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(text)}`,
  };
}
