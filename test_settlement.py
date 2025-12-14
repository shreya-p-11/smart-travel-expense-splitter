from settlement import optimize_settlements

balances = {
    "P001": {"net_balance": 700},
    "P002": {"net_balance": -200},
    "P003": {"net_balance": -500}
}

transactions = optimize_settlements(balances)

for t in transactions:
    print(f"{t['from_participant']} pays {t['to_participant']} ₹{t['amount']}")
