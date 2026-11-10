import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(__file__))
import _cp  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if not _cp.authorized(self.headers):
            return _cp.send(self, 401, {"error": "Invalid passcode"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            station_id = json.loads(self.rfile.read(length) or b"{}").get("station_id")
            if not station_id:
                return _cp.send(self, 400, {"error": "station_id required"})
            join = getattr(_cp.client(), "join_waitlist", None)
            if join is None:
                return _cp.send(self, 501, {
                    "error": "Waitlist is not supported by this python-chargepoint version"})
            _cp.send(self, 200, {"ok": True, "result": _cp.to_plain(join(int(station_id)))})
        except Exception as e:
            _cp.send(self, 502, {"error": f"Waitlist request failed: {e}"})
