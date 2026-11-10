"""Shared helpers: auth check, ChargePoint client, JSON responses.

NOTE: python-chargepoint method names are unverified against the installed
version. Calls are wrapped so failures return a clear error instead of crashing.
"""
import json
import os
import time

_client = None
_client_ts = 0
CLIENT_TTL = 600  # re-login every 10 minutes at most


def authorized(headers):
    secret = os.environ.get("APP_PASSCODE", "")
    return bool(secret) and headers.get("X-Passcode", "") == secret


def client():
    global _client, _client_ts
    if _client is None or time.time() - _client_ts > CLIENT_TTL:
        from python_chargepoint import ChargePoint
        _client = ChargePoint(os.environ["CP_USERNAME"], os.environ["CP_PASSWORD"])
        _client_ts = time.time()
    return _client


def favorites():
    return [s.strip() for s in os.environ.get("FAVORITE_STATION_IDS", "").split(",") if s.strip()]


def to_plain(obj):
    """Best-effort conversion of library objects to JSON-safe data."""
    return json.loads(json.dumps(obj, default=lambda o: getattr(o, "__dict__", str(o))))


def send(handler, code, payload, cache=0):
    body = json.dumps(payload).encode()
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    if cache:
        handler.send_header("Cache-Control", f"s-maxage={cache}")
    handler.end_headers()
    handler.wfile.write(body)
