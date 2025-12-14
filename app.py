from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import re

# Backend imports (DO NOT MODIFY THESE FILES)
from participants import add_participant, get_participants
from expenses import add_expense, get_expenses, VALID_CATEGORIES
from splitter import calculate_balances
from settlement import optimize_settlements
from analytics import generate_analytics
from config.firebase_config import get_db

app = Flask(__name__)

# In-memory active trip (simple, works for demo & Render)
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

# ------------------ ROUTES ------------------

@app.route("/")
def index():
    trip_id = ACTIVE_TRIP["trip_id"]

    participants = []
    expenses = []
    summary = []
    settlements = []
    analytics = {}
    warnings = []

    if trip_id:
        participants = get_participants(trip_id)
        expenses = get_expenses(trip_id)

        if expenses:
            balances = calculate_balances(
                [vars(p) for p in participants],
                [vars(e) for e in expenses]
            )
            settlements = optimize_settlements(balances)
            analytics_result = generate_analytics(
                [vars(p) for p in participants],
                [vars(e) for e in expenses]
            )
            analytics = analytics_result.get("analytics", {})
            warnings = analytics_result.get("warnings", [])

            id_to_name = participant_map(participants)

            for pid, data in balances.items():
                net = data["net_balance"]
                if net > 0:
                    msg = f"Gets back ₹{net:.2f}"
                    status = "positive"
                elif net < 0:
                    msg = f"Owes ₹{abs(net):.2f}"
                    status = "negative"
                else:
                    msg = "Settled"
                    status = "neutral"

                summary.append({
                    "name": id_to_name.get(pid, pid),
                    "paid": round(data["total_paid"], 2),
                    "share": round(data["total_share"], 2),
                    "message": msg,
                    "status": status
                })

    return render_template(
        "index.html",
        trip_id=trip_id,
        participants=participants,
        expenses=expenses,
        summary=summary,
        settlements=settlements,
        analytics=analytics,
        warnings=warnings,
        categories=VALID_CATEGORIES
    )

# ------------------ CREATE TRIP ------------------

@app.route("/create-trip", methods=["POST"])
def create_trip():
    trip_name = request.form["trip_name"]
    names = [n.strip() for n in request.form["participants"].split(",") if n.strip()]
    start_date = request.form["start_date"]
    duration = request.form["duration"]

    if len(names) < 2:
        return "At least two participants required", 400

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

    if not trip_id:
        return redirect(url_for("index"))

    category = request.form["category"]
    payer_id = request.form["payer"]
    amount = float(request.form["amount"])
    expense_date = request.form.get("expense_date", str(date.today()))
    note = request.form.get("note")

    participants = get_participants(trip_id)
    beneficiary_ids = [p.participant_id for p in participants]

    add_expense(
        trip_id=trip_id,
        payer_id=payer_id,
        amount=amount,
        category=category,
        beneficiaries=beneficiary_ids,
        date=expense_date,
        note=note
    )

    return redirect(url_for("index"))

# ------------------ EXPORT ------------------

@app.route("/export")
def export():
    trip_id = ACTIVE_TRIP["trip_id"]
    if not trip_id:
        return redirect(url_for("index"))

    expenses = get_expenses(trip_id)
    lines = ["Category,Amount,Payer,Date"]

    for e in expenses:
        lines.append(f"{e.category},{e.amount},{e.payer_id},{e.date}")

    return "\n".join(lines), 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=trip_report.csv"
    }

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
