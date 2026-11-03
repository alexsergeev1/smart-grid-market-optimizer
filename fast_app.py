import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from optimizer import dispatch

ROOT = Path(__file__).resolve().parent


def calculate(demand=80, line=55, solar=35):
    demand, line, solar = float(demand), float(line), float(solar)
    if not 20 <= demand <= 130 or not 0 <= line <= 120 or not 0 <= solar <= 35:
        raise ValueError("Inputs outside supported ranges")
    now = dispatch(demand, line, solar)
    baseline = dispatch(demand, max(demand, 105), solar)
    curve = []
    for capacity in range(0, 121, 5):
        imported = min(demand, capacity, solar + 70)
        peaker = demand - imported
        if peaker <= 80:
            solar_used = min(solar, imported)
            cost = solar_used * 5 + (imported - solar_used) * 30 + peaker * 115
            curve.append([capacity, round(cost, 4)])
    return {"dispatch": now, "premium": round(now["cost_usd_per_hour"] - baseline["cost_usd_per_hour"], 6), "curve": curve}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/dispatch":
            try:
                params = parse_qs(url.query)
                values = {key: float(params.get(key, [default])[0]) for key, default in (("demand", 80), ("line", 55), ("solar", 35))}
                payload, status = calculate(**values), 200
            except (ValueError, TypeError, OverflowError) as exc:
                payload, status = {"error": str(exc)}, 400
            self.send_json(payload, status)
        elif url.path in ("/", "/grid_dashboard.html"):
            body = (ROOT / "grid_dashboard.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def send_json(self, obj, status):
        body = json.dumps(obj, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    except OSError as exc:
        raise SystemExit(f"Cannot open port 8765: {exc}. Stop any previous fast_app.py process.")
    print("\nGrid dashboard: http://127.0.0.1:8765")
    print("Stop with Ctrl+C\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
