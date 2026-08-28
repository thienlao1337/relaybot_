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
</style>
</head>
<body>
  <h1>Relay</h1>

  <div class="tabs">
    <div class="tab active" data-tab="tasks">📝 Задачі</div>
    <div class="tab" data-tab="weather">🌦 Погода</div>
    <div class="tab" data-tab="currency">💱 Курси</div>
  </div>

  <!-- Tasks -->
  <div class="view active" id="view-tasks">
    <div class="row">
      <input type="text" id="taskInput" placeholder="Нова задача..." />
      <button id="addBtn">Додати</button>
    </div>
    <div class="stats">
      <span id="statsLine">0 з 0 виконано</span>
      <div class="filters">
        <div class="filter active" data-filter="all">Усі</div>
        <div class="filter" data-filter="active">Активні</div>
        <div class="filter" data-filter="done">Виконані</div>
      </div>
    </div>
    <ul id="list"></ul>
    <p id="empty" class="empty" style="display:none;">Задач поки немає.</p>
  </div>

  <!-- Weather -->
  <div class="view" id="view-weather">
    <div class="row">
      <input type="text" id="cityInput" placeholder="Назва міста..." />
      <button id="weatherBtn">OK</button>
    </div>
    <div id="weatherResult"></div>
  </div>

  <!-- Currency -->
  <div class="view" id="view-currency">
    <div class="card" id="currencyResult">
      <p class="empty">Завантаження…</p>
    </div>
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
    document.getElementById("statsLine").textContent = doneCount + " з " + allTasks.length + " виконано";
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
      document.getElementById("empty").textContent = "Не вдалося завантажити задачі.";
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
    result.innerHTML = '<p class="empty">Шукаю…</p>';
    try {
      const data = await api("/api/weather?city=" + encodeURIComponent(city));
      result.innerHTML =
        '<div class="card"><div class="big">' + data.temp + '°C</div>' +
        '<div class="sub">' + data.city + ' · вітер ' + data.wind + ' км/год</div>' +
        '<div class="sub">' + data.desc + '</div></div>';
    } catch (e) {
      result.innerHTML = '<p class="empty">Не знайшов таке місто.</p>';
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
      box.innerHTML = '<p class="empty">Не вдалося завантажити курси.</p>';
    }
  }

  loadTasks();
</script>
</body>
</html>
"""
