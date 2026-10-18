(function () {
  const grid = document.getElementById("kpis");
  const period = document.getElementById("period");

  // one tile per KPI, all filled from the same /api/overview row
  const tiles = CONFIG.kpis.map((kpi) => {
    const tile = document.createElement("div");
    tile.className = "card kpi";
    tile.innerHTML = `<span class="kpi-label">${escapeHtml(kpi.label)}</span>
                      <span class="kpi-value">…</span>`;
    grid.append(tile);
    return { kpi, tile, valueEl: tile.querySelector(".kpi-value") };
  });

  getData(CONFIG.overview)
    .then(({ rows, mock }) => {
      const row = rows[0] || {};
      tiles.forEach(({ kpi, tile, valueEl }) => {
        const raw = row[kpi.field];
        valueEl.textContent = raw === undefined || raw === null ? "—" : (fmt[kpi.format] || fmt.num)(raw);
        if (mock) tile.classList.add("is-mock");
      });
      if (row.first_date && row.last_date) {
        period.textContent = `Delivered orders from ${fmt.date(row.first_date)} to ${fmt.date(row.last_date)}.`;
      }
    })
    .catch((err) => {
      tiles.forEach(({ tile, valueEl }) => {
        valueEl.textContent = "error";
        valueEl.title = err.message;
        tile.classList.add("is-error");
      });
      period.textContent = `Couldn't load the summary: ${err.message}`;
    });
})();
