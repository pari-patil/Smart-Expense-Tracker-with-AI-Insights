let token = null;
let charts = { pie: null, bar: null, line: null };

function authHeaders() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function requireLogin() {
  if (!token) {
    alert('Please login first');
    throw new Error('Not logged in');
  }
}

async function registerUser() {
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const res = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });
  const data = await res.json();
  document.getElementById('authStatus').textContent = data.message || data.error;
}

async function loginUser() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();

  token = data.access_token || null;
  document.getElementById('authStatus').textContent = token
    ? `Logged in as ${data.name} (${data.email})`
    : (data.error || 'Login failed');

  if (token) await refreshAll();
}

function clearExpenseForm() {
  document.getElementById('editingExpenseId').value = '';
  document.getElementById('description').value = '';
  document.getElementById('amount').value = '';
  document.getElementById('category').value = '';
  document.getElementById('date').value = '';
}

async function saveExpense() {
  requireLogin();
  const id = document.getElementById('editingExpenseId').value;
  const payload = {
    description: document.getElementById('description').value,
    amount: parseFloat(document.getElementById('amount').value || '0'),
    category: document.getElementById('category').value,
    date: document.getElementById('date').value
  };

  const url = id ? `/api/expenses/${id}` : '/api/expenses';
  const method = id ? 'PUT' : 'POST';

  await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(payload)
  });

  clearExpenseForm();
  await refreshAll();
}

function populateExpenseForm(item) {
  document.getElementById('editingExpenseId').value = item.id;
  document.getElementById('description').value = item.description;
  document.getElementById('amount').value = item.amount;
  document.getElementById('category').value = item.category;
  document.getElementById('date').value = item.date;
}

async function deleteExpense(id) {
  requireLogin();
  if (!confirm('Delete this expense?')) return;
  await fetch(`/api/expenses/${id}`, { method: 'DELETE', headers: authHeaders() });
  await refreshAll();
}

async function uploadCSV() {
  requireLogin();
  const file = document.getElementById('csvFile').files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);
  await fetch('/api/expenses/upload-csv', { method: 'POST', headers: authHeaders(), body: formData });
  await refreshAll();
}

async function setBudget() {
  requireLogin();
  const category = document.getElementById('budgetCategory').value;
  const monthly_limit = parseFloat(document.getElementById('budgetAmount').value || '0');

  await fetch('/api/budgets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ category, monthly_limit })
  });
  await refreshAll();
}

async function refreshAll() {
  await Promise.all([loadExpenses(), loadInsights()]);
}

async function loadExpenses() {
  const res = await fetch('/api/expenses', { headers: authHeaders() });
  if (!res.ok) return;
  const rows = await res.json();

  const tbody = document.getElementById('expenseRows');
  tbody.innerHTML = '';
  rows.forEach((r) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.date}</td>
      <td>${r.description}</td>
      <td>${r.category}</td>
      <td>₹${Number(r.amount).toFixed(2)}</td>
      <td><div class="actions"><button class="small edit-btn">Edit</button><button class="small danger delete-btn">Delete</button></div></td>
    `;

    tr.querySelector('.edit-btn').addEventListener('click', () => populateExpenseForm(r));
    tr.querySelector('.delete-btn').addEventListener('click', () => deleteExpense(r.id));
    tbody.appendChild(tr);
  });
}

async function loadInsights() {
  const res = await fetch('/api/insights', { headers: authHeaders() });
  if (!res.ok) return;

  const data = await res.json();
  document.getElementById('predicted').textContent = data.predicted_next_month || 0;

  const budgetList = document.getElementById('budgetList');
  budgetList.innerHTML = '';
  (data.budget_vs_actual || []).forEach((item) => {
    const li = document.createElement('li');
    li.textContent = `${item.category}: Budget ₹${item.budget} | Actual ₹${item.actual} | Variance ₹${item.variance}`;
    budgetList.appendChild(li);
  });

  const suggestions = document.getElementById('suggestions');
  suggestions.innerHTML = '';
  (data.suggestions || []).forEach((s) => {
    const li = document.createElement('li');
    li.textContent = s;
    suggestions.appendChild(li);
  });

  renderCharts(data.by_category || {}, data.monthly_totals || {});
}

function renderCharts(byCategory, monthlyTotals) {
  const monthlyLabels = Object.keys(monthlyTotals);
  const monthlyValues = Object.values(monthlyTotals);

  if (charts.pie) charts.pie.destroy();
  charts.pie = new Chart(document.getElementById('pieChart'), {
    type: 'pie',
    data: { labels: Object.keys(byCategory), datasets: [{ data: Object.values(byCategory) }] }
  });

  if (charts.bar) charts.bar.destroy();
  charts.bar = new Chart(document.getElementById('barChart'), {
    type: 'bar',
    data: { labels: monthlyLabels, datasets: [{ label: 'Monthly comparison', data: monthlyValues }] }
  });

  if (charts.line) charts.line.destroy();
  charts.line = new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: { labels: monthlyLabels, datasets: [{ label: 'Spending trend', data: monthlyValues, tension: 0.25 }] }
  });
}
