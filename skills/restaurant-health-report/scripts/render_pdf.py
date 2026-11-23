#!/usr/bin/env python3
"""Render report.html to PDF and check that nothing overflowed.

Usage:
    python3 render_pdf.py path/to/report.html [-o out.pdf] [--preview]

Uses Google Chrome / Chromium / Microsoft Edge in headless mode (most laptops
already have one). Falls back to WeasyPrint if no browser is found.

Checks:
  * layout: measures every page in Chrome and fails if any content runs into the
    sources line / footer, past the right margin, or out of the cover title block.
  * the PDF page count equals the expected count written by build_report.py.
--preview also writes preview.png (all pages stacked) so you can look at it.
Exit code 0 = OK, 1 = render failed, 2 = overflow (text too long somewhere).
"""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = {
    "Darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ],
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "Linux": [],
}
PATH_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "chrome"]


def find_browser():
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for c in CANDIDATES.get(platform.system(), []):
        if Path(c).exists():
            return c
    if platform.system() == "Windows":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            c = Path(local) / "Google/Chrome/Application/chrome.exe"
            if c.exists():
                return str(c)
    for n in PATH_NAMES:
        p = shutil.which(n)
        if p:
            return p
    return None


def count_pages(pdf: Path):
    try:
        from pypdf import PdfReader  # optional
        return len(PdfReader(str(pdf)).pages)
    except Exception:
        pass
    data = pdf.read_bytes()
    counts = [int(m) for m in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data, re.S)]
    counts += [int(m) for m in re.findall(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", data, re.S)]
    if counts:
        return max(counts)
    return len(re.findall(rb"/Type\s*/Page\b(?!s)", data))


def chrome_pdf(browser, html: Path, pdf: Path):
    with tempfile.TemporaryDirectory() as prof:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               f"--user-data-dir={prof}", "--no-pdf-header-footer", "--virtual-time-budget=8000",
               f"--print-to-pdf={pdf}", html.resolve().as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return pdf.exists() and pdf.stat().st_size > 1000, r.stderr[-800:]


def chrome_png(browser, html: Path, png: Path, pages: int):
    with tempfile.TemporaryDirectory() as prof:
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}",
               f"--window-size=816,{1056 * pages}", "--virtual-time-budget=8000", f"--screenshot={png}", html.resolve().as_uri()]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return png.exists()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    html = Path(a.html)
    pdf = Path(a.out) if a.out else html.with_suffix(".pdf")
    m = re.search(r'name="expected-pages" content="(\d+)"', html.read_text(encoding="utf-8", errors="ignore"))
    expected = int(m.group(1)) if m else None
    if pdf.exists():
        pdf.unlink()

    browser = find_browser()
    ok, err, engine = False, "", None
    if browser:
        ok, err = chrome_pdf(browser, html, pdf)
        engine = Path(browser).name
    if not ok and shutil.which("weasyprint"):
        r = subprocess.run(["weasyprint", str(html), str(pdf)], capture_output=True, text=True)
        ok, err, engine = pdf.exists(), r.stderr[-800:], "weasyprint"
    if not ok:
        print("RENDER FAILED. Install Google Chrome (or set CHROME_PATH to a Chrome/Edge binary), then rerun.")
        if err:
            print(err)
        sys.exit(1)

    overflow = None
    if browser:
        with tempfile.TemporaryDirectory() as prof:
            r = subprocess.run([browser, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", "--window-size=1000,1400",
                                "--virtual-time-budget=8000", "--dump-dom", html.resolve().as_uri()], capture_output=True, text=True, timeout=120)
        m2 = re.search(r'data-overflow="([^"]*)"', r.stdout)
        overflow = m2.group(1) if m2 else None
    pages = count_pages(pdf)
    print(f"Wrote {pdf} with {engine}: {pages} pages" + (f" (expected {expected})" if expected else ""))
    if a.preview and browser:
        png = pdf.with_name("preview.png")
        if chrome_png(browser, html, png, expected or pages or 7):
            print(f"Preview image: {png}")
    if overflow and overflow != "none":
        print("OVERFLOW: " + overflow.replace("&quot;", '"').replace(" | ", "\n          "))
        print("Shorten the text on those pages (the dek, a long fact row, a card or a fix), rebuild, rerender.")
        sys.exit(2)
    if overflow is None and browser:
        print("Note: could not run the layout check; look at every page yourself.")
    if expected and pages != expected:
        print("PAGE COUNT MISMATCH: some section is too long and spilled onto an extra page. "
              "Shorten text on the crowded page (usually the dek, a fact row, or a card), rebuild, rerender.")
        sys.exit(2)
    print("OK")


if __name__ == "__main__":
    main()
