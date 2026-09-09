#!/usr/bin/env python3
"""
LM Studio auto-detect proxy. Listens on 127.0.0.1:1235.
Replaces model="__auto__" with the model currently loaded in LM Studio.
Parallel probing — fast (<3s even with many models).
"""
import http.server, urllib.request, json, threading, time, sys, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

LMSTUDIO_BASE = "http://localhost:1234"
LISTEN_PORT = 1235
_cached_model = None
_cache_time = 0
_lock = threading.Lock()
CACHE_TTL = 30

def _probe(name):
    t0 = time.time()
    try:
        req = urllib.request.Request(
            f"{LMSTUDIO_BASE}/v1/chat/completions",
            data=json.dumps({
                "model": name, "messages": [{"role": "user", "content": "."}],
                "max_tokens": 1, "temperature": 0
            }).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=4)
        return name, time.time() - t0
    except Exception:
        return None, 999


def detect_loaded_model():
    global _cached_model, _cache_time
    with _lock:
        now = time.time()
        if _cached_model and (now - _cache_time) < CACHE_TTL:
            return _cached_model

    try:
        req = urllib.request.Request(f"{LMSTUDIO_BASE}/v1/models")
        models = json.loads(urllib.request.urlopen(req, timeout=5).read())
    except Exception:
        with _lock:
            return _cached_model

    candidates = [m["id"] for m in models["data"] if "embed" not in m["id"].lower()]
    if not candidates:
        return None

    # Parallel probe — loaded model responds in <1s, wins immediately
    with ThreadPoolExecutor(max_workers=len(candidates)) as ex:
        futures = {ex.submit(_probe, name): name for name in candidates}
        for future in as_completed(futures):
            name, elapsed = future.result()
            if name and elapsed < 2.0:
                with _lock:
                    _cached_model = name
                    _cache_time = time.time()
                print(f"[proxy] Detected: {name} ({elapsed:.1f}s)", file=sys.stderr)
                # Cancel remaining probes
                for f in futures:
                    f.cancel()
                return name

    # Fallback: any that worked at all
    for future in as_completed(futures):
        name, elapsed = future.result()
        if name:
            with _lock:
                _cached_model = name
                _cache_time = time.time()
            return name

    with _lock:
        return _cached_model


class ThreadingHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if data.get("model") == "__auto__":
            detected = detect_loaded_model()
            if not detected:
                self.send_error(503, "No model detected in LM Studio. Is one loaded?")
                return
            data["model"] = detected

        try:
            req = urllib.request.Request(
                f"{LMSTUDIO_BASE}{self.path}",
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=300)
            self.send_response(resp.status)
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(k, v)
            self.end_headers()
            chunk = resp.read()
            self.wfile.write(chunk)
        except urllib.error.HTTPError as e:
            body_err = e.read()
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(body_err)
        except Exception as e:
            self.send_error(502, str(e))

    def do_GET(self):
        try:
            req = urllib.request.Request(f"{LMSTUDIO_BASE}{self.path}")
            resp = urllib.request.urlopen(req, timeout=10)
            self.send_response(resp.status)
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, fmt, *args):
        pass


def main():
    global LMSTUDIO_BASE, LISTEN_PORT
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1235)
    parser.add_argument("--lmstudio", default="http://localhost:1234")
    args = parser.parse_args()
    LISTEN_PORT = args.port
    LMSTUDIO_BASE = args.lmstudio.rstrip("/")

    # Background warmup thread
    threading.Thread(target=detect_loaded_model, daemon=True).start()

    server = ThreadingHTTPServer(("127.0.0.1", LISTEN_PORT), ProxyHandler)
    print(f"[proxy] Ready: http://127.0.0.1:{LISTEN_PORT} → {LMSTUDIO_BASE}", file=sys.stderr)
    print(f"[proxy] Use model='__auto__' in Hermes alias", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()