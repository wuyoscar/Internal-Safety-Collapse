// ISC-Bench — Frontier LLMs Website
// Auto-fetches data from GitHub repo for real-time updates

const REPO_RAW = "https://raw.githubusercontent.com/wuyoscar/ISC-Bench/main";

// ====== Fallback data (used if fetch fails) ======
const FALLBACK_CASES = {
  "Claude Fable 5": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/claude-fable-5-fake-news", by: "wuyoscar" }] },
  "Claude Opus 4.6": { demos: [{ link: "https://claude.ai/share/407d33f5-4655-4479-b3e3-0a6dc6639d34", by: "wuyoscar" }] },
  "Claude Opus 4.5": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/claudeopus45-share", by: "wuyoscar" }] },
  "Claude Sonnet 4.6": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/claudesonnet46-share", by: "wuyoscar" }] },
  "Gemini 3 Pro": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/issue-13-gemini3pro", by: "wuyoscar" }] },
  "GPT-5.2 Chat": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/issue-29-gpt52chat", by: "wuyoscar" }] },
  "o3": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/o3-share", by: "wuyoscar" }] },
  "Grok 4.1": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/issue-grok41-redacted", by: "wuyoscar" }] },
  "Kimi K2.5 Thinking": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/kimi-k25-thinking-share", by: "wuyoscar" }] },
  "Qwen 3 Max Preview": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/issue-4-qwen3max", by: "wuyoscar" }] },
  "DeepSeek V3.2": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/deepseek-v32-share", by: "wuyoscar" }] },
  "GLM-5": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/glm5-share", by: "wuyoscar" }] },
  "Qwen 3.5 397B": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/issue-3-qwen35397b", by: "HanxunH" }] },
  "Qwen 3 Max 2025-09-23": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/qwen3-max-20250923-share", by: "HanxunH" }] },
  "ERNIE 5.0": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/issue-5-ernie5", by: "HanxunH" }] },
  "Grok 4.1 Thinking": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/grok41fast-guard-attack-v2", by: "wuyoscar" }] },
  "Grok 4.1 Fast Reasoning": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/grok41fast-guard-attack-v2", by: "wuyoscar" }] },
  "Gemini 3 Flash Thinking": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/gemini3flash-guard-attack-v2", by: "wuyoscar" }] },
  "GPT-5.1 High": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/gpt51-guard-attack-v2", by: "wuyoscar" }] },
  "GPT-5.1": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/gpt51-guard-attack-v2", by: "wuyoscar" }] },
  "Claude Opus 4.1": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/claudeopus41-guard-attack-v2", by: "wuyoscar" }] },
  "Claude Opus 4.1 Thinking": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/claudeopus41-guard-attack-v2", by: "wuyoscar" }] },
  "GPT-5.2": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/gpt52-guard-attack-v2", by: "wuyoscar" }] },
  "GPT-5.2 High": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/gpt52-guard-attack-v2", by: "wuyoscar" }] },
  "DeepSeek V3.2 Thinking": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/deepseekv32-guard-attack-v2", by: "wuyoscar" }] },
  "Qwen 3.5 Max Preview": { demos: [{ link: "https://github.com/wuyoscar/ISC-Bench/tree/main/community/qwen35maxpreview-web-share", by: "wuyoscar" }] },
};

// ====== Dynamic Data Fetch ======
async function fetchJSON(path) {
  try {
    const resp = await fetch(`${REPO_RAW}/${path}?t=${Date.now()}`);
    if (!resp.ok) throw new Error(resp.status);
    return await resp.json();
  } catch (e) {
    console.warn(`Failed to fetch ${path}, using fallback:`, e);
    return null;
  }
}

async function loadData() {
  const [arenaData, iscData] = await Promise.all([
    fetchJSON("assets/arena_cache.json"),
    fetchJSON("assets/isc_cases.json"),
  ]);

  const arena = arenaData || [];
  const cases = iscData || FALLBACK_CASES;

  window._allModels = arena;
  window._allCases = cases;
  window._currentPage = 1;
  window._perPage = 25;
  renderPage(1, arena, cases);
  populateDemos(cases);
  updateStats(arena, cases);
}

