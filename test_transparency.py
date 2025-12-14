from utils import explain_participant_share
from splitter import calculate_balances

participants = [
    {"participant_id": "P001", "name": "Alice", "start_date": "2025-12-01", "end_date": None},
    {"participant_id": "P002", "name": "Bob", "start_date": "2025-12-01", "end_date": None},
    {"participant_id": "P003", "name": "Charlie", "start_date": "2025-12-02", "end_date": None},
]

expenses = [
    {
        "expense_id": "E001",
        "payer_id": "P001",
        "amount": 1500,
        "category": "hotel",
        "beneficiaries": ["P001", "P002", "P003"],
        "date": "2025-12-02"
    },
    {
        "expense_id": "E002",
        "payer_id": "P002",
        "amount": 600,
        "category": "food",
        "beneficiaries": ["P001", "P002"],
        "date": "2025-12-01"
    }
]

balances = calculate_balances(participants, expenses)

explanation = explain_participant_share(
    "P001",
    participants,
    expenses,
    balances
)

print(explanation)
