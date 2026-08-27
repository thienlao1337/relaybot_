def get_webapp_html() -> str:
    return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tasks</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root {
    color-scheme: light dark;
  }
  body {
    margin: 0;
    padding: 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--tg-theme-bg-color, #ffffff);
    color: var(--tg-theme-text-color, #111111);
  }
  h1 { font-size: 1.15rem; margin: 4px 0 16px; }
  .row {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
  }
  input[type=text] {
    flex: 1;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--tg-theme-hint-color, #cccccc);
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
    color: var(--tg-theme-text-color, #111111);
    font-size: 0.95rem;
  }
  button {
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    background: var(--tg-theme-button-color, #2ea6ff);
    color: var(--tg-theme-button-text-color, #ffffff);
    font-size: 0.95rem;
    cursor: pointer;
  }
  ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
  li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    background: var(--tg-theme-secondary-bg-color, #f4f4f5);
  }
  li span { flex: 1; word-break: break-word; }
  li.done span { text-decoration: line-through; opacity: 0.55; }
  li button {
    background: transparent;
    color: var(--tg-theme-hint-color, #888888);
    padding: 4px 8px;
    font-size: 1rem;
  }
  .empty { color: var(--tg-theme-hint-color, #888888); font-size: 0.9rem; padding: 8px 2px; }
</style>
</head>
<body>
  <h1>📝 Задачі</h1>
  <div class="row">
    <input type="text" id="taskInput" placeholder="Нова задача..." />
    <button id="addBtn">Додати</button>
  </div>
  <ul id="list"></ul>
  <p id="empty" class="empty" style="display:none;">Задач поки немає.</p>

<script>
  const tg = window.Telegram && window.Telegram.WebApp;
  if (tg) { tg.ready(); tg.expand(); }
  const initData = tg ? tg.initData : "";

  async function api(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    opts.headers["X-Telegram-Init-Data"] = initData;
    const res = await fetch(path, opts);
    if (!res.ok) throw new Error("request failed: " + res.status);
    return res.json();
  }

  function render(tasks) {
    const list = document.getElementById("list");
    const empty = document.getElementById("empty");
    list.innerHTML = "";
    empty.style.display = tasks.length ? "none" : "block";
    tasks.forEach(function (task) {
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
  }

  async function loadTasks() {
    try {
      const data = await api("/api/tasks");
      render(data.tasks || []);
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
    await api("/api/tasks", { method: "POST", body: JSON.stringify({ text: text }) });
    if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
    loadTasks();
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

  loadTasks();
</script>
</body>
</html>
"""
