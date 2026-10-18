(function () {
  const root = document.getElementById("reports");
  const index = document.getElementById("reportIndex");
  const PALETTE = ["#2563eb", "#16a34a", "#d97706", "#db2777", "#7c3aed", "#0891b2", "#65a30d", "#dc2626"];

  CONFIG.reports.forEach((r) => {
    index.insertAdjacentHTML("beforeend", `<a href="#${r.id}">${escapeHtml(r.title)}</a>`);
    root.append(buildReport(r));
  });

  function paramInput(p) {
    const id = `p-${p.name}`;
    if (p.type === "select") {
      // options can be plain strings or { value, label }
      const opts = p.options.map((o) => {
        const value = typeof o === "object" ? o.value : o;
        const label = typeof o === "object" ? o.label : (o === "" ? "All" : o);
        return `<option value="${escapeHtml(value)}" ${value === p.default ? "selected" : ""}>${escapeHtml(label)}</option>`;
      }).join("");
      return `<label>${escapeHtml(p.label)}<select name="${p.name}" id="${id}">${opts}</select></label>`;
    }
    return `<label>${escapeHtml(p.label)}<input name="${p.name}" id="${id}" type="${p.type || "text"}" value="${escapeHtml(p.default ?? "")}"></label>`;
  }

  function buildReport(r) {
    const section = document.createElement("section");
    section.className = "card report";
    section.id = r.id;
    const hasChart = r.chart && r.chart !== "table";
    section.innerHTML = `
      <div class="report-head">
        <div>
          <h2>${escapeHtml(r.title)}</h2>
          ${r.description ? `<p class="muted">${escapeHtml(r.description)}</p>` : ""}
        </div>
        <span class="badge mock-badge" hidden>Mock data</span>
      </div>
      ${r.params?.length ? `<form class="toolbar" onsubmit="return false">${r.params.map(paramInput).join("")}</form>` : ""}
      ${hasChart ? `<div class="chart-box"><canvas></canvas></div>` : ""}
      <details ${hasChart ? "" : "open"}>
        <summary>Data table</summary>
        <div class="report-table"></div>
      </details>`;

    let chart = null;
    const form = section.querySelector("form");
    const tableEl = section.querySelector(".report-table");

    async function run() {
      const params = form ? Object.fromEntries(new FormData(form)) : {};
      tableEl.innerHTML = `<p class="empty">Loading…</p>`;
      try {
        const { rows, mock } = await getData(r, params);
        section.querySelector(".mock-badge").hidden = !mock;
        renderTable(tableEl, rows);
        if (hasChart) chart = drawChart(section.querySelector("canvas"), r, rows, chart);
      } catch (err) {
        showError(tableEl, err);
        section.querySelector("details").open = true;
      }
    }

    form?.addEventListener("change", run);
    run();
    return section;
  }

  function drawChart(canvas, r, rows, existing) {
    existing?.destroy();
    if (typeof Chart === "undefined") {
      canvas.replaceWith(Object.assign(document.createElement("p"),
        { className: "error", textContent: "Chart.js failed to load (offline?). See the data table." }));
      return null;
    }
    const round = r.chart === "pie" || r.chart === "doughnut";
    rows = r.chartRows ? r.chartRows(rows) : rows;
    // x can be a column name or a function(row) -> label
    const labels = rows.map((row) => (typeof r.x === "function" ? r.x(row) : row[r.x]));
    const datasets = r.y.map((col, i) => ({
      label: col,
      data: rows.map((row) => Number(row[col])),
      backgroundColor: round ? labels.map((_, j) => PALETTE[j % PALETTE.length]) : PALETTE[i % PALETTE.length],
      borderColor: round ? "transparent" : PALETTE[i % PALETTE.length],
      tension: 0.25,
    }));
    return new Chart(canvas, {
      type: r.chart,
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: r.horizontal ? "y" : "x",   // horizontal bars for long labels
        plugins: { legend: { display: round || r.y.length > 1 } },
        scales: round ? {} : { [r.horizontal ? "x" : "y"]: { beginAtZero: true } },
      },
    });
  }
})();
