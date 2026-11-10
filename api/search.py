import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(__file__))
import _cp  # noqa: E402

# Unverified: candidate method names for a location search in python-chargepoint.
CANDIDATES = ("search_stations", "get_nearby_stations", "get_stations_nearby", "find_stations", "search")


def pick(obj, *keys):
    for k in keys:
        v = obj.get(k) if isinstance(obj, dict) else getattr(obj, k, None)
        if v not in (None, ""):
            return v
    return None


def normalize(item):
    plain = _cp.to_plain(item)
    sid = pick(plain, "id", "station_id", "deviceId", "device_id")
    name = pick(plain, "name", "station_name", "stationName", "address")
    return {"id": str(sid) if sid is not None else None, "name": str(name) if name else "", "raw": plain}


class NoSearch(Exception):
    pass


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not _cp.authorized(self.headers):
            return _cp.send(self, 401, {"error": "Invalid passcode"})
        q = parse_qs(urlparse(self.path).query)
        try:
            lat, lng = float(q["lat"][0]), float(q["lng"][0])
        except (KeyError, ValueError):
            return _cp.send(self, 400, {"error": "lat and lng are required"})

        async def work(cp):
            method = next((getattr(cp, n) for n in CANDIDATES if hasattr(cp, n)), None)
            if method is None:
                available = sorted(n for n in dir(cp) if not n.startswith("_"))
                raise NoSearch(", ".join(available))
            return await _cp.maybe_await(method(lat, lng))

        try:
            found = _cp.run(work)
            results = [normalize(r) for r in (found or [])][:25]
            _cp.send(self, 200, {"results": [r for r in results if r["id"]]})
        except NoSearch as e:
            _cp.send(self, 501, {
                "error": "No station search found in python-chargepoint. Available methods: " + str(e)})
        except Exception as e:
            _cp.send(self, 502, {"error": f"Search failed: {e}"})
