import requests

PAGES = [
    "/index.html",
    "/calendar.html",
    "/attachments.html",
    "/threads.html",
    "/drafts.html",
    "/settings.html",
    "/css/components.css",
    "/js/api.js"
]

BASE_URL = "http://127.0.0.1:8000"

def test_pages():
    print("=== Executive AI Assistant: Static Page Access Audit ===")
    for page in PAGES:
        try:
            url = f"{BASE_URL}{page}"
            res = requests.head(url, timeout=5)
            print(f"[{'OK' if res.status_code == 200 else 'FAIL'}] {page} (Status: {res.status_code})")
        except Exception as e:
            print(f"[ERROR] {page}: {e}")

if __name__ == "__main__":
    test_pages()
