#!/usr/bin/env python3
"""
Family Calculator - local save server (macOS build).

Serves index.html (and saves it back via POST /save) over
http://127.0.0.1:8765/, so auto-save works in any browser.

This is also the entry point for the packaged "Family Calculator.app"
(PyInstaller). When frozen, the app's files are bundled read-only inside the
app, so on first run we copy the default index.html into a writable data folder
(~/Library/Application Support/FamilyCalc) and serve/save there. That way your
data persists across launches and app updates never overwrite it.

Bound to 127.0.0.1 only, so nothing on your network can reach it.

The port can be overridden for testing with FAMILYCALC_PORT.
"""

import http.server
import os
import shutil
import socket
import socketserver
import sys
import threading
import webbrowser

PORT = int(os.environ.get("FAMILYCALC_PORT", "8765"))
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}/"

ASSETS = ("index.html",)
SAVABLE = {"index.html"}


def resolve_dirs():
    """Return (bundle_dir, data_dir): a read-only shipped copy, and a writable
    folder that we actually serve and save to."""
    if getattr(sys, "frozen", False):
        bundle = sys._MEIPASS  # PyInstaller extraction dir (read-only)
        home = os.path.expanduser("~")
        if sys.platform == "darwin":
            data = os.path.join(home, "Library", "Application Support", "FamilyCalc")
        elif os.name == "nt":
            base = os.environ.get("LOCALAPPDATA") or home
            data = os.path.join(base, "FamilyCalc")
        else:
            data = os.path.join(home, ".familycalc")
    else:
        bundle = os.path.dirname(os.path.abspath(__file__))
        data = bundle
    os.makedirs(data, exist_ok=True)
    if bundle != data:
        for name in ASSETS:
            src, dst = os.path.join(bundle, name), os.path.join(data, name)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
    return bundle, data


BUNDLE_DIR, DATA_DIR = resolve_dirs()
INDEX = os.path.join(DATA_DIR, "index.html")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DATA_DIR, **kwargs)

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            self.send_error(400, "Empty body")
            return
        body = self.rfile.read(length)
        tmp = INDEX + ".tmp"
        try:
            with open(tmp, "wb") as f:
                f.write(body)
            os.replace(tmp, INDEX)
        except OSError as e:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass
            self.send_error(500, f"Save failed: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        msg = fmt % args
        if "/save" in msg or " 4" in msg or " 5" in msg:
            sys.stderr.write("  %s\n" % msg)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def already_running():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        s.connect((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        s.close()


def main():
    open_browser = "--serve-only" not in sys.argv
    if already_running():
        if open_browser:
            webbrowser.open(URL)
        return
    if not os.path.exists(INDEX):
        sys.exit(f"index.html not found (data folder: {DATA_DIR})")
    try:
        httpd = Server((HOST, PORT), Handler)
    except OSError:
        if open_browser:
            webbrowser.open(URL)
        return
    print("Family Calculator is running.")
    print(f"  Open:  {URL}")
    print(f"  Data:  {DATA_DIR}")
    print("  Auto-save writes index.html on every change. Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(URL)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        httpd.shutdown()


if __name__ == "__main__":
    main()
