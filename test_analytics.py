from analytics import generate_analytics

participants = [
    {"participant_id": "P001", "name": "Alice"},
    {"participant_id": "P002", "name": "Bob"},
    {"participant_id": "P003", "name": "Charlie"},
]

expenses = [
    {"payer_id": "P001", "amount": 1500, "category": "hotel", "date": "2025-12-01"},
    {"payer_id": "P002", "amount": 600, "category": "food", "date": "2025-12-01"},
    {"payer_id": "P001", "amount": 1200, "category": "transport", "date": "2025-12-02"},
    {"payer_id": "P003", "amount": 400, "category": "food", "date": "2025-12-02"},
]

result = generate_analytics(participants, expenses)
analytics = result["analytics"]

print("Category Breakdown:", analytics["category_breakdown"])
print("Daily Spending:", analytics["daily_spending"])
print("Highest Spending Day:", analytics["highest_spending_day"])
print("Payer Totals:", analytics["payer_totals"])
print("\nWarnings:")
for w in result["warnings"]:
    print("-", w)