// ====== Pagination ======
function renderPage(page, models, cases) {
  const perPage = window._perPage;
  const start = (page - 1) * perPage;
  const end = start + perPage;
  const pageModels = models.slice(start, end);
  window._currentPage = page;
  populateLeaderboard(pageModels, cases);
  renderPagination(models.length, perPage, page);
}

function renderPagination(total, perPage, current) {
  const totalPages = Math.ceil(total / perPage);
  let container = document.getElementById("pagination-nav");
  if (!container) {
    container = document.createElement("nav");
    container.id = "pagination-nav";
    container.className = "pagination is-centered is-small mt-4";
    container.setAttribute("role", "navigation");
    const tableContainer = document.querySelector(".table-container");
    if (tableContainer) tableContainer.parentNode.insertBefore(container, tableContainer.nextSibling);
  }

  let html = '<ul class="pagination-list">';

  // Previous
  if (current > 1) {
    html += `<li><a class="pagination-link" onclick="renderPage(${current-1}, window._allModels, window._allCases)">&laquo;</a></li>`;
  }

  // Page numbers
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= current - 2 && i <= current + 2)) {
      html += `<li><a class="pagination-link ${i === current ? 'is-current' : ''}" onclick="renderPage(${i}, window._allModels, window._allCases)">${i}</a></li>`;
    } else if (i === current - 3 || i === current + 3) {
      html += '<li><span class="pagination-ellipsis">&hellip;</span></li>';
    }
  }

  // Next
  if (current < totalPages) {
    html += `<li><a class="pagination-link" onclick="renderPage(${current+1}, window._allModels, window._allCases)">&raquo;</a></li>`;
  }

  html += '</ul>';
  container.innerHTML = html;
}

// ====== Leaderboard ======
function populateLeaderboard(models, cases) {
  const tbody = document.getElementById("leaderboard-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  models.forEach(model => {
    const displayName = slugToDisplay(model.name);
    const isc = cases[displayName];
    const tr = document.createElement("tr");

    let statusHTML, demoHTML = "", byHTML = "";
    if (isc) {
      statusHTML = '<span class="badge-jailbroken"><i class="fas fa-unlock"></i> Triggered</span>';
      demoHTML = isc.demos.map((d, i) =>
        `<a href="${d.link}" target="_blank" title="View conversation">🔗${isc.demos.length > 1 ? `₊${i+1}` : ""}</a>`
      ).join(" ");
      byHTML = isc.demos.map(d =>
        `<a href="https://github.com/${d.by}" target="_blank">@${d.by}</a>`
      ).join("<br>");
    } else {
      statusHTML = '<span class="badge-safe"><i class="fas fa-hourglass-half"></i> Pending</span>';
    }

    tr.innerHTML = `
      <td><span class="model-name">${displayName}</span><span class="model-org">${model.org}</span></td>
      <td class="has-text-centered">${statusHTML}</td>
      <td class="has-text-centered">${demoHTML}</td>
      <td class="has-text-centered">${byHTML}</td>
    `;
    tr.dataset.name = displayName.toLowerCase();
    tr.dataset.status = isc ? "jailbroken" : "safe";
    tbody.appendChild(tr);
  });
}

// ====== Demo Cards (Marquee) ======
function populateDemos(cases) {
  const container = document.getElementById("demo-grid");
  if (!container) return;
  container.innerHTML = "";

  const favicons = {
    "claude": "anthropic.com", "gemini": "google.com", "gpt": "openai.com", "chatgpt": "openai.com",
    "grok": "x.ai", "kimi": "moonshot.ai", "qwen": "alibabacloud.com", "deepseek": "deepseek.com",
    "glm": "z.ai", "ernie": "baidu.com", "o3": "openai.com", "dola": "volcengine.com",
  };

  // Build card HTML
  function makeCard(name, data) {
    const demo = data.demos[0];
    const key = Object.keys(favicons).find(k => name.toLowerCase().includes(k)) || "";
    const domain = favicons[key] || "";
    const icon = domain
      ? `<img src="https://www.google.com/s2/favicons?domain=${domain}&sz=32" width="20" style="vertical-align:middle;border-radius:3px;">`
      : "🤖";
    return `<div class="demo-card">
      <div class="demo-icon">${icon}</div>
      <div class="demo-info"><h4>${name}</h4><p>by @${demo.by}</p></div>
      <a href="${demo.link}" target="_blank" class="demo-link">View →</a>
    </div>`;
  }

  const entries = Object.entries(cases);
  const mid = Math.ceil(entries.length / 2);
  const row1Items = entries.slice(0, mid);
  const row2Items = entries.slice(mid);

  // Create two marquee rows
  [row1Items, row2Items].forEach(items => {
    const row = document.createElement("div");
    row.className = "marquee-row";
    const inner = document.createElement("div");
    inner.className = "marquee-inner";
    // Original + duplicate for seamless loop
    const cardsHTML = items.map(([n, d]) => makeCard(n, d)).join("");
    inner.innerHTML = cardsHTML + cardsHTML;
    row.appendChild(inner);
    container.appendChild(row);
  });
}

