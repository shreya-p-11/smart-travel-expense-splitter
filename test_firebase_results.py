from firebase_store import (
    save_balances,
    save_settlements,
    save_analytics,
    save_explanations
)

TRIP_ID = "trip_test_results"

balances = {
    "P001": {"total_paid": 1500, "total_share": 800, "net_balance": 700},
    "P002": {"total_paid": 600, "total_share": 800, "net_balance": -200},
    "P003": {"total_paid": 0, "total_share": 500, "net_balance": -500},
}

settlements = [
    {"from_participant": "P002", "to_participant": "P001", "amount": 200},
    {"from_participant": "P003", "to_participant": "P001", "amount": 500},
]

analytics = {
    "category_breakdown": {"hotel": 1500, "food": 600},
    "daily_spending": {"2025-12-01": 2100},
    "highest_spending_day": {"date": "2025-12-01", "amount": 2100},
    "payer_totals": {"P001": 1500, "P002": 600},
    "warnings": ["P001 paid significantly more than others"]
}

explanations = {
    "P001": {"net_balance": 700, "details": "sample"},
    "P002": {"net_balance": -200, "details": "sample"},
}

save_balances(TRIP_ID, balances)
save_settlements(TRIP_ID, settlements)
save_analytics(TRIP_ID, analytics)
save_explanations(TRIP_ID, explanations)

print("Results successfully saved to Firebase")
