#!/bin/sh
# Serve the built game (repo root) on http://127.0.0.1:8765 for the test tools. Safe to run twice.
cd "$(dirname "$0")/.." || exit 1
curl -s -o /dev/null -m 3 http://127.0.0.1:8765/ 2>/dev/null && exit 0
setsid nohup python3 -c "
import http.server,socketserver
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
class S(socketserver.ThreadingMixIn,http.server.HTTPServer):daemon_threads=True;allow_reuse_address=True
S(('127.0.0.1',8765),H).serve_forever()" >/dev/null 2>&1 </dev/null &
sleep 1
