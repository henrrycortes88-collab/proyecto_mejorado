import requests
import time

BASE_URL = "http://localhost:8080"

def test_security_headers():
    print("Testing Security Headers...")
    try:
        response = requests.get(f"{BASE_URL}/login")
        headers = response.headers
        expected_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection', 'Strict-Transport-Security', 'Content-Security-Policy']
        for h in expected_headers:
            if h in headers:
                print(f"[OK] {h}: {headers[h]}")
            else:
                print(f"[FAIL] {h} is missing!")
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")

def test_rate_limiting():
    print("\nTesting Rate Limiting on /login (POST)...")
    # Limiter is set to 10 per minute
    for i in range(12):
        response = requests.post(f"{BASE_URL}/login", data={"username": "test", "password": "test"})
        if response.status_code == 429:
            print(f"[OK] Rate limit triggered at request {i+1}")
            return
        time.sleep(0.1)
    print("[FAIL] Rate limit not triggered")

def test_csrf_protection():
    print("\nTesting CSRF Protection on /login (POST)...")
    # POST without CSRF token should fail with 400 or 403
    response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "wrong_password"})
    if response.status_code in [400, 403]:
        print(f"[OK] Request without CSRF token blocked (Status: {response.status_code})")
    else:
        print(f"[FAIL] Request without CSRF token allowed or returned unexpected status: {response.status_code}")

if __name__ == "__main__":
    print("Starting Security Verification...")
    test_security_headers()
    test_csrf_protection()
    # test_rate_limiting() # Uncomment if you want to test rate limiting (slows down further tests)
    print("\nVerification Script Completed.")
