import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(__file__))
import _cp  # noqa: E402


def requested_ids(path):
    raw = parse_qs(urlparse(path).query).get("ids", [""])[0]
    ids = [i.strip() for i in raw.split(",") if i.strip().isdigit()]
    return ids[:20] or _cp.favorites()  # fall back to env var if none sent


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not _cp.authorized(self.headers):
            return _cp.send(self, 401, {"error": "Invalid passcode"})
        ids = requested_ids(self.path)

        async def work(cp):
            getter = getattr(cp, "get_station", None)
            out = []
            for sid in ids:
                if getter is None:
                    out.append({"id": sid, "error": "get_station not available in this library version"})
                    continue
                try:
                    out.append({"id": sid, "data": _cp.to_plain(await _cp.maybe_await(getter(int(sid))))})
                except Exception as e:  # one bad station should not break the rest
                    out.append({"id": sid, "error": str(e)})
            return out

        try:
            _cp.send(self, 200, {"stations": _cp.run(work)})
        except Exception as e:
            _cp.send(self, 502, {"error": f"ChargePoint request failed: {e}"})
