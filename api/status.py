import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(__file__))
import _cp  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not _cp.authorized(self.headers):
            return _cp.send(self, 401, {"error": "Invalid passcode"})
        try:
            cp = _cp.client()
            stations = []
            for sid in _cp.favorites():
                getter = getattr(cp, "get_station", None)
                if getter is None:
                    stations.append({"id": sid, "error": "get_station not available in this library version"})
                    continue
                try:
                    stations.append({"id": sid, "data": _cp.to_plain(getter(int(sid)))})
                except Exception as e:  # one bad station should not break the rest
                    stations.append({"id": sid, "error": str(e)})
            _cp.send(self, 200, {"stations": stations}, cache=30)
        except Exception as e:
            _cp.send(self, 502, {"error": f"ChargePoint request failed: {e}"})
