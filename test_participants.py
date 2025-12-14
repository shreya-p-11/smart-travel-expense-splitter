from participants import add_participant, get_participants

TRIP_ID = "trip_test_ids"

add_participant(TRIP_ID, "Alice", "2025-12-01")
add_participant(TRIP_ID, "Bob", "2025-12-01")
add_participant(TRIP_ID, "Charlie", "2025-12-02")

for p in get_participants(TRIP_ID):
    print(p.participant_id, p.name)
