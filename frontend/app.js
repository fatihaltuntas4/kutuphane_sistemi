const API_URL = "http://127.0.0.1:8000";
let currentUser = null;
let token = null;

function showToast(message, isError = false) {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${isError ? 'error' : ''}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = "slideInRight 0.3s reverse forwards";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const btn = input.nextElementSibling;
    if (input.type === "password") {
        input.type = "text";
        btn.textContent = "🙈"; 
    } else {
        input.type = "password";
        btn.textContent = "👁️"; 
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => form.classList.add('hidden'));
    
    event.target.classList.add('active');
    document.getElementById(`${tabName}-form`).classList.remove('hidden');
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Giriş başarısız");

        token = data.access_token;
        const payload = JSON.parse(atob(token.split('.')[1]));
        currentUser = { email: payload.sub, role: payload.role };
        
        document.getElementById("auth-section").classList.add("hidden");
        document.getElementById("dashboard-section").classList.remove("hidden");
        document.getElementById("user-greeting").textContent = `Merhaba, ${currentUser.email}`;
        
        setupMenu();
        showToast("Başarıyla giriş yapıldı!");
    } catch (err) {
        showToast(err.message, true);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById("register-name").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const role = document.getElementById("register-role").value;

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ full_name: name, email: email, password: password, role: role })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Kayıt başarısız");

        showToast("Kayıt başarılı! Lütfen giriş yapın.");
        switchTab('login');
        document.querySelector('.tab-btn[onclick="switchTab(\'login\')"]').click();
    } catch (err) {
        showToast(err.message, true);
    }
}

function handleLogout() {
    currentUser = null;
    token = null;
    document.getElementById("dashboard-section").classList.add("hidden");
    document.getElementById("auth-section").classList.remove("hidden");
    showToast("Çıkış yapıldı");
}

// Menü ve Görünüm Kontrolü
function setupMenu() {
    const menuList = document.getElementById("menu-list");
    menuList.innerHTML = "";
    
    // Herkes için Kitap Kataloğu
    addMenuItem(menuList, "📚 Kitap Kataloğu", "view-books", true);
    // Herkes için İşlemlerim
    addMenuItem(menuList, "👤 İşlemlerim", "view-my-transactions");
    
    if (currentUser.role === "Yönetici" || currentUser.role === "Kütüphaneci") {
        addMenuItem(menuList, "🛠️ Kitap Yönetimi", "view-admin-books");
        addMenuItem(menuList, "📋 Tüm İşlemler", "view-all-transactions");
        addMenuItem(menuList, "📊 Raporlar", "view-reports");
    }
    
    switchView('view-books');
}

function addMenuItem(parent, text, targetId, isActive = false) {
    const li = document.createElement("li");
    li.textContent = text;
    if (isActive) li.classList.add("active");
    li.onclick = (e) => {
        document.querySelectorAll("#menu-list li").forEach(el => el.classList.remove("active"));
        e.target.classList.add("active");
        switchView(targetId);
    };
    parent.appendChild(li);
}

function switchView(viewId) {
    document.querySelectorAll(".view-section").forEach(v => v.classList.add("hidden"));
    document.getElementById(viewId).classList.remove("hidden");
    
    if (viewId === "view-books") fetchBooks();
    if (viewId === "view-my-transactions") fetchMyTransactions();
    if (viewId === "view-admin-books") fetchAdminBooks();
    if (viewId === "view-all-transactions") fetchAllTransactions();
    if (viewId === "view-reports") fetchReports();
}

// Kitap İşlemleri (Arama vs)
async function fetchBooks() {
    const q = document.getElementById("search-input").value;
    let url = `${API_URL}/books/?limit=50`;
    if(q) url += `&q=${encodeURIComponent(q)}`;

    try {
        const response = await fetch(url);
        const books = await response.json();
        
        const grid = document.getElementById("books-grid");
        grid.innerHTML = "";
        
        books.forEach(book => {
            const card = document.createElement("div");
            card.className = "book-card";
            card.innerHTML = `
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author} | ${book.publication_year}</div>
                <div class="badge ${book.is_available ? 'available' : 'unavailable'}">
                    ${book.is_available ? 'Müsait' : 'Ödünç Alındı'}
                </div>
                <div style="margin-top:15px">
                    ${book.is_available ? 
                        `<button class="primary-btn" onclick="borrowBook('${book.isbn}')">Ödünç Al</button>` : 
                        `<button class="primary-btn" style="background:#f59e0b" onclick="reserveBook('${book.isbn}')">Rezervasyon Yap</button>`
                    }
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        showToast("Kitaplar yüklenemedi", true);
    }
}

async function borrowBook(isbn) {
    try {
        const res = await fetch(`${API_URL}/transactions/borrow`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: currentUser.email, isbn: isbn, days: 15 })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast(data.mesaj);
        fetchBooks();
    } catch(e) {
        showToast(e.message, true);
    }
}

async function reserveBook(isbn) {
    try {
        const res = await fetch(`${API_URL}/transactions/reserve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: currentUser.email, isbn: isbn })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast(data.mesaj);
    } catch(e) {
        showToast(e.message, true);
    }
}

