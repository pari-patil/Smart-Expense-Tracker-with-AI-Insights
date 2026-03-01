# 💰 Smart Expense Tracker with AI Insights

An AI-powered full-stack web application that helps users track daily expenses, automatically categorize transactions using Machine Learning, predict future spending, and visualize financial insights through interactive dashboards.

---

## 🚀 Features

- 📌 Add, edit, and delete daily expenses
- 🤖 Automatic expense categorization using ML
- 📈 Monthly spending prediction
- 📊 Interactive dashboard with charts
- 🗂 Category-wise expense breakdown
- 💾 MySQL database integration
- 🔗 RESTful API architecture

---

## 🧠 AI Implementation

### 1️⃣ Auto-Categorization
- Text preprocessing using **TF-IDF Vectorization**
- Classification using:
  - Logistic Regression
  - Naive Bayes
- Predicts category based on transaction description

Example:
```
Input: "Uber ride to office"
Output: "Transport"
```

### 2️⃣ Spending Prediction
- Regression-based model for forecasting next month’s expenses
- Uses historical transaction data
- Provides budget insights

---

## 🛠 Tech Stack

| Layer        | Technology Used |
|-------------|-----------------|
| Frontend     | HTML, CSS, JavaScript |
| Charts       | Chart.js |
| Backend      | Flask / PHP |
| Database     | MySQL |
| Machine Learning | Scikit-learn |
| APIs         | RESTful APIs |

---

## 📊 Dashboard Insights

- 🥧 Pie Chart – Category distribution
- 📊 Bar Chart – Monthly comparison
- 📈 Line Chart – Spending trends
- 🔮 Predicted next month spending

---

## 🗄 Database Schema (Simplified)

### Users Table
- id
- name
- email
- password

### Expenses Table
- id
- user_id
- amount
- category
- description
- date

---

## ⚙ Installation & Setup

### 1️⃣ Clone the repository
```
git clone https://github.com/yourusername/smart-expense-tracker.git
cd smart-expense-tracker
```

### 2️⃣ Create Virtual Environment (Flask)
```
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Configure Database
- Create MySQL database
- Update DB credentials in config file

### 5️⃣ Run Application
```
python app.py
```

---

## 📌 API Endpoints (Sample)

| Method | Endpoint | Description |
|--------|----------|------------|
| POST | /add-expense | Add new expense |
| GET | /expenses | Get all expenses |
| POST | /predict-category | Predict category using ML |
| GET | /predict-spending | Forecast next month expense |

---

## 💡 Future Enhancements

- 🔐 JWT Authentication
- 📂 CSV Upload for bulk transactions
- 💰 Budget alert notifications
- ☁ Cloud deployment (AWS / Render)
- 📱 Fully responsive UI

---

## 💼 Project Highlights

✔ Full-Stack Web Development  
✔ Machine Learning Integration  
✔ REST API Design  
✔ Data Analytics & Forecasting  
✔ Real-world Financial Use Case  

---

## 📄 License

This project is licensed under the MIT License.

---

## 👩‍💻 Author

Your Name  
B.Tech CSE (Data Science)  
Aspiring Software Developer | AI Enthusiast
