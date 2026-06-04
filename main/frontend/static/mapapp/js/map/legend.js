import { HOTEL_SCORE_BANDS } from "./config.js";


export function renderScoreLegend() {
  const legendItems = document.getElementById("score-legend-items");

  if (!legendItems) {
    return;
  }

  legendItems.replaceChildren();
  HOTEL_SCORE_BANDS.slice()
    .sort((left, right) => left.min - right.min)
    .forEach((band) => {
      const item = document.createElement("div");
      const dot = document.createElement("span");

      dot.className = `legend-dot legend-dot-${band.key}`;
      item.append(dot, document.createTextNode(band.label));
      legendItems.appendChild(item);
    });
}