// ====== Update Stats ======
function updateStats(arena, cases) {
  // Count only tracked Arena models that are triggered — matches the leaderboard
  // rows and the static badge (not the raw isc_cases key count, which includes
  // historical entries no longer in the Arena).
  const confirmed = arena.filter(m => cases[slugToDisplay(m.name)]).length;
  const total = arena.length || 100;

  // Footer "<N> models tracked" — driven by data, no hardcoded count
  const trackedEl = document.getElementById("tracked-count");
  if (trackedEl) trackedEl.textContent = `${total} models`;

  // Update arena subtitle
  const subtitle = document.querySelector("#arena .subtitle");
  if (subtitle) {
    subtitle.innerHTML = `Tracking ISC across <strong>${total}</strong> frontier models.
      Every <span class="has-text-danger">red dot</span> is a confirmed case.
      <strong class="has-text-danger">${confirmed}</strong> triggered so far.`;
  }
}

// ====== Search + Filter ======
function setupSearch() {
  const searchInput = document.getElementById("arenaSearch");
  const filterSelect = document.getElementById("arenaFilter");
  if (!searchInput || !filterSelect) return;

  function applyFilter() {
    const query = searchInput.value.toLowerCase();
    const filter = filterSelect.value;
    const allModels = window._allModels || [];
    const cases = window._allCases || {};

    const filtered = allModels.filter(m => {
      const name = slugToDisplay(m.name).toLowerCase();
      const isc = cases[slugToDisplay(m.name)];
      const nameMatch = name.includes(query) || m.org.toLowerCase().includes(query);
      const statusMatch = filter === "all" || (filter === "jailbroken" && isc) || (filter === "safe" && !isc);
      return nameMatch && statusMatch;
    });

    window._filteredModels = filtered;
    window._currentPage = 1;
    populateLeaderboard(filtered.slice(0, window._perPage), cases);
    renderPagination(filtered.length, window._perPage, 1);
  }

  // Override renderPage to use filtered if available
  const origRenderPage = window.renderPage;
  window.renderPage = function(page, models, cases) {
    const src = window._filteredModels || models;
    const perPage = window._perPage;
    const start = (page - 1) * perPage;
    populateLeaderboard(src.slice(start, start + perPage), cases);
    renderPagination(src.length, perPage, page);
    window._currentPage = page;
  };

  searchInput.addEventListener("input", applyFilter);
  filterSelect.addEventListener("change", applyFilter);
}

