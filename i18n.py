TEXT = {
    "welcome": {
        "ua": "Привіт, {name}! Я демонстраційний бот для портфоліо — вмію трохи більше, ніж просто відповідати на /start.\n\nОберіть, що показати:",
        "en": "Hi, {name}! I'm a portfolio demo bot — I do a bit more than just reply to /start.\n\nPick something to try:",
        "ru": "Привет, {name}! Я демонстрационный бот для портфолио — умею чуть больше, чем просто отвечать на /start.\n\nВыберите, что показать:",
    },
    "menu_tasks": {"ua": "📝 Задачі", "en": "📝 Tasks", "ru": "📝 Задачи"},
    "menu_weather": {"ua": "🌦 Погода", "en": "🌦 Weather", "ru": "🌦 Погода"},
    "menu_currency": {"ua": "💱 Курси валют", "en": "💱 Exchange rates", "ru": "💱 Курсы валют"},
    "menu_lang": {"ua": "🌐 Мова", "en": "🌐 Language", "ru": "🌐 Язык"},
    "menu_help": {"ua": "ℹ️ Довідка", "en": "ℹ️ Help", "ru": "ℹ️ Справка"},
    "menu_ai": {"ua": "🤖 AI-помічник", "en": "🤖 AI assistant", "ru": "🤖 AI-помощник"},
    "menu_webapp": {"ua": "🖥 Відкрити застосунок", "en": "🖥 Open mini app", "ru": "🖥 Открыть приложение"},
    "menu_stars": {"ua": "⭐ Підтримати проєкт", "en": "⭐ Support this project", "ru": "⭐ Поддержать проект"},
    "menu_watch": {"ua": "🔔 Курс-алерт", "en": "🔔 Rate alert", "ru": "🔔 Курс-алерт"},
    "back": {"ua": "◀️ Назад", "en": "◀️ Back", "ru": "◀️ Назад"},
    "help": {
        "ua": (
            "Команди:\n"
            "/start — головне меню\n"
            "/tasks — список задач\n"
            "/weather — погода в місті\n"
            "/currency — курси валют\n"
            "/lang — змінити мову\n\n"
            "Це демо-бот, зроблений як приклад для портфоліо: показує роботу з БД, зовнішніми API, "
            "inline-клавіатурами та станами діалогу."
        ),
        "en": (
            "Commands:\n"
            "/start — main menu\n"
            "/tasks — task list\n"
            "/weather — weather for a city\n"
            "/currency — exchange rates\n"
            "/lang — change language\n\n"
            "This is a portfolio demo bot showing database use, external APIs, inline keyboards, "
            "and conversation state."
        ),
        "ru": (
            "Команды:\n"
            "/start — главное меню\n"
            "/tasks — список задач\n"
            "/weather — погода в городе\n"
            "/currency — курсы валют\n"
            "/lang — сменить язык\n\n"
            "Это демо-бот для портфолио: показывает работу с БД, внешними API, inline-клавиатурами "
            "и состояниями диалога."
        ),
    },
    "tasks_empty": {
        "ua": "Задач поки немає. Додайте першу кнопкою нижче.",
        "en": "No tasks yet. Add your first one below.",
        "ru": "Задач пока нет. Добавьте первую кнопкой ниже.",
    },
    "tasks_title": {
        "ua": "📝 Ваші задачі (✔️ — виконати, 🗑 — видалити):",
        "en": "📝 Your tasks (✔️ — mark done, 🗑 — delete):",
        "ru": "📝 Ваши задачи (✔️ — выполнить, 🗑 — удалить):",
    },
    "tasks_add_btn": {"ua": "➕ Додати задачу", "en": "➕ Add task", "ru": "➕ Добавить задачу"},
    "tasks_ask": {
        "ua": "Напишіть текст задачі одним повідомленням:",
        "en": "Send the task text as a message:",
        "ru": "Напишите текст задачи одним сообщением:",
    },
    "tasks_added": {"ua": "Додано ✅", "en": "Added ✅", "ru": "Добавлено ✅"},
    "tasks_done": {"ua": "Готово ✅", "en": "Done ✅", "ru": "Готово ✅"},
    "weather_ask": {
        "ua": "Напишіть назву міста:",
        "en": "Type a city name:",
        "ru": "Напишите название города:",
    },
    "weather_not_found": {
        "ua": "Не знайшов таке місто 🤔 Спробуйте ще раз.",
        "en": "Couldn't find that city 🤔 Try again.",
        "ru": "Не нашёл такой город 🤔 Попробуйте ещё раз.",
    },
    "weather_result": {
        "ua": "📍 {city}\n🌡 {temp}°C, вітер {wind} км/год\n{desc}",
        "en": "📍 {city}\n🌡 {temp}°C, wind {wind} km/h\n{desc}",
        "ru": "📍 {city}\n🌡 {temp}°C, ветер {wind} км/ч\n{desc}",
    },
    "currency_loading": {
        "ua": "Тягну свіжі курси…",
        "en": "Fetching fresh rates…",
        "ru": "Тяну свежие курсы…",
    },
    "currency_result": {
        "ua": "💱 Курси до гривні (UAH):\n\n1 USD ≈ {usd:.2f} ₴\n1 EUR ≈ {eur:.2f} ₴\n\nДжерело: open.er-api.com",
        "en": "💱 Rates to Ukrainian hryvnia (UAH):\n\n1 USD ≈ {usd:.2f} ₴\n1 EUR ≈ {eur:.2f} ₴\n\nSource: open.er-api.com",
        "ru": "💱 Курсы к гривне (UAH):\n\n1 USD ≈ {usd:.2f} ₴\n1 EUR ≈ {eur:.2f} ₴\n\nИсточник: open.er-api.com",
    },
    "currency_error": {
        "ua": "Не вдалося отримати курси, спробуйте пізніше.",
        "en": "Couldn't fetch rates, try again later.",
        "ru": "Не удалось получить курсы, попробуйте позже.",
    },
    "lang_pick": {
        "ua": "Оберіть мову:",
        "en": "Choose a language:",
        "ru": "Выберите язык:",
    },
    "lang_set": {"ua": "Мову змінено ✅", "en": "Language changed ✅", "ru": "Язык изменён ✅"},
    "broadcast_usage": {
        "ua": "Використання: /broadcast текст повідомлення",
        "en": "Usage: /broadcast message text",
        "ru": "Использование: /broadcast текст сообщения",
    },
    "broadcast_done": {
        "ua": "Розіслано {n} користувачам.",
        "en": "Sent to {n} users.",
        "ru": "Разослано {n} пользователям.",
    },
    "broadcast_denied": {
        "ua": "Ця команда лише для адміністратора.",
        "en": "This command is admin-only.",
        "ru": "Эта команда только для администратора.",
    },
    "ai_ask": {
        "ua": "Напишіть питання одним повідомленням:",
        "en": "Send your question as a message:",
        "ru": "Напишите вопрос одним сообщением:",
    },
    "ai_thinking": {"ua": "Думаю…", "en": "Thinking…", "ru": "Думаю…"},
    "ai_disabled": {
        "ua": "AI-помічник вимкнено: не задано GEMINI_API_KEY, ANTHROPIC_API_KEY або OPENAI_API_KEY у налаштуваннях (GEMINI_API_KEY — безкоштовний варіант).",
        "en": "AI assistant is disabled: no GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY is configured (GEMINI_API_KEY is the free option).",
        "ru": "AI-помощник выключен: не задан GEMINI_API_KEY, ANTHROPIC_API_KEY или OPENAI_API_KEY в настройках (GEMINI_API_KEY — бесплатный вариант).",
    },
    "ai_cooldown": {
        "ua": "Занадто часто — спробуйте ще раз через {seconds} с.",
        "en": "Too many requests — try again in {seconds}s.",
        "ru": "Слишком часто — попробуйте ещё раз через {seconds} с.",
    },
    "ai_error": {
        "ua": "Не вдалося отримати відповідь від AI: {error}",
        "en": "Couldn't get a reply from the AI: {error}",
        "ru": "Не удалось получить ответ от AI: {error}",
    },
    "webapp_unavailable": {
        "ua": "Міні-застосунок доступний лише після деплою на постійний хостинг (потрібен HTTPS-адрес).",
        "en": "The mini app is only available once deployed to a permanent host (needs an HTTPS address).",
        "ru": "Мини-приложение доступно только после деплоя на постоянный хостинг (нужен HTTPS-адрес).",
    },
    "stars_title": {
        "ua": "Підтримка проєкту",
        "en": "Support this project",
        "ru": "Поддержка проекта",
    },
    "stars_description": {
        "ua": "Тестова оплата через Telegram Stars — {price} ⭐. Можна скасувати на екрані підтвердження, нічого не спишеться.",
        "en": "A test payment via Telegram Stars — {price} ⭐. You can cancel on the confirmation screen without being charged.",
        "ru": "Тестовый платёж через Telegram Stars — {price} ⭐. Можно отменить на экране подтверждения, ничего не спишется.",
    },
    "stars_label": {"ua": "Підтримка", "en": "Support", "ru": "Поддержка"},
    "stars_thanks": {
        "ua": "Дякую за підтримку! 🎉 Оплата пройшла успішно.",
        "en": "Thanks for the support! 🎉 Payment succeeded.",
        "ru": "Спасибо за поддержку! 🎉 Оплата прошла успешно.",
    },
    "watch_list_title": {
        "ua": "🔔 Ваші алерти по курсу:",
        "en": "🔔 Your rate alerts:",
        "ru": "🔔 Ваши алерты по курсу:",
    },
    "watch_list_empty": {
        "ua": "Алертів поки немає. Бот повідомить вас, щойно обраний курс перетне поріг.",
        "en": "No alerts yet. The bot will message you the moment a rate crosses your threshold.",
        "ru": "Алертов пока нет. Бот сообщит вам, как только выбранный курс пересечёт порог.",
    },
    "watch_add_btn": {"ua": "➕ Новий алерт", "en": "➕ New alert", "ru": "➕ Новый алерт"},
    "watch_pick_currency": {
        "ua": "За якою валютою стежити?",
        "en": "Which currency should I watch?",
        "ru": "За какой валютой следить?",
    },
    "watch_pick_direction": {
        "ua": "Повідомити, коли курс {currency}/UAH:",
        "en": "Notify me when the {currency}/UAH rate is:",
        "ru": "Сообщить, когда курс {currency}/UAH:",
    },
    "watch_dir_above": {"ua": "⬆️ Вище за...", "en": "⬆️ Above...", "ru": "⬆️ Выше чем..."},
    "watch_dir_below": {"ua": "⬇️ Нижче за...", "en": "⬇️ Below...", "ru": "⬇️ Ниже чем..."},
    "watch_ask_threshold": {
        "ua": "Напишіть число-поріг (наприклад 42.5):",
        "en": "Send the threshold number (e.g. 42.5):",
        "ru": "Напишите число-порог (например 42.5):",
    },
    "watch_invalid_number": {
        "ua": "Це не схоже на число. Спробуйте ще раз, наприклад 42.5:",
        "en": "That doesn't look like a number. Try again, e.g. 42.5:",
        "ru": "Это не похоже на число. Попробуйте ещё раз, например 42.5:",
    },
    "watch_created": {
        "ua": "Готово ✅ Повідомлю, коли {currency}/UAH буде {direction} {threshold}.",
        "en": "Done ✅ I'll notify you when {currency}/UAH is {direction} {threshold}.",
        "ru": "Готово ✅ Сообщу, когда {currency}/UAH будет {direction} {threshold}.",
    },
    "watch_direction_word_above": {"ua": "вище за", "en": "above", "ru": "выше"},
    "watch_direction_word_below": {"ua": "нижче за", "en": "below", "ru": "ниже"},
    "watch_deleted": {"ua": "Видалено 🗑", "en": "Deleted 🗑", "ru": "Удалено 🗑"},
    "watch_triggered": {
        "ua": "🔔 Курс {currency}/UAH зараз {rate} — це перетнуло ваш поріг {threshold}.",
        "en": "🔔 {currency}/UAH is now {rate} — that crossed your threshold of {threshold}.",
        "ru": "🔔 Курс {currency}/UAH сейчас {rate} — это пересекло ваш порог {threshold}.",
    },
}

