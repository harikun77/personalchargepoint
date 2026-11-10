"""Shared helpers: auth check, ChargePoint client, JSON responses.

python-chargepoint appears to be async (it needs a running event loop), so each
request builds the client and does its work inside one asyncio.run(). Method
names are unverified; calls handle both sync and async results.
"""
import asyncio
import inspect
import json
import os


def authorized(headers):
    secret = os.environ.get("APP_PASSCODE", "")
    return bool(secret) and headers.get("X-Passcode", "") == secret


def favorites():
    return [s.strip() for s in os.environ.get("FAVORITE_STATION_IDS", "").split(",") if s.strip()]


async def maybe_await(value):
    return await value if inspect.isawaitable(value) else value


async def _with_client(work):
    from python_chargepoint import ChargePoint
    user, pw = os.environ["CP_USERNAME"], os.environ["CP_PASSWORD"]
    factory = getattr(ChargePoint, "create", None)
    cp = await maybe_await(factory(user, pw)) if factory else ChargePoint(user, pw)
    try:
        return await work(cp)
    finally:
        for name in ("close", "logout", "aclose"):
            closer = getattr(cp, name, None)
            if closer:
                try:
                    await maybe_await(closer())
                except Exception:
                    pass
                break


def run(work):
    """Run `async def work(cp)` with a freshly logged-in client."""
    return asyncio.run(_with_client(work))


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
