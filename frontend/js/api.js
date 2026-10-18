// Fetch helpers shared by every page.

function apiBase() {
  if (CONFIG.API_BASE) return CONFIG.API_BASE.replace(/\/$/, "");
  // same origin when served over http(s); fall back to local uvicorn when opened as file://
  return location.protocol.startsWith("http") ? location.origin : "http://127.0.0.1:8000";
}

function buildUrl(endpoint, params = {}) {
  const url = new URL(apiBase() + endpoint);
  for (const [k, v] of Object.entries(params)) {
    if (v !== "" && v !== null && v !== undefined) url.searchParams.set(k, v);
  }
  return url;
}

async function fetchJson(endpoint, params = {}) {
  const res = await fetch(buildUrl(endpoint, params));
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const body = await res.json();
      msg = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
    } catch { /* non-JSON error body */ }
    throw new Error(`${res.status} ${msg}`);
  }
  return res.json();
}

function isMock(item) {
  return CONFIG.USE_MOCK || !item.endpoint;
}

// Returns { rows, total, mock }
async function getData(item, params = {}) {
  if (isMock(item)) {
    const fn = MOCK[item.id];
    const rows = fn ? fn(params) : [];
    return { rows, total: rows.length, mock: true };
  }
  const data = await fetchJson(item.endpoint, params);
  const rows = Array.isArray(data) ? data : data.rows ?? [];
  return { rows, total: data.total ?? rows.length, mock: false };
}

// ---------- formatting ----------
const fmt = {
  int: (v) => Number(v).toLocaleString("en-PH", { maximumFractionDigits: 0 }),
  money: (v) => Number(v).toLocaleString("en-PH", { style: "currency", currency: "PHP" }),
  date: (v) => new Date(`${v}T00:00:00`).toLocaleDateString("en-PH", { year: "numeric", month: "short", day: "numeric" }),
  // whole numbers stay whole; decimals always show 2 places (1,680.10)
  num: (v) => Number(v).toLocaleString("en-PH",
    Number.isInteger(Number(v)) ? {} : { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
};

// ids, keys and years print as-is (no "1,976")
const RAW_NUMBER_COLS = /(^id$|_id$|key$|year$)/i;

function formatCell(v, col = "") {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return RAW_NUMBER_COLS.test(col) ? String(v) : fmt.num(v);
  return String(v);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Renders an array of row objects into a <table>. Columns come from the first row.
function renderTable(container, rows, { onSort, sort, order } = {}) {
  if (!rows.length) {
    container.innerHTML = `<p class="empty">No rows.</p>`;
    return;
  }
  const cols = Object.keys(rows[0]);
  const arrow = (c) => (c === sort ? (order === "desc" ? " ▼" : " ▲") : "");
  container.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr>${cols.map((c) =>
          `<th data-col="${escapeHtml(c)}" class="${onSort ? "sortable" : ""}">${escapeHtml(c)}${arrow(c)}</th>`).join("")}
        </tr></thead>
        <tbody>${rows.map((r) =>
          `<tr>${cols.map((c) =>
            `<td class="${typeof r[c] === "number" ? "num" : ""}">${escapeHtml(formatCell(r[c], c))}</td>`).join("")}</tr>`).join("")}
        </tbody>
      </table>
    </div>`;
  if (onSort) {
    container.querySelectorAll("th").forEach((th) =>
      th.addEventListener("click", () => onSort(th.dataset.col)));
  }
}

function showError(container, err) {
  container.innerHTML = `<p class="error">Couldn't load data: ${escapeHtml(err.message)}</p>`;
}
