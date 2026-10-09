def get_webapp_html() -> str:
    return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relay</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 14px 14px 24px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--tg-theme-bg-color, #ffffff);
    color: var(--tg-theme-text-color, #111111);
  }
  h1 { font-size: 1.05rem; margin: 4px 0 14px; opacity: 0.9; }

  .tabs {
    display: flex;
    gap: 6px;
    margin-bottom: 16px;
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    border-radius: 12px;
    padding: 4px;
  }
  .tab {
    flex: 1;
    text-align: center;
    padding: 9px 6px;
    border-radius: 9px;
    font-size: 0.86rem;
    cursor: pointer;
    color: var(--tg-theme-hint-color, #888888);
    user-select: none;
  }
  .tab.active {
    background: var(--tg-theme-button-color, #2ea6ff);
    color: var(--tg-theme-button-text-color, #ffffff);
  }

  .view { display: none; }
  .view.active { display: block; }

  .row { display: flex; gap: 8px; margin-bottom: 14px; }
  input[type=text] {
    flex: 1;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--tg-theme-hint-color, #cccccc);
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    color: var(--tg-theme-text-color, #111111);
    font-size: 0.95rem;
    min-width: 0;
  }
  button {
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    background: var(--tg-theme-button-color, #2ea6ff);
    color: var(--tg-theme-button-text-color, #ffffff);
    font-size: 0.95rem;
    cursor: pointer;
    white-space: nowrap;
  }
  button:disabled { opacity: 0.55; }

  .stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.82rem;
    color: var(--tg-theme-hint-color, #888888);
    margin-bottom: 10px;
  }
  .filters { display: flex; gap: 6px; }
  .filter {
    padding: 4px 10px;
    border-radius: 999px;
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    cursor: pointer;
    font-size: 0.78rem;
  }
  .filter.active { background: var(--tg-theme-button-color, #2ea6ff); color: var(--tg-theme-button-text-color, #fff); }

  ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
  li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    animation: fade-in 0.15s ease;
  }
  @keyframes fade-in { from { opacity: 0; transform: translateY(-3px); } to { opacity: 1; transform: none; } }
  li span { flex: 1; word-break: break-word; }
  li.done span { text-decoration: line-through; opacity: 0.55; }
  li button { background: transparent; color: var(--tg-theme-hint-color, #888888); padding: 4px 8px; font-size: 1rem; }
  .empty { color: var(--tg-theme-hint-color, #888888); font-size: 0.9rem; padding: 8px 2px; }

  .card {
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    border-radius: 12px;
    padding: 16px;
    margin-top: 4px;
  }
  .card .big { font-size: 1.8rem; font-weight: 600; }
  .card .sub { color: var(--tg-theme-hint-color, #888888); font-size: 0.85rem; margin-top: 4px; }
  .rate-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 0.98rem; }
  .rate-row + .rate-row { border-top: 1px solid var(--tg-theme-bg-color, #ffffff); }

  .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
  .stat-card { background: var(--tg-theme-secondary-bg-color, #f4f4f5); border-radius: 12px; padding: 12px 14px; }
  .stat-card .num { font-size: 1.5rem; font-weight: 600; }
  .stat-card .label { color: var(--tg-theme-hint-color, #888888); font-size: 0.78rem; margin-top: 2px; }
  textarea {
    width: 100%;
    min-height: 90px;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--tg-theme-hint-color, #cccccc);
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    color: var(--tg-theme-text-color, #111111);
    font-size: 0.95rem;
    font-family: inherit;
    resize: vertical;
    margin-bottom: 10px;
  }
  .msg { font-size: 0.85rem; margin-top: 8px; color: var(--tg-theme-hint-color, #888888); }
</style>
</head>
<body>
  <h1>Relay</h1>

  <div class="tabs">
    <div class="tab active" data-tab="tasks" data-i18n="tab_tasks">📝 Tasks</div>
    <div class="tab" data-tab="weather" data-i18n="tab_weather">🌦 Weather</div>
    <div class="tab" data-tab="currency" data-i18n="tab_currency">💱 Rates</div>
    <div class="tab" data-tab="admin" id="adminTab" style="display:none;">🛠 Admin</div>
  </div>

  <!-- Tasks -->
  <div class="view active" id="view-tasks">
    <div class="row">
      <input type="text" id="taskInput" data-i18n-placeholder="task_placeholder" placeholder="New task..." />
      <button id="addBtn" data-i18n="add">Add</button>
    </div>
    <div class="stats">
      <span id="statsLine">0 of 0 done</span>
      <div class="filters">
        <div class="filter active" data-filter="all" data-i18n="filter_all">All</div>
        <div class="filter" data-filter="active" data-i18n="filter_active">Active</div>
        <div class="filter" data-filter="done" data-i18n="filter_done">Done</div>
      </div>
    </div>
    <ul id="list"></ul>
    <p id="empty" class="empty" style="display:none;" data-i18n="no_tasks">No tasks yet.</p>
  </div>

  <!-- Weather -->
  <div class="view" id="view-weather">
    <div class="row">
      <input type="text" id="cityInput" data-i18n-placeholder="city_placeholder" placeholder="City name..." />
      <button id="weatherBtn">OK</button>
    </div>
    <div id="weatherResult"></div>
  </div>

  <!-- Currency -->
  <div class="view" id="view-currency">
    <div class="card" id="currencyResult">
      <p class="empty" data-i18n="loading">Loading…</p>
    </div>
  </div>

  <!-- Admin (hidden unless /api/me says is_admin) -->
  <div class="view" id="view-admin">
    <div class="stat-grid" id="statGrid">
      <div class="stat-card"><div class="num">—</div><div class="label">users</div></div>
      <div class="stat-card"><div class="num">—</div><div class="label">tasks (active/done)</div></div>
      <div class="stat-card"><div class="num">—</div><div class="label">active alerts</div></div>
      <div class="stat-card"><div class="num">—</div><div class="label">by language</div></div>
    </div>
    <textarea id="broadcastText" placeholder="Broadcast message to all users..."></textarea>
    <button id="broadcastBtn">Send broadcast</button>
    <p class="msg" id="broadcastMsg"></p>
  </div>

<script>
  const tg = window.Telegram && window.Telegram.WebApp;
  if (tg) { tg.ready(); tg.expand(); }
  const initData = tg ? tg.initData : "";

  async function api(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    opts.headers["X-Telegram-Init-Data"] = initData;
    const res = await fetch(path, opts);
    const data = await res.json().catch(function () { return {}; });
    if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
    return data;
  }

  // ---------- i18n (follows the language chosen in the bot) ----------
  const I18N = {
    en: {
      tab_tasks: "📝 Tasks", tab_weather: "🌦 Weather", tab_currency: "💱 Rates",
      task_placeholder: "New task...", add: "Add",
      filter_all: "All", filter_active: "Active", filter_done: "Done",
      no_tasks: "No tasks yet.", tasks_failed: "Couldn't load tasks.",
      stats: "{done} of {total} done",
      city_placeholder: "City name...", searching: "Searching…",
      wind: "wind {wind} km/h", city_not_found: "City not found.",
      loading: "Loading…", rates_failed: "Couldn't load exchange rates."
    },
    ua: {
      tab_tasks: "📝 Задачі", tab_weather: "🌦 Погода", tab_currency: "💱 Курси",
      task_placeholder: "Нова задача...", add: "Додати",
      filter_all: "Усі", filter_active: "Активні", filter_done: "Виконані",
      no_tasks: "Задач поки немає.", tasks_failed: "Не вдалося завантажити задачі.",
      stats: "{done} з {total} виконано",
      city_placeholder: "Назва міста...", searching: "Шукаю…",
      wind: "вітер {wind} км/год", city_not_found: "Не знайшов таке місто.",
      loading: "Завантаження…", rates_failed: "Не вдалося завантажити курси."
    },
    ru: {
      tab_tasks: "📝 Задачи", tab_weather: "🌦 Погода", tab_currency: "💱 Курсы",
      task_placeholder: "Новая задача...", add: "Добавить",
      filter_all: "Все", filter_active: "Активные", filter_done: "Выполненные",
      no_tasks: "Задач пока нет.", tasks_failed: "Не удалось загрузить задачи.",
      stats: "{done} из {total} выполнено",
      city_placeholder: "Название города...", searching: "Ищу…",
      wind: "ветер {wind} км/ч", city_not_found: "Не нашёл такой город.",
      loading: "Загрузка…", rates_failed: "Не удалось загрузить курсы."
    }
  };
  let lang = "en";

  function tr(key, vars) {
    let s = (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
    Object.keys(vars || {}).forEach(function (k) { s = s.replace("{" + k + "}", vars[k]); });
    return s;
  }

  function applyLang(newLang) {
    if (!I18N[newLang]) return;
    lang = newLang;
    document.documentElement.lang = lang === "ua" ? "uk" : lang;
    document.querySelectorAll("[data-i18n]").forEach(function (el) { el.textContent = tr(el.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) { el.placeholder = tr(el.dataset.i18nPlaceholder); });
    renderTasks();
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---------- tabs ----------
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach(function (tabEl) {
    tabEl.addEventListener("click", function () {
      tabs.forEach(function (t) { t.classList.remove("active"); });
      document.querySelectorAll(".view").forEach(function (v) { v.classList.remove("active"); });
      tabEl.classList.add("active");
      document.getElementById("view-" + tabEl.dataset.tab).classList.add("active");
      if (tg && tg.HapticFeedback) tg.HapticFeedback.selectionChanged();
      if (tabEl.dataset.tab === "currency") loadCurrency();
      if (tabEl.dataset.tab === "admin") loadAdminStats();
    });
  });

  // ---------- tasks ----------
  let allTasks = [];
  let currentFilter = "all";

  function renderTasks() {
    const list = document.getElementById("list");
    const empty = document.getElementById("empty");
    const filtered = allTasks.filter(function (t) {
      if (currentFilter === "active") return !t.done;
      if (currentFilter === "done") return t.done;
      return true;
    });
    list.innerHTML = "";
    empty.style.display = filtered.length ? "none" : "block";
    filtered.forEach(function (task) {
      const li = document.createElement("li");
      if (task.done) li.className = "done";
      const span = document.createElement("span");
      span.textContent = task.text;
      const doneBtn = document.createElement("button");
      doneBtn.textContent = "✔️";
      doneBtn.onclick = function () { toggleTask(task.id); };
      const delBtn = document.createElement("button");
      delBtn.textContent = "🗑";
      delBtn.onclick = function () { deleteTask(task.id); };
      li.appendChild(span);
      li.appendChild(doneBtn);
      li.appendChild(delBtn);
      list.appendChild(li);
    });
    const doneCount = allTasks.filter(function (t) { return t.done; }).length;
    document.getElementById("statsLine").textContent = tr("stats", { done: doneCount, total: allTasks.length });
  }

  document.querySelectorAll(".filter").forEach(function (f) {
    f.addEventListener("click", function () {
      document.querySelectorAll(".filter").forEach(function (x) { x.classList.remove("active"); });
      f.classList.add("active");
      currentFilter = f.dataset.filter;
      renderTasks();
    });
  });

  async function loadTasks() {
    try {
      const data = await api("/api/tasks");
      allTasks = data.tasks || [];
      renderTasks();
    } catch (e) {
      document.getElementById("empty").textContent = tr("tasks_failed");
      document.getElementById("empty").style.display = "block";
    }
  }

  async function addTask() {
    const input = document.getElementById("taskInput");
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    document.getElementById("addBtn").disabled = true;
    try {
      await api("/api/tasks", { method: "POST", body: JSON.stringify({ text: text }) });
      if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
      await loadTasks();
    } finally {
      document.getElementById("addBtn").disabled = false;
    }
  }

  async function toggleTask(id) {
    await api("/api/tasks/" + id + "/toggle", { method: "POST" });
    loadTasks();
  }

  async function deleteTask(id) {
    await api("/api/tasks/" + id, { method: "DELETE" });
    loadTasks();
  }

  document.getElementById("addBtn").addEventListener("click", addTask);
  document.getElementById("taskInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") addTask();
  });

  // ---------- weather ----------
  async function loadWeather() {
    const city = document.getElementById("cityInput").value.trim();
    const result = document.getElementById("weatherResult");
    if (!city) return;
    result.innerHTML = '<p class="empty">' + tr("searching") + '</p>';
    try {
      const data = await api("/api/weather?city=" + encodeURIComponent(city));
      result.innerHTML =
        '<div class="card"><div class="big">' + escapeHtml(data.temp) + '°C</div>' +
        '<div class="sub">' + escapeHtml(data.city) + ' · ' + escapeHtml(tr("wind", { wind: data.wind })) + '</div>' +
        '<div class="sub">' + escapeHtml(data.desc) + '</div></div>';
    } catch (e) {
      result.innerHTML = '<p class="empty">' + tr("city_not_found") + '</p>';
    }
  }
  document.getElementById("weatherBtn").addEventListener("click", loadWeather);
  document.getElementById("cityInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") loadWeather();
  });

  // ---------- currency ----------
  let currencyLoaded = false;
  async function loadCurrency() {
    if (currencyLoaded) return;
    const box = document.getElementById("currencyResult");
    try {
      const data = await api("/api/currency");
      box.innerHTML =
        '<div class="rate-row"><span>1 USD</span><span>' + data.usd.toFixed(2) + ' ₴</span></div>' +
        '<div class="rate-row"><span>1 EUR</span><span>' + data.eur.toFixed(2) + ' ₴</span></div>';
      currencyLoaded = true;
    } catch (e) {
      box.innerHTML = '<p class="empty">' + tr("rates_failed") + '</p>';
    }
  }

  // ---------- admin ----------
  async function checkAdmin() {
    try {
      const data = await api("/api/me");
      if (data.lang) applyLang(data.lang);
      if (data.is_admin) document.getElementById("adminTab").style.display = "";
    } catch (e) { /* not authenticated or not admin - tab stays hidden */ }
  }

  let adminStatsLoaded = false;
  async function loadAdminStats() {
    if (adminStatsLoaded) return;
    try {
      const s = await api("/api/admin/stats");
      const cards = document.querySelectorAll("#statGrid .stat-card .num");
      const byLang = Object.entries(s.by_lang || {}).map(function (e) { return e[0] + ":" + e[1]; }).join(" ") || "—";
      cards[0].textContent = s.total_users;
      cards[1].textContent = s.active_tasks + "/" + s.done_tasks;
      cards[2].textContent = s.active_watchers;
      cards[3].textContent = byLang;
      adminStatsLoaded = true;
    } catch (e) {
      document.getElementById("broadcastMsg").textContent = "Failed to load stats.";
    }
  }

  document.getElementById("broadcastBtn").addEventListener("click", async function () {
    const textEl = document.getElementById("broadcastText");
    const msgEl = document.getElementById("broadcastMsg");
    const text = textEl.value.trim();
    if (!text) return;
    const btn = document.getElementById("broadcastBtn");
    btn.disabled = true;
    msgEl.textContent = "Sending…";
    try {
      const res = await api("/api/admin/broadcast", { method: "POST", body: JSON.stringify({ text: text }) });
      msgEl.textContent = "Sent to " + res.sent + " / " + res.total + " users.";
      textEl.value = "";
      if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
    } catch (e) {
      msgEl.textContent = "Failed to send broadcast.";
    } finally {
      btn.disabled = false;
    }
  });

  checkAdmin();
  loadTasks();
</script>
</body>
</html>
"""
