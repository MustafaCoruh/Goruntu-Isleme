const tableList = document.querySelector("#table-list");
const statusMessage = document.querySelector("#status-message");
const lastUpdated = document.querySelector("#last-updated");
const refreshButton = document.querySelector("#refresh-button");
const template = document.querySelector("#table-card-template");
const readinessPanel = document.querySelector("#readiness-panel");
const readinessTitle = document.querySelector("#readiness-title");
const readinessNextStep = document.querySelector("#readiness-next-step");
const readinessChecks = document.querySelector("#readiness-checks");

const statusLabels = {
  occupied: "Dolu",
  empty: "Boş",
  uncertain: "Belirsiz",
};

function formatTimestamp(value) {
  if (!value) {
    return "Bilinmiyor";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("tr-TR", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}

function normalizeStatus(status) {
  return Object.hasOwn(statusLabels, status) ? status : "uncertain";
}

function renderTables(tables = []) {
  tableList.replaceChildren();

  if (tables.length === 0) {
    statusMessage.textContent = "Gösterilecek masa bulunamadı.";
    return;
  }

  statusMessage.textContent = "";

  tables.forEach((table) => {
    const card = template.content.firstElementChild.cloneNode(true);
    const status = normalizeStatus(table.status);

    card.classList.add(`table-card--${status}`);
    card.querySelector("h2").textContent = table.name ?? table.table_id ?? "Masa";
    card.querySelector(".table-card__status").textContent = statusLabels[status];
    card.querySelector(".table-card__confidence").textContent =
      typeof table.confidence === "number" ? table.confidence.toFixed(2) : "-";

    tableList.append(card);
  });
}

async function loadOccupancy() {
  statusMessage.textContent = "Veriler alınıyor...";
  refreshButton.disabled = true;

  try {
    const response = await fetch("/occupancy/current", { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    renderTables(data.tables);
    lastUpdated.textContent = formatTimestamp(data.timestamp);
    lastUpdated.dateTime = data.timestamp ?? "";
  } catch (error) {
    statusMessage.textContent = `Doluluk verisi alınamadı: ${error.message}`;
  } finally {
    refreshButton.disabled = false;
  }
}

function renderReadiness(data) {
  const ready = data.ready_for_video_test === true;
  readinessPanel.classList.toggle("readiness-panel--ready", ready);
  readinessPanel.classList.toggle("readiness-panel--blocked", !ready);
  readinessTitle.textContent = ready ? "Video testine hazır" : "Video testi için eksikler var";
  readinessNextStep.textContent = data.next_step ?? "Ürün hazırlık sonucu alınamadı.";
  readinessChecks.replaceChildren();

  (data.checks ?? []).forEach((check) => {
    const item = document.createElement("li");
    item.className = `readiness-check readiness-check--${check.status}`;
    item.textContent = `${check.status === "pass" ? "✓" : "!"} ${check.message}`;
    readinessChecks.append(item);
  });
}

async function loadReadiness() {
  try {
    const response = await fetch("/product/readiness", { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    renderReadiness(await response.json());
  } catch (error) {
    readinessTitle.textContent = "Ürün kontrolü alınamadı";
    readinessNextStep.textContent = error.message;
    readinessPanel.classList.add("readiness-panel--blocked");
  }
}

refreshButton.addEventListener("click", () => {
  loadOccupancy();
  loadReadiness();
});
loadOccupancy();
loadReadiness();
