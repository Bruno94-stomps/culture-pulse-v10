#!/usr/bin/env python3
"""Smoke test for critical backend ML endpoints."""

import os
import sys
import urllib.request
import urllib.error
import json

DEFAULT_FASTAPI_URL = "http://localhost:8000"
AUTH_TOKEN_ENV_VAR = "SMOKE_TEST_AUTH_TOKEN"
ENDPOINTS = [
    ("GET", "/api/v8/dashboard/trends?plan=free&top_n=2"),
    ("GET", "/api/v8/ml/strategy-status"),
    ("GET", "/api/v8/dashboard/emerging-profiles?plan=free&top_n=3"),
    ("POST", "/api/v8/dashboard/emerging-profiles/refresh?plan=free&top_n=3"),
    ("GET", "/api/v8/dashboard/emerging-profiles/status"),
]


def check_endpoint(base_url: str, method: str, path: str, headers: dict):
    url = base_url.rstrip("/") + path
    req = urllib.request.Request(url, headers=headers, method=method)
    if method == "POST":
        req.data = b""
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            payload = response.read(4096).decode("utf-8", errors="replace")
            data = json.loads(payload) if payload else None
            print(f"OK {status} {method} {path} -> {type(data).__name__}")
            return True
    except urllib.error.HTTPError as exc:
        print(f"FAIL {path} -> HTTP {exc.code}: {exc.reason}")
    except urllib.error.URLError as exc:
        print(f"FAIL {path} -> URL error: {exc.reason}")
    except json.JSONDecodeError as exc:
        print(f"FAIL {path} -> invalid JSON: {exc}")
    except Exception as exc:
        print(f"FAIL {path} -> unexpected: {exc}")
    return False


def get_auth_token():
    token = os.environ.get(AUTH_TOKEN_ENV_VAR)
    if not token:
        print(f"ERROR: environment variable {AUTH_TOKEN_ENV_VAR} is required for real smoke tests.")
        return None
    return token


def check_supabase_configuration():
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip() or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY/SUPABASE_SERVICE_ROLE_KEY must be configured to run real backend smoke tests.")
        return False
    print("Supabase configuration detected.")
    return True


def main():
    base_url = os.environ.get("FASTAPI_URL") or os.environ.get("NEXT_PUBLIC_FASTAPI_URL") or DEFAULT_FASTAPI_URL
    auth_token = get_auth_token()
    if not auth_token:
        sys.exit(1)

    if not check_supabase_configuration():
        sys.exit(1)

    print(f"Running smoke tests against {base_url}")
    headers = {"Authorization": f"Bearer {auth_token}"}
    results = [check_endpoint(base_url, method, path, headers) for method, path in ENDPOINTS]
    failed = [path for (method, path), ok in zip(ENDPOINTS, results) if not ok]
    if failed:
        print("\nSmoke test failed for endpoints:")
        for path in failed:
            print(f" - {path}")
        sys.exit(1)
    print("\nAll smoke endpoints passed.")


if __name__ == "__main__":
    main()
