from splitter import calculate_balances

participants = [
    {"participant_id": "P001", "start_date": "2025-12-01", "end_date": None},
    {"participant_id": "P002", "start_date": "2025-12-01", "end_date": None},
    {"participant_id": "P003", "start_date": "2025-12-02", "end_date": None},
]

expenses = [
    {
        "payer_id": "P001",
        "amount": 1500,
        "beneficiaries": ["P001", "P002", "P003"],
        "date": "2025-12-02"
    },
    {
        "payer_id": "P002",
        "amount": 600,
        "beneficiaries": ["P001", "P002"],
        "date": "2025-12-01"
    }
]

balances = calculate_balances(participants, expenses)

for pid, data in balances.items():
    print(pid, data)
