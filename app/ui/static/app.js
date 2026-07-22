const tableList = document.querySelector("#table-list");
const statusMessage = document.querySelector("#status-message");
const lastUpdated = document.querySelector("#last-updated");
const refreshButton = document.querySelector("#refresh-button");
const template = document.querySelector("#table-card-template");
const readinessPanel = document.querySelector("#readiness-panel");
const readinessTitle = document.querySelector("#readiness-title");
const readinessNextStep = document.querySelector("#readiness-next-step");
const readinessChecks = document.querySelector("#readiness-checks");
const occupiedCount = document.querySelector("#occupied-count");
const emptyCount = document.querySelector("#empty-count");
const uncertainCount = document.querySelector("#uncertain-count");
const videoTestFile = document.querySelector("#video-test-file");
const videoTestButton = document.querySelector("#video-test-button");
const videoTestStatus = document.querySelector("#video-test-status");
const workflowNotice = document.querySelector("#workflow-notice");

const readinessLabels = {
  camera_config: "Kamera yapılandırması",
  table_calibration: "Masa kalibrasyonu",
  person_model: "Kişi tespit modeli",
};

if (new URLSearchParams(window.location.search).get("calibration") === "saved") {
  workflowNotice.classList.add("workflow-notice--saved");
  workflowNotice.innerHTML = "<strong>Kalibrasyon kaydedildi.</strong> Hazırlık kontrolü yenilendi. Doluluk sonuçları model hazırlandıktan ve video işlendikten sonra değişir.";
}

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

  const totals = { occupied: 0, empty: 0, uncertain: 0 };
  tables.forEach((table) => {
    totals[normalizeStatus(table.status)] += 1;
  });
  occupiedCount.textContent = totals.occupied;
  emptyCount.textContent = totals.empty;
  uncertainCount.textContent = totals.uncertain;

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
  videoTestButton.disabled = !ready || !videoTestFile.files.length;
  if (!ready) {
    videoTestStatus.textContent = "Kalibrasyon ve model hazır olmadan video işlenemez.";
  }

  (data.checks ?? []).forEach((check) => {
    const item = document.createElement("li");
    item.className = `readiness-check readiness-check--${check.status}`;
    const label = readinessLabels[check.name] ?? check.name ?? "Kontrol";
    item.textContent = `${check.status === "pass" ? "✓" : "!"} ${label}: ${check.message}`;
    readinessChecks.append(item);
  });
}

videoTestFile.addEventListener("change", () => {
  videoTestButton.disabled = !videoTestFile.files.length || readinessPanel.classList.contains("readiness-panel--blocked");
  if (videoTestFile.files.length) {
    videoTestStatus.textContent = `${videoTestFile.files[0].name} seçildi.`;
  }
});

videoTestButton.addEventListener("click", async () => {
  const file = videoTestFile.files[0];
  if (!file) return;
  videoTestButton.disabled = true;
  videoTestStatus.textContent = "Video işleniyor; bu işlem birkaç dakika sürebilir…";
  try {
    const response = await fetch("/product/video-test", {
      method: "POST",
      headers: { "Content-Type": "application/octet-stream", "X-Video-Filename": file.name },
      body: file,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.next_step ?? data.detail ?? `HTTP ${response.status}`);
    videoTestStatus.textContent = `${data.processed_frames} kare işlendi; ${data.table_count} masa güncellendi.`;
    await loadOccupancy();
  } catch (error) {
    videoTestStatus.textContent = `Video testi başarısız: ${error.message}`;
  } finally {
    videoTestButton.disabled = false;
  }
});

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
