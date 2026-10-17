(function () {
  const grid = document.getElementById("kpis");

  CONFIG.kpis.forEach(async (kpi) => {
    const tile = document.createElement("div");
    tile.className = "card kpi";
    tile.innerHTML = `<span class="kpi-label">${escapeHtml(kpi.label)}</span>
                      <span class="kpi-value">…</span>`;
    grid.append(tile);
    const valueEl = tile.querySelector(".kpi-value");

    try {
      const { rows, mock } = await getData(kpi);
      const raw = rows[0]?.[kpi.field || "value"];
      valueEl.textContent = raw === undefined ? "—" : (fmt[kpi.format] || fmt.num)(raw);
      if (mock) tile.classList.add("is-mock");
    } catch (err) {
      valueEl.textContent = "error";
      valueEl.title = err.message;
      tile.classList.add("is-error");
    }
  });
})();