// ====== Name Conversion ======
const DISPLAY_NAMES = {
  "mistral-large": "Mistral Large",
  "amazon-nova-pro": "Amazon Nova Pro",
  "llama-4-scout": "Llama 4 Scout",
  "claude-opus-4-8": "Claude Opus 4.8",
  "claude-opus-4-7-thinking": "Claude Opus 4.7",
  "claude-opus-4-6-thinking": "Claude Opus 4.6",
  "gemini-3.1-pro-preview": "Gemini 3.1 Pro",
  "grok-4.20-beta1": "Grok 4.20",
  "kimi-k2.6": "Kimi K2.6",
  "gemini-3-pro": "Gemini 3 Pro",
  "gpt-5.4-high": "GPT-5.4",
  "gpt-5.2-chat-latest-20260210": "GPT-5.2",
  "gemini-3-flash": "Gemini 3 Flash",
  "claude-opus-4-5-20251101-thinking-32k": "Claude Opus 4.5",
  "grok-4.1-thinking": "Grok 4.1",
  "claude-sonnet-4-6": "Claude Sonnet 4.6",
  "qwen3.5-max-preview": "Qwen3.5 Max",
  "gpt-5.3-chat-latest": "GPT-5.3",
  "dola-seed-2.0-preview": "Dola Seed 2.0",
  "gpt-5.1-high": "GPT-5.1",
  "glm-5": "GLM-5",
  "kimi-k2.5-thinking": "Kimi K2.5",
  "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
  "ernie-5.0-0110": "ERNIE 5.0",
  "qwen3.5-397b-a17b": "Qwen3.5 397B",
  "claude-opus-4-1-20250805-thinking-16k": "Claude Opus 4.1",
  "gemini-2.5-pro": "Gemini 2.5 Pro",
  "mimo-v2-pro": "Mimo V2 Pro",
  "gpt-4.5-preview-2025-02-27": "GPT-4.5",
  "chatgpt-4o-latest-20250326": "ChatGPT-4o",
  "glm-4.7": "GLM-4.7",
  "gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash Lite",
  "qwen3-max-preview": "Qwen3 Max",
  "gpt-5-high": "GPT-5",
  "o3-2025-04-16": "o3",
  "kimi-k2-thinking-turbo": "Kimi K2",
  "amazon-nova-experimental-chat-26-02-10": "Amazon Nova Experimental",
  "glm-4.6": "GLM-4.6",
  "deepseek-v3.2-exp-thinking": "DeepSeek V3.2",
  "claude-opus-4-20250514-thinking-16k": "Claude Opus 4",
  "qwen3-235b-a22b-instruct-2507": "Qwen3 235B",
  "deepseek-r1-0528": "DeepSeek R1",
  "grok-4-fast-chat": "Grok 4",
  "deepseek-v3.1": "DeepSeek V3.1",
  "qwen3.5-122b-a10b": "Qwen3.5 122B",
  "deepseek-v3.1-terminus-thinking": "DeepSeek V3.1 Terminus",
  "mistral-large-3": "Mistral Large 3",
  "qwen3-vl-235b-a22b-instruct": "Qwen3 VL 235B",
  "gpt-4.1-2025-04-14": "GPT-4.1",
  "grok-3-preview-02-24": "Grok 3",
  "gemini-2.5-flash": "Gemini 2.5 Flash",
  "glm-4.5": "GLM-4.5",
  "mistral-medium-2508": "Mistral Medium",
  "minimax-m2.7": "MiniMax M2.7",
  "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
  "qwen3.5-27b": "Qwen3.5 27B",
  "minimax-m2.5": "MiniMax M2.5",
  "o1-2024-12-17": "o1",
  "qwen3-next-80b-a3b-instruct": "Qwen3 Next 80B",
  "qwen3.5-flash": "Qwen3.5 Flash",
  "qwen3.5-35b-a3b": "Qwen3.5 35B",
  "longcat-flash-chat": "LongCat Flash",
  "claude-sonnet-4-20250514-thinking-32k": "Claude Sonnet 4",
  "hunyuan-vision-1.5-thinking": "Hunyuan Vision 1.5",
  "deepseek-v3-0324": "DeepSeek V3",
  "mai-1-preview": "MAI-1",
  "mimo-v2-flash (non-thinking)": "Mimo V2 Flash",
  "o4-mini-2025-04-16": "o4-mini",
  "gpt-5-mini-high": "GPT-5 Mini",
  "step-3.5-flash": "Step 3.5 Flash",
};

function slugToDisplay(slug) {
  return DISPLAY_NAMES[slug] || slug.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

// ====== Nav ======
document.addEventListener("DOMContentLoaded", () => {
  // Burger menu toggle
  document.querySelectorAll(".navbar-burger").forEach(el => {
    el.addEventListener("click", () => {
      const target = document.getElementById(el.dataset.target);
      el.classList.toggle("is-active");
      target.classList.toggle("is-active");
    });
  });

  // Scroll animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); });
  }, { threshold: 0.1 });
  document.querySelectorAll(".fade-in").forEach(el => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
    observer.observe(el);
  });

  // Copy BibTeX
  window.copyBibtex = function() {
    const text = document.getElementById("bibtex").textContent;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.querySelector(".copy-btn span:last-child");
      if (btn) { btn.textContent = "Copied!"; setTimeout(() => { btn.textContent = "Copy"; }, 2000); }
    });
  };

  // Load data + search
  loadData().then(() => setupSearch());
});
