export const ROUTE_COLOR = "#CAED42";
export const HOTEL_STROKE = "#424140";
export const ROUTE_DRAW_DURATION_MS = 5000;
export const HOTEL_REVEAL_DURATION_MS = 5000;

export const MAP_VIEW = {
  center: [2.1734, 41.3851],
  maxBounds: [
    [1.96, 41.24],
    [2.36, 41.55],
  ],
  minZoom: 10,
  zoom: 12,
  fitMaxZoom: 13.2,
};

export const MAP_STYLE_COLORS = {
  background: "#F6F3F1",
  water: "#ece9e7",
  parks: "#ebe9e0",
  buildings: "#ebe7e2",
  streetCasing: "#f9f7f5",
  streets: "#DDDAD8",
  text: "#706c68",
};

export const SCORE_COLORS = {
  red: "#d94b42",
  orange: "#ef8d3c",
  yellow: "#e3c83d",
  green: "#3aa861",
};

// Las etiquetas comparten limites porque el usuario quiere ver rangos tipo 15-50.
export const HOTEL_SCORE_BANDS = [
  {
    key: "green",
    label: "70-100",
    min: 70,
    color: SCORE_COLORS.green,
  },
  {
    key: "yellow",
    label: "50-70",
    min: 50,
    color: SCORE_COLORS.yellow,
  },
  {
    key: "orange",
    label: "15-50",
    min: 15,
    color: SCORE_COLORS.orange,
  },
  {
    key: "red",
    label: "0-15",
    min: 0,
    color: SCORE_COLORS.red,
  },
];

export const SCORE_EXPRESSION = [
  "to-number",
  ["coalesce", ["get", "running_accessibility_score"], 0],
  0,
];

export const HOTEL_COLOR_EXPRESSION = [
  "case",
  ...HOTEL_SCORE_BANDS.filter((band) => band.min > 0).flatMap((band) => [
    [">=", SCORE_EXPRESSION, band.min],
    band.color,
  ]),
  HOTEL_SCORE_BANDS.find((band) => band.min === 0).color,
];
