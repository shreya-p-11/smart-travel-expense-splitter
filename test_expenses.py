from participants import add_participant
from expenses import add_expense, get_expenses

TRIP_ID = "trip_test_expenses"

# Add participants
add_participant(TRIP_ID, "Alice", "2025-12-01")   # P001
add_participant(TRIP_ID, "Bob", "2025-12-01")     # P002
add_participant(TRIP_ID, "Charlie", "2025-12-01") # P003

# Add expenses
add_expense(
    trip_id=TRIP_ID,
    payer_id="P001",
    amount=1500,
    category="hotel",
    beneficiaries=["P001", "P002", "P003"],
    date="2025-12-01",
    note="Hotel booking"
)

add_expense(
    trip_id=TRIP_ID,
    payer_id="P002",
    amount=600,
    category="food",
    beneficiaries=["P001", "P002"],
    date="2025-12-01",
    note="Dinner"
)

# Print expenses
expenses = get_expenses(TRIP_ID)
for e in expenses:
    print(e.expense_id, e.category, e.amount, e.beneficiaries)
