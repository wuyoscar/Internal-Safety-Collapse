// ISC-Bench — static website interactions

function updateStaticArenaStats() {
  const rows = Array.from(document.querySelectorAll("#leaderboard-body tr"));
  const trackedEl = document.getElementById("tracked-count");
  if (trackedEl) trackedEl.textContent = `${rows.length} confirmed models`;

  const subtitle = document.querySelector("#arena .subtitle");
  if (subtitle) {
    subtitle.innerHTML = `Static evidence table with <strong>${rows.length}</strong> confirmed frontier-model cases.<br>Every row links to archived evidence.`;
  }
}

function setupArenaSearch() {
  const searchInput = document.getElementById("arenaSearch");
  const rows = Array.from(document.querySelectorAll("#leaderboard-body tr"));
  if (!searchInput || !rows.length) return;

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase().trim();
    rows.forEach(row => {
      const haystack = `${row.dataset.name || ""} ${row.textContent || ""}`.toLowerCase();
      row.style.display = !query || haystack.includes(query) ? "" : "none";
    });
  });
}

// ====== Nav ======
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".navbar-burger").forEach(el => {
    el.addEventListener("click", () => {
      const target = document.getElementById(el.dataset.target);
      el.classList.toggle("is-active");
      if (target) target.classList.toggle("is-active");
    });
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); });
  }, { threshold: 0.1 });
  document.querySelectorAll(".fade-in").forEach(el => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
    observer.observe(el);
  });

  window.copyBibtex = function() {
    const node = document.getElementById("bibtex");
    if (!node) return;
    navigator.clipboard.writeText(node.textContent).then(() => {
      const btn = document.querySelector(".copy-btn span:last-child");
      if (btn) {
        btn.textContent = "Copied!";
        setTimeout(() => { btn.textContent = "Copy"; }, 2000);
      }
    });
  };

  updateStaticArenaStats();
  setupArenaSearch();
});
