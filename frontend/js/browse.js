(function () {
  const el = (id) => document.getElementById(id);
  const datasetSel = el("dataset");
  const search = el("search");
  const pageSizeSel = el("pageSize");
  const tableEl = el("table");

  const state = {
    dataset: CONFIG.datasets[0],
    q: "",
    sort: null,
    order: "asc",
    page: 0,
    pageSize: +pageSizeSel.value,
    cache: null, // all rows, for client-side datasets
  };

  CONFIG.datasets.forEach((d, i) =>
    datasetSel.insertAdjacentHTML("beforeend", `<option value="${i}">${escapeHtml(d.label)}</option>`));

  // open a specific table from a link like browse.html?table=dim_product
  const wanted = new URLSearchParams(location.search).get("table");
  const wantedIdx = CONFIG.datasets.findIndex((d) => d.id === wanted);
  if (wantedIdx >= 0) {
    state.dataset = CONFIG.datasets[wantedIdx];
    datasetSel.value = String(wantedIdx);
  }

  // ---------- client-side search / sort / paging ----------
  function clientView(rows) {
    let out = rows;
    if (state.q) {
      const q = state.q.toLowerCase();
      out = out.filter((r) => Object.values(r).some((v) => String(v ?? "").toLowerCase().includes(q)));
    }
    if (state.sort) {
      const k = state.sort, dir = state.order === "desc" ? -1 : 1;
      out = [...out].sort((a, b) =>
        (a[k] > b[k] ? 1 : a[k] < b[k] ? -1 : 0) * dir);
    }
    const start = state.page * state.pageSize;
    return { rows: out.slice(start, start + state.pageSize), total: out.length };
  }

  async function load() {
    tableEl.innerHTML = `<p class="empty">Loading…</p>`;
    const d = state.dataset;
    const serverMode = d.server && !isMock(d);

    try {
      let view, mock;
      if (serverMode) {
        // backend does the work: ?q=&sort=&order=&limit=&offset=
        const res = await getData(d, {
          q: state.q, sort: state.sort, order: state.order,
          limit: state.pageSize, offset: state.page * state.pageSize,
        });
        view = res; mock = res.mock;
      } else {
        if (!state.cache) state.cache = await getData(d);
        view = clientView(state.cache.rows); mock = state.cache.mock;
      }

      renderTable(tableEl, view.rows, { onSort, sort: state.sort, order: state.order });
      const pages = Math.max(1, Math.ceil(view.total / state.pageSize));
      el("count").textContent = `${fmt.int(view.total)} row${view.total === 1 ? "" : "s"}`;
      el("pageInfo").textContent = `Page ${state.page + 1} of ${pages}`;
      el("prev").disabled = state.page === 0;
      el("next").disabled = state.page + 1 >= pages;
      el("mockNote").hidden = !mock;
    } catch (err) {
      showError(tableEl, err);
    }
  }

  function onSort(col) {
    state.order = state.sort === col && state.order === "asc" ? "desc" : "asc";
    state.sort = col;
    state.page = 0;
    load();
  }

  // ---------- events ----------
  datasetSel.addEventListener("change", () => {
    Object.assign(state, {
      dataset: CONFIG.datasets[+datasetSel.value], cache: null, sort: null, page: 0,
    });
    load();
  });

  let t;
  search.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(() => { state.q = search.value.trim(); state.page = 0; load(); }, 300);
  });

  pageSizeSel.addEventListener("change", () => {
    state.pageSize = +pageSizeSel.value; state.page = 0; load();
  });
  el("prev").addEventListener("click", () => { state.page--; load(); });
  el("next").addEventListener("click", () => { state.page++; load(); });

  load();
})();
