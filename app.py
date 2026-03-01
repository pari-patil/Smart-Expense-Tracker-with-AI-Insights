import csv
import io
import os
from datetime import date, datetime

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

mysql_url = os.getenv("MYSQL_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url or "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)


CATEGORIES = ["Food", "Transport", "Shopping", "Health", "Utilities", "Entertainment", "Education", "Other"]
TRAIN_TEXT = [
    "grocery vegetables supermarket restaurant dinner lunch",
    "uber taxi metro bus fuel parking",
    "amazon clothes electronics shopping order",
    "doctor medicine pharmacy hospital checkup",
    "electricity water internet rent bill recharge",
    "movie netflix concert game subscription",
    "tuition books course training exam",
    "misc expense random payment",
]
TRAIN_LABELS = ["Food", "Transport", "Shopping", "Health", "Utilities", "Entertainment", "Education", "Other"]

logistic_model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
    ("clf", LogisticRegression(max_iter=500)),
])
nb_model = Pipeline([
    ("tfidf", TfidfVectorizer(lowercase=True)),
    ("clf", MultinomialNB()),
])
logistic_model.fit(TRAIN_TEXT, TRAIN_LABELS)
nb_model.fit(TRAIN_TEXT, TRAIN_LABELS)


def predict_category(text: str) -> str:
    clean_text = (text or "").strip().lower() or "misc expense"
    proba = logistic_model.predict_proba([clean_text])[0]
    best_idx = int(np.argmax(proba))
    if proba[best_idx] >= 0.55:
        return logistic_model.classes_[best_idx]
    return nb_model.predict([clean_text])[0]


def current_user_id() -> int:
    return int(get_jwt_identity())


def parse_expense_date(raw_date: str | None) -> date:
    if not raw_date:
        return date.today()
    return datetime.strptime(raw_date, "%Y-%m-%d").date()


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/auth/register")
def register():
    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip() or "User"
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 409

    user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "registered"}), 201


@app.post("/api/auth/login")
def login():
    payload = request.get_json() or {}
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "name": user.name, "email": user.email})


@app.post("/api/expenses")
@app.post("/add-expense")
@jwt_required()
def add_expense():
    payload = request.get_json() or {}
    description = (payload.get("description") or payload.get("title") or "").strip()
    amount = float(payload.get("amount") or 0)
    category = (payload.get("category") or "").strip()
    note = (payload.get("note") or "").strip()

    if not description or amount <= 0:
        return jsonify({"error": "description and positive amount are required"}), 400

    category = category or predict_category(f"{description} {note}")
    expense = Expense(
        user_id=current_user_id(),
        amount=amount,
        category=category,
        description=description,
        date=parse_expense_date(payload.get("date") or payload.get("spent_on")),
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify({"message": "expense added", "id": expense.id, "category": category}), 201


@app.get("/api/expenses")
@app.get("/expenses")
@jwt_required()
def list_expenses():
    rows = Expense.query.filter_by(user_id=current_user_id()).order_by(Expense.date.desc(), Expense.id.desc()).all()
    return jsonify([
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "description": e.description,
            "date": e.date.isoformat(),
        }
        for e in rows
    ])


@app.put("/api/expenses/<int:expense_id>")
@jwt_required()
def update_expense(expense_id: int):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user_id()).first()
    if not expense:
        return jsonify({"error": "expense not found"}), 404

    payload = request.get_json() or {}
    if "description" in payload or "title" in payload:
        expense.description = (payload.get("description") or payload.get("title") or expense.description).strip()
    if "amount" in payload:
        expense.amount = float(payload.get("amount") or expense.amount)
    if "category" in payload:
        expense.category = (payload.get("category") or expense.category).strip() or expense.category
    if "date" in payload or "spent_on" in payload:
        expense.date = parse_expense_date(payload.get("date") or payload.get("spent_on"))

    if expense.amount <= 0 or not expense.description:
        return jsonify({"error": "invalid expense data"}), 400

    db.session.commit()
    return jsonify({"message": "expense updated"})


@app.delete("/api/expenses/<int:expense_id>")
@jwt_required()
def delete_expense(expense_id: int):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user_id()).first()
    if not expense:
        return jsonify({"error": "expense not found"}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "expense deleted"})


