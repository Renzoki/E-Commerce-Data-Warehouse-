// Injects the shared header/footer so the nav lives in one place.

const NAV = [
  { href: "index.html",   label: "Overview" },
  { href: "browse.html",  label: "Browse" },
  { href: "reports.html", label: "Reports" },
  { href: "schema.html",  label: "Schema" },
];

(function renderLayout() {
  const page = location.pathname.split("/").pop() || "index.html";

  const header = document.createElement("header");
  header.className = "site-header";
  header.innerHTML = `
    <div class="container header-inner">
      <a class="brand" href="index.html">E-Commerce DW</a>
      <nav>${NAV.map((n) =>
        `<a href="${n.href}" class="${n.href === page ? "active" : ""}">${n.label}</a>`).join("")}
      </nav>
    </div>`;
  document.body.prepend(header);

  const footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.innerHTML = `
    <div class="container footer-inner">
      <span><span id="api-dot" class="dot"></span> API: <span id="api-status">checking…</span></span>
      ${CONFIG.USE_MOCK ? `<span class="badge">Mock data on</span>` : ""}
    </div>`;
  document.body.append(footer);

  // ping /health
  const dot = footer.querySelector("#api-dot");
  const status = footer.querySelector("#api-status");
  fetchJson(CONFIG.HEALTH_ENDPOINT)
    .then(() => { dot.classList.add("ok"); status.textContent = `online (${apiBase()})`; })
    .catch(() => { dot.classList.add("down"); status.textContent = `offline (${apiBase()})`; });
})();
