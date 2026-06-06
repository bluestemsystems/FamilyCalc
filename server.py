#!/usr/bin/env python3
"""
Family Calculator - local save server (Windows build).

Serves index.html (and the logo images) over http://127.0.0.1:8765/ and accepts
POST /save to write the page back to disk, so auto-save works in every browser.

This is also the entry point for the packaged FamilyCalc.exe (PyInstaller). When
frozen, the app's files are bundled read-only inside the exe, so on first run we
copy the default index.html + logos into a writable data folder
(%LOCALAPPDATA%\\FamilyCalc) and serve/save there. That way your data persists
across launches, and updating the exe never overwrites it.

Bound to 127.0.0.1 only, so nothing on your network can reach it.
"""

import http.server
import os
import shutil
import socket
import socketserver
import sys
import threading
import webbrowser

PORT = 8765
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}/"

# Files the app ships with / needs in the data folder.
ASSETS = ("index.html",)
# Only this file may be written by /save.
SAVABLE = {"index.html"}


def resolve_dirs():
    """Return (bundle_dir, data_dir).

    bundle_dir holds the read-only shipped copy of the assets.
    data_dir is writable and is what we actually serve and save.
    """
    if getattr(sys, "frozen", False):
        bundle = sys._MEIPASS  # PyInstaller extraction dir (read-only)
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        data = os.path.join(base, "FamilyCalc")
    else:
        bundle = os.path.dirname(os.path.abspath(__file__))
        data = bundle
    os.makedirs(data, exist_ok=True)
    # Seed the data folder on first run (never overwrite existing data).
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
        # Atomic write: temp file then replace, so a crash can't half-write.
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
    """True if something is already listening on our port (another instance)."""
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
    # --serve-only: start the server without opening a browser. Used by the
    # login auto-start so logging in doesn't pop a browser window every time.
    open_browser = "--serve-only" not in sys.argv
    # If a copy is already serving (e.g. started at login), just open the app.
    if already_running():
        if open_browser:
            webbrowser.open(URL)
        return
    if not os.path.exists(INDEX):
        sys.exit(f"index.html not found (data folder: {DATA_DIR})")
    try:
        httpd = Server((HOST, PORT), Handler)
    except OSError:
        # Lost a race - someone else grabbed the port. Just open the app.
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
