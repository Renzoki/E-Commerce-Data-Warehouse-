(function () {
  const { fact, tables } = CONFIG.schema;
  const star = document.getElementById("star");
  const dims = Object.keys(tables).filter((t) => t !== fact);

  function tableCard(name, isFact) {
    const cols = tables[name].map((c) => `
      <li>
        <span class="col-name">${c.pk ? `<b class="key pk">PK</b>` : c.fk ? `<b class="key fk">FK</b>` : ""}${escapeHtml(c.name)}</span>
        <span class="col-type">${escapeHtml(c.type)}${c.fk ? ` → <a href="#t-${c.fk}">${escapeHtml(c.fk)}</a>` : ""}</span>
      </li>`).join("");
    const idx = CONFIG.datasets.findIndex((d) => d.id === name);
    return `
      <section class="card schema-table ${isFact ? "is-fact" : ""}" id="t-${name}">
        <header>
          <h2>${escapeHtml(name)}</h2>
          <span class="muted">${isFact ? "fact" : "dimension"} · ${tables[name].length} cols</span>
        </header>
        <ul>${cols}</ul>
        ${idx >= 0 ? `<a class="browse-link" href="browse.html?table=${encodeURIComponent(name)}">Browse rows →</a>` : ""}
      </section>`;
  }

  // dims in the four corners, fact in the middle (stacks on small screens)
  star.innerHTML =
    tableCard(dims[0], false) +
    tableCard(dims[1], false) +
    tableCard(fact, true) +
    dims.slice(2).map((d) => tableCard(d, false)).join("");
})();
