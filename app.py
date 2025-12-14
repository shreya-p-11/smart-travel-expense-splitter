from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import re
from collections import defaultdict

# Backend imports (DO NOT MODIFY THESE FILES)
from participants import add_participant, get_participants
from expenses import add_expense, get_expenses, VALID_CATEGORIES
from splitter import calculate_balances
from settlement import optimize_settlements
from analytics import generate_analytics
from config.firebase_config import get_db

app = Flask(__name__)

ACTIVE_TRIP = {
    "trip_id": None,
    "trip_name": None
}

# ------------------ HELPERS ------------------

def generate_trip_id(trip_name):
    trip_id = trip_name.lower().strip()
    trip_id = re.sub(r"\s+", "_", trip_id)
    trip_id = re.sub(r"[^a-z0-9_]", "", trip_id)
    return f"{trip_id}_{date.today().strftime('%Y%m%d')}"

def participant_map(participants):
    return {p.participant_id: p.name for p in participants}

def explain_participant_expenses(participant_id, expenses, id_to_name):
    explanation = []
    total_paid = 0
    total_share = 0

    for e in expenses:
        if participant_id in e.beneficiaries:
            share = e.amount / len(e.beneficiaries)
            total_share += share

            explanation.append({
                "expense_id": e.expense_id,
                "category": e.category,
                "amount": e.amount,
                "beneficiaries": len(e.beneficiaries),
                "share": round(share, 2),
                "payer": id_to_name.get(e.payer_id, e.payer_id)
            })

        if e.payer_id == participant_id:
            total_paid += e.amount

    return {
        "details": explanation,
        "total_paid": round(total_paid, 2),
        "total_share": round(total_share, 2),
        "net": round(total_paid - total_share, 2)
    }

# ------------------ ROUTES ------------------

@app.route("/")
def index():
    trip_id = ACTIVE_TRIP["trip_id"]

    participants = []
    expenses = []
    summary = []
    settlements_named = []
    warnings = []

    analytics = {
        "category_breakdown": {},
        "daily_spending": {}
    }

    explanations = {}


    if trip_id:
        participants = get_participants(trip_id)
        expenses = get_expenses(trip_id)

        id_to_name = participant_map(participants)
        payer_name_map = id_to_name

        if expenses:
            balances = calculate_balances(
                [vars(p) for p in participants],
                [vars(e) for e in expenses]
            )

            settlements = optimize_settlements(balances)

            for s in settlements:
                settlements_named.append({
                    "from": id_to_name.get(s["from_participant"]),
                    "to": id_to_name.get(s["to_participant"]),
                    "amount": s["amount"]
                })

            analytics_result = generate_analytics(
                [vars(p) for p in participants],
                [vars(e) for e in expenses]
            )

            analytics = analytics_result.get("analytics", {
    "category_breakdown": {},
    "daily_spending": {}
})
            warnings = analytics_result.get("warnings", [])

            for pid, data in balances.items():
                net = data["net_balance"]
                summary.append({
                    "name": id_to_name.get(pid),
                    "paid": round(data["total_paid"], 2),
                    "share": round(data["total_share"], 2),
                    "net": round(net, 2)
                })

            for p in participants:
                explanations[p.name] = explain_participant_expenses(
                    p.participant_id, expenses, id_to_name
                )

    return render_template(
        "index.html",
        trip_id=trip_id,
        participants=participants,
        expenses=expenses,
        summary=summary,
        settlements=settlements_named,
        analytics=analytics,
        warnings=warnings,
        explanations=explanations,
        categories=VALID_CATEGORIES
        payer_name_map=payer_name_map,

    )

# ------------------ CREATE TRIP ------------------

@app.route("/create-trip", methods=["POST"])
def create_trip():
    trip_name = request.form["trip_name"]
    names = [n.strip() for n in request.form["participants"].split(",") if n.strip()]
    start_date = request.form["start_date"]
    duration = request.form["duration"]

    trip_id = generate_trip_id(trip_name)

    db = get_db()
    db.collection("trips").document(trip_id).set({
        "trip_name": trip_name,
        "start_date": start_date,
        "duration": duration,
        "created_at": str(date.today())
    })

    for name in names:
        add_participant(trip_id, name, start_date)

    ACTIVE_TRIP["trip_id"] = trip_id
    ACTIVE_TRIP["trip_name"] = trip_name

    return redirect(url_for("index"))

# ------------------ ADD EXPENSE ------------------

@app.route("/add-expense", methods=["POST"])
def add_exp():
    trip_id = ACTIVE_TRIP["trip_id"]

    category = request.form["category"]
    payer_id = request.form["payer"]
    amount = float(request.form["amount"])
    expense_date = request.form.get("expense_date", str(date.today()))
    note = request.form.get("note")

    beneficiaries = request.form.getlist("beneficiaries")

    add_expense(
        trip_id=trip_id,
        payer_id=payer_id,
        amount=amount,
        category=category,
        beneficiaries=beneficiaries,
        date=expense_date,
        note=note
    )

    return redirect(url_for("index"))

# ------------------ EXPORT ------------------

@app.route("/export")
def export():
    trip_id = ACTIVE_TRIP["trip_id"]
    expenses = get_expenses(trip_id)

    lines = ["Category,Amount,Paid By,Date"]
    for e in expenses:
        lines.append(f"{e.category},{e.amount},{e.payer_id},{e.date}")

    return "\n".join(lines), 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=trip_report.csv"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
