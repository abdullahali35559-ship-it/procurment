def mock_frontend_search(emails, search_term):
    search_term = search_term.lower()
    filtered = []
    for email in emails:
        matches_search = (
            (email.get('sender') or email.get('from') or '').lower().find(search_term) != -1 or
            (email.get('subject') or '').lower().find(search_term) != -1 or
            (email.get('body') or '').lower().find(search_term) != -1 or
            (email.get('tender_id') or '').lower().find(search_term) != -1
        )
        if matches_search:
            filtered.append(email)
    return filtered

# Test data
test_emails = [
    {
        "id": 190,
        "subject": "Invitation to Bid – High-Rise Commercial Tower (G+22) | TND-2026-00002",
        "tender_id": "TND-2026-00013",
        "sender": "example@domain.com"
    },
    {
        "id": 191,
        "subject": "Invitation to Bid: Industrial Warehouse Construction - TND-2026-00001",
        "tender_id": "TND-2026-00014",
        "sender": "example@domain.com"
    }
]

print("--- Testing Search for TND-2026-00013 ---")
results = mock_frontend_search(test_emails, "TND-2026-00013")
for r in results:
    print(f"Found: {r['id']} - {r['subject']}")

print("\n--- Testing Search for TND-2026-00014 ---")
results = mock_frontend_search(test_emails, "TND-2026-00014")
for r in results:
    print(f"Found: {r['id']} - {r['subject']}")
