export function showMapError(message) {
  const shell = document.querySelector(".map-shell");
  const error = document.createElement("div");

  error.className = "map-error";
  error.textContent = message;

  shell.appendChild(error);
}