// İşlemlerim Sayfası
async function fetchMyTransactions() {
    try {
        const resBorrows = await fetch(`${API_URL}/transactions/me?email=${currentUser.email}`);
        const borrows = await resBorrows.json();
        const tbBorrows = document.getElementById("my-borrows-tbody");
        tbBorrows.innerHTML = "";
        borrows.forEach(b => {
            tbBorrows.innerHTML += `
                <tr>
                    <td>${b.book_title}</td>
                    <td>${b.borrow_date}</td>
                    <td>${b.due_date}</td>
                    <td>${b.status}</td>
                    <td>
                        ${b.status === "Aktif" ? `<button class="danger-btn" style="background:#10b981" onclick="returnBook(${b.transaction_id})">İade Et</button>` : "-"}
                    </td>
                </tr>`;
        });

        const resReserves = await fetch(`${API_URL}/transactions/reservations/me?email=${currentUser.email}`);
        const reserves = await resReserves.json();
        const tbReserves = document.getElementById("my-reserves-tbody");
        tbReserves.innerHTML = "";
        reserves.forEach(r => {
            tbReserves.innerHTML += `
                <tr>
                    <td>${r.book_title}</td>
                    <td>${r.reservation_date.substring(0,10)}</td>
                    <td>${r.status}</td>
                    <td>
                        ${r.status === "Bekliyor" ? `<button class="danger-btn" onclick="cancelReservation(${r.reservation_id})">İptal Et</button>` : "-"}
                    </td>
                </tr>`;
        });
    } catch(e) {
        showToast("İşlemler yüklenemedi", true);
    }
}

async function returnBook(id) {
    try {
        const res = await fetch(`${API_URL}/transactions/return`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transaction_id: id })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast(data.mesaj);
        fetchMyTransactions();
    } catch(e) {
        showToast(e.message, true);
    }
}

async function cancelReservation(id) {
    try {
        const res = await fetch(`${API_URL}/transactions/reserve/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast(data.mesaj);
        fetchMyTransactions();
    } catch(e) {
        showToast(e.message, true);
    }
}

// Yönetici: Kitap Yönetimi
async function fetchAdminBooks() {
    try {
        const response = await fetch(`${API_URL}/books/?limit=100`);
        const books = await response.json();
        const tbody = document.getElementById("admin-books-tbody");
        tbody.innerHTML = "";
        books.forEach(b => {
            tbody.innerHTML += `
                <tr>
                    <td>${b.isbn}</td>
                    <td>${b.title}</td>
                    <td>${b.author}</td>
                    <td>${b.is_available ? '<span style="color:#10b981">Müsait</span>' : '<span style="color:#ef4444">Müsait Değil</span>'}</td>
                    <td><button class="danger-btn" onclick="deleteBook('${b.isbn}')">Sil</button></td>
                </tr>`;
        });
    } catch(e) {
        showToast("Kitaplar yüklenemedi", true);
    }
}

async function handleAddBook(e) {
    e.preventDefault();
    const body = {
        isbn: document.getElementById("add-isbn").value,
        title: document.getElementById("add-title").value,
        author: document.getElementById("add-author").value,
        publisher: document.getElementById("add-publisher").value,
        publication_year: parseInt(document.getElementById("add-year").value),
        is_available: true
    };
    try {
        const res = await fetch(`${API_URL}/books/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast("Kitap Eklendi!");
        e.target.reset();
        fetchAdminBooks();
    } catch(e) {
        showToast(e.message, true);
    }
}

async function deleteBook(isbn) {
    if(!confirm("Bu kitabı silmek istediğinize emin misiniz?")) return;
    try {
        const res = await fetch(`${API_URL}/books/${isbn}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast(data.mesaj);
        fetchAdminBooks();
    } catch(e) {
        showToast(e.message, true);
    }
}

// Yönetici: Tüm İşlemler
async function fetchAllTransactions() {
    try {
        const response = await fetch(`${API_URL}/transactions/all`);
        const txs = await response.json();
        const tbody = document.getElementById("all-transactions-tbody");
        tbody.innerHTML = "";
        txs.forEach(t => {
            tbody.innerHTML += `
                <tr>
                    <td>#${t.transaction_id}</td>
                    <td>${t.user_email}</td>
                    <td>${t.book_title}</td>
                    <td>${t.borrow_date} / ${t.due_date}</td>
                    <td>${t.status}</td>
                </tr>`;
        });
    } catch(e) {
        showToast("İşlemler yüklenemedi", true);
    }
}

// Raporlar (PDF İsterlerine Göre)
async function fetchReports() {
    try {
        const [resMost, resUsers, resOverdue, resCurrent, resMonthly] = await Promise.all([
            fetch(`${API_URL}/reports/most-borrowed`),
            fetch(`${API_URL}/reports/active-users`),
            fetch(`${API_URL}/reports/overdue`),
            fetch(`${API_URL}/reports/currently-borrowed`),
            fetch(`${API_URL}/reports/monthly-stats`)
        ]);
        
        const mostBorrowed = await resMost.json();
        const activeUsers = await resUsers.json();
        const overdue = await resOverdue.json();
        const current = await resCurrent.json();
        const monthly = await resMonthly.json();

        document.getElementById("most-borrowed-list").innerHTML = mostBorrowed.map(b => `<li><span>${b.title}</span> <span>${b.borrow_count} kez</span></li>`).join('');
        document.getElementById("active-users-list").innerHTML = activeUsers.map(u => `<li><span>${u.email}</span> <span>${u.borrow_count} işlem</span></li>`).join('');
        document.getElementById("overdue-list").innerHTML = overdue.map(o => `<li><span>${o.book_title}</span> <span style="color:#ef4444">${o.user_email}</span></li>`).join('');
        document.getElementById("currently-borrowed-list").innerHTML = current.map(c => `<li><span>${c.book_title}</span> <span style="color:#10b981">${c.user_email}</span></li>`).join('');
        document.getElementById("monthly-stats-list").innerHTML = monthly.map(m => `<li><span>${m.month}</span> <span style="color:#6366f1">${m.count} ödünç</span></li>`).join('');
    } catch (err) {
        showToast("Raporlar yüklenemedi", true);
    }
}
