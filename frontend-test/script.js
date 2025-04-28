// frontend-test/script.js

// Базовый адрес FastAPI
const API_BASE = "http://localhost:7000";

// Ключ локального хранилища
const LS_PHONE = "client_phone";

// Все секции и навигация
const views = document.querySelectorAll("main section");
const navBar = document.getElementById("nav-bar");
const loginView = document.getElementById("login-view");

document.addEventListener("DOMContentLoaded", () => {
  // Навигационные кнопки
  navBar.querySelectorAll("button[data-view]").forEach(btn => {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      if (view === "tickets-view") loadTickets();
      if (view === "payments-view") loadPayments();
      showView(view);
    });
  });
  navBar.querySelector("button[data-view='operator-view']")
  .addEventListener("click", () => { loadOperator(); showView("operator-view"); });
  // Логика форм
  document.getElementById("logout-btn").addEventListener("click", logout);
  document.getElementById("login-form").addEventListener("submit", onLogin);
  document.getElementById("ticket-form").addEventListener("submit", onSubmitTicket);
  document.getElementById("op-refresh").addEventListener("click", loadOperator);
  // Если уже залогинены — в профиль, иначе — в логин
  if (localStorage.getItem(LS_PHONE)) {
    setupAuthenticated();
    showView("dashboard-view");
    loadProfile();
  } else {
    showView("login-view");
  }
});

// Показать нужную секцию
function showView(id) {
  views.forEach(sec => {
    sec.id === id ? sec.classList.remove("hidden") : sec.classList.add("hidden");
  });
}

// Заголовки с телефоном клиента
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "X-Client-Phone": localStorage.getItem(LS_PHONE)
  };
}

// Обработчик логина
async function onLogin(e) {
  e.preventDefault();
  const phone = document.getElementById("login-phone").value.trim();
  if (!phone) return alert("Введите телефон");

  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone })
    });
    const payload = await res.json();
    if (!res.ok) {
      return alert(payload.detail || payload.message || "Ошибка входа");
    }
    // Сохраняем телефон и переходим в приложение
    localStorage.setItem(LS_PHONE, phone);
    setupAuthenticated();
    showView("dashboard-view");
    loadProfile();
  } catch (err) {
    console.error(err);
    alert("Сетевая ошибка при логине");
  }
}

// Настроить UI после логина
function setupAuthenticated() {
  loginView.classList.add("hidden");
  navBar.classList.remove("hidden");
}

// Выход
function logout() {
  localStorage.removeItem(LS_PHONE);
  location.reload();
}

// Загрузка профиля
async function loadProfile() {
  try {
    const res = await fetch(`${API_BASE}/api/users/me`, {
      headers: authHeaders()
    });
    const user = await res.json();
    if (!res.ok) throw user;

    document.getElementById("profile-name").textContent   = user.full_name;
    document.getElementById("profile-phone").textContent  = user.phone;
    document.getElementById("profile-tariff").textContent = user.tariff || "-";

    // Обработка services (JSON-объект вида {feature: boolean})
    let servicesText = "-";
    if (Array.isArray(user.services)) {
      // на случай, если придёт массив
      servicesText = user.services.join(", ");
    } else if (user.services && typeof user.services === "object") {
      servicesText = Object.entries(user.services)
        .filter(([_, enabled]) => enabled)
        .map(([name]) => name)
        .join(", ");
      if (!servicesText) servicesText = "-";
    }
    document.getElementById("profile-services").textContent = servicesText;

    document.getElementById("profile-balance").textContent = user.balance;
    document.getElementById("profile-debt").textContent    = user.debt;
  } catch (err) {
    console.error("Ошибка загрузки профиля:", err);
    alert("Не удалось загрузить профиль");
  }
}


// Отправка новой заявки
async function onSubmitTicket(e) {
  e.preventDefault();
  const phone = localStorage.getItem(LS_PHONE);
  const subject = document.getElementById("ticket-subject").value.trim();
  const text    = document.getElementById("ticket-text").value.trim();
  if (!subject || !text) return alert("Заполните тему и описание");

  try {
    const res = await fetch(`${API_BASE}/api/tickets`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ client_phone: phone, subject, text })
    });
    const data = await res.json();
    if (!res.ok) throw data;
    document.getElementById("ticket-result").textContent =
      `Заявка №${data.id} создана. Категория: ${data.category}`;
    document.getElementById("ticket-form").reset();
  } catch (err) {
    console.error("Ошибка создания заявки:", err);
    alert(err.detail || err.message || "Ошибка создания заявки");
  }
}

// Загрузка списка заявок
async function loadTickets() {
  const phone = localStorage.getItem(LS_PHONE);
  const tbody = document.querySelector("#tickets-table tbody");
  tbody.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/api/tickets?client_phone=${encodeURIComponent(phone)}`, {
      headers: authHeaders()
    });
    const tickets = await res.json();
    if (!res.ok) throw tickets;

    tickets.forEach(t => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${t.id}</td>
        <td>${t.subject || "-"}</td>
        <td>${t.category || "-"}</td>
        <td>${t.status}</td>
        <td>${new Date(t.created_at).toLocaleString()}</td>
      `;
      tbody.append(tr);
    });
  } catch (err) {
    console.error("Ошибка загрузки заявок:", err);
    alert("Не удалось загрузить заявки");
  }
}

