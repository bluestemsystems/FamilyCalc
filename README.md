# Family Calculator

**Family Calculator** is a configurable bill and cash-flow calculator for your household. You enter your starting balance, your bills, and your income, and it projects a **running balance** forward month by month — so you can see at a glance where your money lands on any given day and get a warning before it dips too low. Everything is fully editable: add, remove, or change bills and income (with bi-weekly, twice-monthly, or monthly schedules) and the projection updates instantly. It also includes a **chores tab** for tracking kids' chore hours and allowances.

It runs in your web browser, and a tiny local helper (`server.py`, Python standard library only) saves your data straight to disk — in **any** browser (Firefox, Chrome, Edge, or Safari). Your data never leaves your computer.

## Download

Grab the latest version from the [**Releases page**](../../releases/latest):

- **Windows** — `FamilyCalc-Setup.exe` (installer)
- **macOS** — `FamilyCalc-Mac.zip` (universal app, Intel + Apple Silicon)

Both are unsigned, so on first launch your system will warn you:
- **Windows:** SmartScreen → **More info → Run anyway**
- **macOS:** right-click the app → **Open** → **Open** (or System Settings → Privacy & Security → **Open Anyway**)

## Tabs

### Family Details
- Enter a **starting balance** and **as-of date**, then project cash flow up to 36 months ahead
- Collapsible month-by-month projection table with running balance after each transaction
- **Alert banners** warn when the balance is projected to drop below $100 or $50, with click-to-scroll navigation to the offending row
- End-of-month summary grid for a quick balance-at-a-glance across all projected months
- Manage recurring **Bills** (name, amount, due day of month)
- Manage **Income** sources with three cadences: bi-weekly (anchored to a start date), twice-a-month (two specific days), or monthly
- Collapsible **Debts & Credit** table tracking balance, interest rate, minimum payment, credit line, and estimated payoff date

### Chores
- **Add or remove kids** and rename them inline
- Set a **rate per hour**, then track each kid's chore hours for a two-week pay period
- Per-kid cards show chore name, hours logged, and dollar value at the current rate
- **Deductions** (e.g. phone bill share, internet) are subtracted from gross to show a net allowance
- Total household payout shown in the header bar

## Windows version

This folder is the **Windows** build of Family Calculator. It packages into a
single `FamilyCalc.exe` with a real installer (Start Menu shortcut + optional
login auto-start), so it behaves like a normal installed program.

### Building the .exe (do this once, on a Windows PC)

The `.exe` must be built on Windows — PyInstaller does not cross-compile from a Mac.

1. Install **Python 3** from <https://www.python.org/downloads/> (tick "Add Python to PATH" during setup).
2. Double-click **`build.bat`**. It installs PyInstaller and produces **`dist\FamilyCalc.exe`** — a single self-contained app (Python is bundled inside; users don't need Python installed).

You can ship `dist\FamilyCalc.exe` on its own, or wrap it in an installer (next).

### Making the installer (optional, recommended)

1. Install **Inno Setup** (free) from <https://jrsoftware.org/isdl.php>.
2. Open **`FamilyCalc.iss`** in Inno Setup and click **Compile**.
3. It produces **`Output\FamilyCalc-Setup.exe`** — a normal Windows installer that
   adds a Start Menu (and optional Desktop) shortcut, an entry in Add/Remove
   Programs, and an optional **"start at login"** option (server only, no browser
   pop-up). Installs per-user, so no admin prompt.

### Using it

- Launch **Family Calculator** from the Start Menu / Desktop (or just run `FamilyCalc.exe`). It starts the local save server if needed, then opens your **default browser**.
- Or **bookmark `http://127.0.0.1:8765/`** — if login auto-start is enabled, that bookmark works any time, in any browser.

First launch may show a **SmartScreen** warning since the `.exe` is unsigned —
click **More info → Run anyway**.

### Run without building (any machine with Python)

`python server.py` (or `py server.py`) launches the save server and opens the app — handy for testing before you package.

### Where your data lives

When run as the packaged `.exe`, your data file is created at
**`%LOCALAPPDATA%\FamilyCalc\index.html`** (writable, persists across updates).
When run as a plain script, it uses `index.html` in this folder. Uninstalling
leaves your data folder untouched.

## macOS version

The Mac build lives in [`mac/`](mac/) and packages into a single
**Family Calculator.app** — Python is bundled inside, so users need nothing installed.

### Building the app (on a Mac)

1. Install **Python 3** from <https://www.python.org/downloads/> (the python.org build is *universal2*, which lets one app run on both Intel and Apple Silicon).
2. `pip3 install pyinstaller`
3. `bash mac/build_mac.sh`

This produces `mac/dist/Family Calculator.app` and `mac/FamilyCalc-Mac.zip` (the
distributable). The app is ad-hoc signed automatically so it launches; it is not
notarized, so first-run still needs right-click → **Open**.

Data is stored at **`~/Library/Application Support/FamilyCalc/index.html`**.

## Data Persistence

State is always mirrored to the browser's `localStorage` on every change. Beyond that, **how it writes to disk depends on how the page is opened:**

- **Served by `server.py` (the `http://127.0.0.1:8765/` address) — recommended.** Auto-save is on automatically. Every change (~800ms after you stop editing) is POSTed back and written to `index.html` on disk. Works identically in **every** browser. The server is localhost-only and writes atomically (temp file + rename).
- **Opened directly as a file (`file://…/index.html`) — fallback.** The **⬇ Save File** button uses the File System Access API (Chrome/Edge only) to write back to the file; in Firefox/Safari it falls back to downloading a copy. This is the old, Chrome-dependent path — the local server exists to replace it.

Either way, a saved `index.html` has your data baked in as the new defaults, so it's also a portable backup.

## Tech

- React 18 (UMD, via unpkg)
- Babel Standalone (JSX transpiled in-browser)
- Libre Baskerville + DM Mono (Google Fonts)
- `server.py` — Python standard-library save server (no pip installs); binds to `127.0.0.1` only; frozen-aware (writable data dir under `%LOCALAPPDATA%`)
- Windows packaging: `build.bat` (PyInstaller → `FamilyCalc.exe`), `FamilyCalc.iss` (Inno Setup → installer), `FamilyCalc.ico` (icon, generated by `build_ico.py` from `icon.swift` artwork)
- PyInstaller is the only build-time dependency; the app itself ships no third-party packages