WEATHER_CODES = {
    "ua": {
        0: "Ясно ☀️", 1: "Переважно ясно 🌤", 2: "Мінлива хмарність ⛅", 3: "Хмарно ☁️",
        45: "Туман 🌫", 48: "Туман з інеєм 🌫", 51: "Легка мряка 🌦", 61: "Дощ 🌧",
        71: "Сніг 🌨", 80: "Зливи 🌧", 95: "Гроза ⛈",
    },
    "en": {
        0: "Clear ☀️", 1: "Mostly clear 🌤", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
        45: "Fog 🌫", 48: "Rime fog 🌫", 51: "Light drizzle 🌦", 61: "Rain 🌧",
        71: "Snow 🌨", 80: "Showers 🌧", 95: "Thunderstorm ⛈",
    },
    "ru": {
        0: "Ясно ☀️", 1: "Малооблачно 🌤", 2: "Переменная облачность ⛅", 3: "Облачно ☁️",
        45: "Туман 🌫", 48: "Туман с инеем 🌫", 51: "Лёгкая морось 🌦", 61: "Дождь 🌧",
        71: "Снег 🌨", 80: "Ливень 🌧", 95: "Гроза ⛈",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in ("ua", "en", "ru") else "ua"
    template = TEXT[key][lang]
    return template.format(**kwargs) if kwargs else template


def weather_desc(code: int, lang: str) -> str:
    lang = lang if lang in ("ua", "en", "ru") else "ua"
    return WEATHER_CODES[lang].get(code, "—")