// Загрузка истории платежей
async function loadPayments() {
  const phone = localStorage.getItem(LS_PHONE);
  const tbody = document.querySelector("#payments-table tbody");
  tbody.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/api/payments?client_phone=${encodeURIComponent(phone)}`, {
      headers: authHeaders()
    });
    const payments = await res.json();
    if (!res.ok) throw payments;

    payments.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${new Date(p.date).toLocaleDateString()}</td>
        <td>${p.amount}</td>
        <td>${p.service || "-"}</td>
        <td>${p.status}</td>
      `;
      tbody.append(tr);
    });
  } catch (err) {
    console.error("Ошибка загрузки платежей:", err);
    alert("Не удалось загрузить платежи");
  }
}
// --- AI Chat ---

// Инициализация чата (очистка окна при открытии)
function initChat() {
  const chatWindow = document.getElementById("chat-window");
  if (chatWindow) {
    chatWindow.innerHTML = ''; // Очищаем старые сообщения
  }
}

// Обработчик отправки сообщения в чат
document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("chat-input");
      const text = input.value.trim();
      if (!text) return;

      appendMessage("Вы", text);
      input.value = "";

      appendMessage("AI", "Печатает...");

      try {
        const phone = localStorage.getItem(LS_PHONE);  // Берём номер телефона из localStorage
        if (!phone) {
          replaceLastMessage("Ошибка", "Не найден номер клиента, авторизуйтесь заново.");
          return;
        }

        const res = await fetch(`${API_BASE}/api/ai/chat_with_db`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            client_phone: phone
          })
        });

        const data = await res.json();
        if (!res.ok) throw data;

        replaceLastMessage("AI", data.ai_message);
      } catch (err) {
        console.error("Ошибка общения с AI:", err);
        replaceLastMessage("Ошибка", err.detail || err.message || "Не удалось получить ответ от AI");
      }
    });
  }
});

// Добавляем сообщение в окно чата
function appendMessage(author, text) {
  const chatWindow = document.getElementById("chat-window");
  const msg = document.createElement("div");
  msg.innerHTML = `<strong>${author}:</strong> ${text}`;
  msg.style.marginBottom = "0.5rem";
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Заменяем последнее сообщение
function replaceLastMessage(author, text) {
  const chatWindow = document.getElementById("chat-window");
  const msgs = chatWindow.querySelectorAll("div");
  if (msgs.length > 0) {
    const lastMsg = msgs[msgs.length - 1];
    lastMsg.innerHTML = `<strong>${author}:</strong> ${text}`;
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
}


async function loadOperator() {
  const cat = document.getElementById("op-filter-category").value;
  const st  = document.getElementById("op-filter-status").value;
  const url = new URL(`${API_BASE}/api/operator/tickets`);
  if (cat) url.searchParams.set("category", cat);
  if (st)  url.searchParams.set("status", st);
  const res = await fetch(url, { headers: authHeaders() });
  const data = await res.json();
  const tbody = document.querySelector("#operator-table tbody");
  tbody.innerHTML = "";
  data.forEach(t => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.id}</td>
      <td>${t.subject||"-"}</td>
      <td>${t.category||"-"}</td>
      <td>${t.status}</td>
      <td>${t.assigned_to||"-"}</td>
      <td>${new Date(t.created_at).toLocaleString()}</td>
      <td>
        <button class="op-view" data-id="${t.id}">Открыть</button>
      </td>`;
    tbody.append(tr);
  });
  document.querySelectorAll(".op-view").forEach(btn =>
    btn.addEventListener("click", () => openOperatorDetail(btn.dataset.id))
  );
}

async function openOperatorDetail(id) {
  document.getElementById("operator-detail").classList.remove("hidden");
  // 1) история клиента
  const resH = await fetch(`${API_BASE}/api/operator/tickets/${id}/history`, { headers: authHeaders() });
  const hist = await resH.json();
  document.getElementById("client-history").innerText =
    JSON.stringify(hist, null, 2);

  // 2) комментарии
  const resC = await fetch(`${API_BASE}/api/operator/tickets/${id}/comments`, { headers: authHeaders() });
  const comm = await resC.json();
  const list = document.getElementById("comments-list");
  list.innerHTML = comm.map(c => `<p><strong>${c.author}</strong>: ${c.text}</p>`).join("");

  // 3) отправка комментариев
  const form = document.getElementById("comment-form");
  form.onsubmit = async e => {
    e.preventDefault();
    const author = document.getElementById("comment-author").value;
    const text   = document.getElementById("comment-text").value;
    await fetch(`${API_BASE}/api/operator/tickets/${id}/comments`, {
      method: "POST",
      headers: {...authHeaders(), "Content-Type":"application/json"},
      body: JSON.stringify({author, text})
    });
    form.reset();
    openOperatorDetail(id);
  };

  // 4) генерация и рассылка ответа
  document.getElementById("generate-and-send").onclick = async () => {
    const resp = await fetch(`${API_BASE}/api/tickets/${id}/send_response`, {
      method: "POST", headers: authHeaders()
    });
    const data = await resp.json();
    document.getElementById("ai-response").innerText = data.ai_response;
    alert(data.message);
  };
}
