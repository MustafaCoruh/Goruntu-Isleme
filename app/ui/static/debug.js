const debugFrame = document.querySelector("#debug-frame");
const debugOverlay = document.querySelector("#debug-overlay");
const debugStatus = document.querySelector("#debug-status");
const debugRefreshButton = document.querySelector("#debug-refresh-button");

const REFRESH_INTERVAL_MS = 2000;
const SVG_NS = "http://www.w3.org/2000/svg";
const statusColors = {
  occupied: "#dc2626",
  empty: "#16a34a",
  uncertain: "#facc15",
};

function svgElement(name, attributes = {}) {
  const element = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  return element;
}

function tableLabel(table) {
  const confidence = typeof table.confidence === "number" ? table.confidence.toFixed(2) : "-";
  return `${table.name ?? table.table_id}: ${table.status ?? "uncertain"} (${confidence})`;
}

function drawTable(table) {
  const points = (table.polygon ?? []).map(([x, y]) => `${x},${y}`).join(" ");
  if (!points) return;

  const color = statusColors[table.status] ?? statusColors.uncertain;
  debugOverlay.append(svgElement("polygon", {
    points,
    fill: `${color}33`,
    stroke: color,
    "stroke-width": "6",
  }));

  const [labelX, labelY] = table.polygon[0];
  const text = svgElement("text", {
    x: labelX,
    y: Math.max(24, labelY - 12),
    fill: "#ffffff",
    "font-size": "28",
    "font-weight": "700",
  });
  text.textContent = tableLabel(table);
  debugOverlay.append(text);
}

function drawDetection(detection) {
  if (detection.class_name !== "person" || !Array.isArray(detection.bbox)) return;
  const [x1, y1, x2, y2] = detection.bbox;
  debugOverlay.append(svgElement("rect", {
    x: x1,
    y: y1,
    width: x2 - x1,
    height: y2 - y1,
    fill: "transparent",
    stroke: "#2563eb",
    "stroke-width": "6",
  }));
}

function renderDebugState(data) {
  const cacheBust = `t=${Date.now()}`;
  debugFrame.src = `${data.frame_url}?${cacheBust}`;
  debugOverlay.setAttribute("viewBox", `0 0 ${data.frame.width} ${data.frame.height}`);
  debugOverlay.replaceChildren();

  (data.tables ?? []).forEach(drawTable);
  (data.detections ?? []).forEach(drawDetection);
  debugStatus.textContent = `Son güncelleme: ${new Date(data.timestamp).toLocaleString("tr-TR")}`;
}

async function loadDebugState() {
  debugRefreshButton.disabled = true;
  try {
    const response = await fetch(`/debug/state?t=${Date.now()}`, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderDebugState(await response.json());
  } catch (error) {
    debugStatus.textContent = `Debug ekranı kapalı veya veri alınamadı: ${error.message}`;
    debugFrame.removeAttribute("src");
    debugOverlay.replaceChildren();
  } finally {
    debugRefreshButton.disabled = false;
  }
}

debugRefreshButton.addEventListener("click", loadDebugState);
loadDebugState();
setInterval(loadDebugState, REFRESH_INTERVAL_MS);