@app.post("/api/expenses/upload-csv")
@jwt_required()
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    file = request.files["file"]
    content = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    inserted = 0

    for row in reader:
        description = (row.get("description") or row.get("title") or "").strip()
        amount = float(row.get("amount") or 0)
        if not description or amount <= 0:
            continue

        category = (row.get("category") or "").strip() or predict_category(description)
        db.session.add(Expense(
            user_id=current_user_id(),
            amount=amount,
            category=category,
            description=description,
            date=parse_expense_date(row.get("date") or row.get("spent_on")),
        ))
        inserted += 1

    db.session.commit()
    return jsonify({"message": "csv imported", "inserted": inserted})


@app.post("/api/budgets")
@jwt_required()
def set_budget():
    payload = request.get_json() or {}
    category = (payload.get("category") or "").strip()
    monthly_limit = float(payload.get("monthly_limit") or 0)

    if not category or monthly_limit <= 0:
        return jsonify({"error": "category and positive monthly_limit are required"}), 400

    user_id = current_user_id()
    budget = Budget.query.filter_by(user_id=user_id, category=category).first()
    if budget:
        budget.monthly_limit = monthly_limit
    else:
        db.session.add(Budget(user_id=user_id, category=category, monthly_limit=monthly_limit))

    db.session.commit()
    return jsonify({"message": "budget set"})


@app.post("/api/predict-category")
@app.post("/predict-category")
@jwt_required()
def predict_category_endpoint():
    payload = request.get_json() or {}
    description = (payload.get("description") or "").strip()
    if not description:
        return jsonify({"error": "description is required"}), 400
    return jsonify({"category": predict_category(description)})


def _predict_next_month_from_expenses(expenses: list[Expense]) -> float:
    if not expenses:
        return 0.0
    df = pd.DataFrame([{"amount": e.amount, "date": pd.to_datetime(e.date)} for e in expenses])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly_totals = df.groupby("month")["amount"].sum().sort_index()
    if len(monthly_totals) < 2:
        predicted = float(monthly_totals.iloc[-1])
    else:
        X = np.arange(len(monthly_totals)).reshape(-1, 1)
        y = monthly_totals.values
        model = LinearRegression().fit(X, y)
        predicted = float(model.predict([[len(monthly_totals)]])[0])
    return round(max(0, predicted), 2)


@app.get("/api/predict-spending")
@app.get("/predict-spending")
@jwt_required()
def predict_spending():
    expenses = Expense.query.filter_by(user_id=current_user_id()).all()
    return jsonify({"predicted_next_month": _predict_next_month_from_expenses(expenses)})


@app.get("/api/insights")
@jwt_required()
def insights():
    user_id = current_user_id()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()

    if not expenses:
        return jsonify({
            "by_category": {},
            "monthly_totals": {},
            "predicted_next_month": 0,
            "budget_vs_actual": [],
            "suggestions": ["Add expenses to unlock personalized AI insights."],
        })

    df = pd.DataFrame([
        {"amount": e.amount, "category": e.category, "date": pd.to_datetime(e.date)}
        for e in expenses
    ])
    by_category = df.groupby("category")["amount"].sum().round(2).to_dict()

    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly_totals = df.groupby("month")["amount"].sum().round(2).sort_index()

    predicted = _predict_next_month_from_expenses(expenses)

    budget_map = {b.category: b.monthly_limit for b in budgets}
    current_month = date.today().strftime("%Y-%m")
    current_actual = df[df["month"] == current_month].groupby("category")["amount"].sum().to_dict()

    categories = sorted(set(budget_map.keys()) | set(current_actual.keys()))
    budget_vs_actual = []
    for cat in categories:
        budget = round(float(budget_map.get(cat, 0)), 2)
        actual = round(float(current_actual.get(cat, 0)), 2)
        budget_vs_actual.append({"category": cat, "budget": budget, "actual": actual, "variance": round(budget - actual, 2)})

    top_cat = max(by_category, key=by_category.get)
    suggestions = [
        f"You spend most on {top_cat}. Try a weekly cap for this category.",
        "Automate savings right after salary credit to improve consistency.",
    ]
    if any(row["variance"] < 0 for row in budget_vs_actual):
        suggestions.append("You crossed at least one budget this month. Reduce non-essential spend by 10%.")

    return jsonify({
        "by_category": by_category,
        "monthly_totals": monthly_totals.to_dict(),
        "predicted_next_month": predicted,
        "budget_vs_actual": budget_vs_actual,
        "suggestions": suggestions,
    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
