# 💰 Smart Expense Tracker with AI Insights

An AI-powered full-stack web application that helps users track daily expenses, automatically categorize transactions using Machine Learning, predict future spending, and visualize financial insights through interactive dashboards.

---

## 🚀 Features

- 📌 Add, edit, and delete daily expenses
- 🤖 Automatic expense categorization using ML
- 📈 Monthly spending prediction
- 📊 Interactive dashboard with pie/bar/line charts
- 🗂 Category-wise expense breakdown
- 💾 MySQL database integration (`MYSQL_URL`) with SQLite fallback
- 🔗 RESTful API architecture
- 🔐 JWT authentication
- 📥 CSV upload for bulk expenses
- 📱 Responsive UI
- 🧠 AI-based saving suggestions

---

## 🧠 AI Implementation

### 1️⃣ Auto-Categorization
- Text preprocessing using **TF-IDF Vectorization**
- Classification using:
  - Logistic Regression
  - Naive Bayes
- Predicts category based on transaction description

Example:

```text
Input: "Uber ride to office"
Output: "Transport"
```

### 2️⃣ Spending Prediction
- Regression-based model for forecasting next month’s expenses
- Uses historical transaction data
- Provides budget planning insights

---

## 🛠 Tech Stack

| Layer | Technology Used |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Backend | Flask |
| Database | MySQL / SQLite |
| Machine Learning | Scikit-learn |
| APIs | RESTful APIs |

---

## 📊 Dashboard Insights

- 🥧 Pie Chart – Category distribution
- 📊 Bar Chart – Monthly comparison
- 📈 Line Chart – Spending trends
- 🔮 Predicted next month spending
- 💡 Smart saving suggestions

---

## 🗄 Database Schema (Simplified)

### Users Table
- id
- name
- email
- password_hash

### Expenses Table
- id
- user_id
- amount
- category
- description
- date

### Budgets Table
- id
- user_id
- category
- monthly_limit

---

## ⚙ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/smart-expense-tracker.git
cd smart-expense-tracker
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Database
- Optional: set `MYSQL_URL` for MySQL usage.
- If not set, app uses local SQLite (`expenses.db`).

### 5️⃣ Run Application
```bash
python app.py
```

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login and get JWT |
| POST | /api/expenses | Add expense |
| GET | /api/expenses | List expenses |
| PUT | /api/expenses/{id} | Edit expense |
| DELETE | /api/expenses/{id} | Delete expense |
| POST | /api/expenses/upload-csv | Bulk upload expenses |
| POST | /api/budgets | Set category budget |
| POST | /api/predict-category | Predict category from text |
| GET | /api/predict-spending | Forecast next month expense |
| GET | /api/insights | Full dashboard insights |

---

## 📄 License

This project is licensed under the MIT License.
