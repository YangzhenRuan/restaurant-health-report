#!/usr/bin/env python3
"""Build a Truvana Tech Restaurant Health Report (HTML) from a data.json file.

Usage:
    python3 build_report.py path/to/data.json [-o path/to/report.html]

The script does all the arithmetic (effective card rates, delivery markups,
commission examples) so the numbers in the report are always consistent.
It prints a summary of the computed numbers; use those exact values anywhere
the prose mentions them (cover KPIs, headlines).

Only the Python standard library is needed. Fonts and logos are embedded, so
the HTML is self-contained and renders the same in Chrome or WeasyPrint.
"""
import argparse
import base64
import html
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Every report carries these. They are part of the template, not data.json.
SITE = "https://truvanatech.com"
UTM = "utm_source=restaurant-health-report&utm_medium=pdf&utm_campaign=health-report"
FREE_TOOLS = {
    "card-fee-calculator": ("Card fee calculator", "/tools/card-fee-calculator"),
    "delivery-app-commission-calculator": ("Delivery app commission calculator", "/tools/delivery-app-commission-calculator"),
    "credit-card-surcharge-checker": ("Surcharge and cash discount checker", "/tools/credit-card-surcharge-checker"),
    "processor-contract-exit-cost": ("Processor contract exit cost calculator", "/tools/processor-contract-exit-cost"),
    "cash-discount-sign-maker": ("Cash discount sign maker", "/tools/cash-discount-sign-maker"),
}
CTA_FEES = ("Free statement review",
            "Truvana Tech will read one month of your card statement with you, line by line, and show your real rate in writing. Free, in English or Spanish.",
            "/contact")
CTA_PLAN_TITLE = "Want a deeper look?"
CTA_PLAN_TEXT = ("This report is a quick check-up from public information, not a full analysis. Truvana Tech built it "
                 "from conversations with 6,000+ merchants. For a deeper look, our team is happy to meet with you, "
                 "walk through your restaurant together and suggest what to improve first.")
SIGNALS = {"strong": ("Strong signal", "sig-strong"), "some": ("Some signal", "sig-some"),
           "low": ("Low signal", "sig-low"), "unknown": ("Not enough data", "sig-unknown")}


def link(path, text=None, cls=""):
    url = f"{SITE}{path}{'&' if '?' in path else '?'}{UTM}"
    return f'<a class="{cls}" href="{esc(url)}">{esc(text or ("truvanatech.com" + (path if path != "/" else "")))}</a>'


STATUS = {
    "verified": ("t-ok", "Verified"),
    "public": ("t-ok", "Public"),
    "law": ("t-ok", "State law"),
    "verify": ("t-verify", "Verify"),
    "not_confirmed": ("t-no", "Not confirmed"),
    "not_public": ("t-no", "Not public"),
    "client": ("t-client", "From partner"),
}
TONES = {"green": "g", "orange": "o", "navy": "n"}


# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def md(s):
    """Escape text, then allow **bold** and line breaks."""
    out = esc(s)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    return out.replace("\n", "<br>")


def money(x):
    return f"${x:,.2f}"


def pct(x, digits=2):
    q = Decimal(1).scaleb(-digits)
    return f"{Decimal(repr(x + 1e-9)).quantize(q, ROUND_HALF_UP)}%"


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def need(obj, key, where):
    if key not in obj or obj[key] in (None, "", []):
        raise SystemExit(f"data.json: missing '{key}' in {where}")
    return obj[key]


# ---------------------------------------------------------------- CSS
def css():
    f = ASSETS / "fonts"
    faces = "".join(
        f"@font-face{{font-family:Inter;font-weight:{w};src:url({b64(f / f'inter-{w}.woff2', 'font/woff2')}) format('woff2')}}"
        for w in (400, 500, 600, 700, 800)
    )
    faces += f"@font-face{{font-family:Mono;font-weight:500;src:url({b64(f / 'mono-500.woff2', 'font/woff2')}) format('woff2')}}"
    return faces + r"""
:root{--navy:#021760;--navy-2:#0B2A86;--orange:#C14B10;--orange-soft:#F6E3D7;--blue:#0068D6;--cream:#F7F3EA;--paper:#FFFFFF;--body:#1B2233;--meta:#596074;--line:#E4DDCD;--green:#1E7A4C;--green-soft:#DDEFE4;--amber:#9A6200;--amber-soft:#F7EBCF}
@page{size:8.5in 11in;margin:0}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{margin:0;padding:0}
body{font-family:Inter,sans-serif;color:var(--body);font-size:9.6pt;line-height:1.45;background:var(--cream)}
.page{width:8.5in;height:11in;position:relative;overflow:hidden;break-after:page;page-break-after:always;background:var(--cream);padding:.52in .66in .8in}
.page:last-child{break-after:auto;page-break-after:auto}
.page>*{position:relative;z-index:1}
.page>.bignum{position:absolute;z-index:0;right:.62in;top:.92in;font-size:54pt;font-weight:800;color:#ECE5D5;letter-spacing:-.03em;line-height:1}
.page>.ftr{position:absolute;left:.66in;right:.66in;bottom:.4in;display:flex;justify-content:space-between;font-size:7pt;color:var(--meta);border-top:.6pt solid var(--line);padding-top:6pt}
.page>.src{position:absolute;left:.66in;right:.66in;bottom:.72in;font-size:6.6pt;color:var(--meta);line-height:1.4}
.hdr{display:flex;justify-content:space-between;align-items:center;padding-bottom:9pt;border-bottom:1.2pt solid var(--navy);margin-bottom:16pt}
.hdr img{height:20pt}
.hdr .sec{font-family:Mono,monospace;font-size:7.2pt;letter-spacing:.22em;text-transform:uppercase;color:var(--meta)}
.hdr .sec b{color:var(--orange);font-weight:500}
.eyebrow{display:flex;align-items:center;gap:8pt;font-size:7.4pt;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--orange);margin-bottom:7pt}
.eyebrow:before{content:"";display:inline-block;width:20pt;height:1pt;background:var(--orange)}
h1{font-size:21pt;line-height:1.12;letter-spacing:-.02em;color:var(--navy);font-weight:700;margin:0 0 6pt;max-width:6.2in}
.dek{color:var(--meta);font-size:9.4pt;max-width:6.6in;margin:0 0 14pt}
.lbl{font-size:6.8pt;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--meta)}
.card{background:var(--paper);border:.7pt solid var(--line);border-radius:6pt;padding:11pt 13pt}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10pt}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10pt}
.grid4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:9pt}
.kpi .v{font-size:20pt;font-weight:700;color:var(--navy);letter-spacing:-.02em;line-height:1.1;margin:5pt 0 3pt}
.kpi .v.o{color:var(--orange)}
.kpi p{margin:0;font-size:7.8pt;color:var(--meta);line-height:1.38}
.tag{display:inline-block;font-size:6.2pt;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:2pt 5pt;border-radius:3pt;white-space:nowrap}
.t-ok{background:var(--green-soft);color:var(--green)}.t-verify{background:var(--amber-soft);color:var(--amber)}.t-no{background:#E9E6F1;color:#4A3F7A}.t-client{background:#DCE8F8;color:var(--navy-2)}
table.facts{width:100%;border-collapse:collapse;font-size:8.4pt}
table.facts td{padding:6pt 0;border-bottom:.6pt solid var(--line);vertical-align:top}
table.facts td.k{width:1.35in;color:var(--meta);font-weight:500}
table.facts td.t{width:1.05in;padding-left:8pt}
.callout{display:grid;grid-template-columns:1.25in 1fr;gap:12pt;align-items:center;background:var(--navy);color:#fff;border-radius:6pt;padding:12pt 15pt}
.callout .lbl{color:#F3B48E}
.callout .q{font-size:10pt;font-weight:500;line-height:1.4}
.callout.orange{background:var(--orange)}.callout.orange .lbl{color:#FFE3D2}
.card h4{margin:0 0 4pt;font-size:7.2pt;letter-spacing:.15em;text-transform:uppercase}
.card h4.g{color:var(--green)}.card h4.o{color:var(--orange)}.card h4.n{color:var(--navy)}
.card p{margin:0;font-size:8.4pt}
.bars .row{display:grid;grid-template-columns:1.55in 1fr .75in;gap:8pt;align-items:center;margin:5.5pt 0;font-size:8pt}
.bars .track{height:7pt;background:#EFE9DC;border-radius:4pt;overflow:hidden}
.bars .fill{height:7pt;border-radius:4pt;background:var(--navy)}
.bars .fill.o{background:var(--orange)}
.bars .val{text-align:right;font-weight:700;color:var(--navy);font-variant-numeric:tabular-nums}
.bars .val.o{color:var(--orange)}
.bars .head{font-size:6.6pt;color:var(--meta);letter-spacing:.14em;font-weight:700;margin-top:0}
table.data{width:100%;border-collapse:separate;border-spacing:0;font-size:8.3pt;background:var(--paper);border:.7pt solid var(--line);border-radius:6pt;overflow:hidden}
table.data th{background:var(--navy);color:#fff;font-size:6.6pt;letter-spacing:.14em;text-transform:uppercase;text-align:right;padding:7pt 9pt;font-weight:600}
table.data th:first-child{text-align:left}
table.data td{padding:4.3pt 9pt;border-top:.6pt solid var(--line);text-align:right;font-variant-numeric:tabular-nums}
table.data td:first-child{text-align:left}
table.data tr.zero td{color:var(--meta)}
.up{color:var(--orange);font-weight:700}
.chips{display:flex;flex-wrap:wrap;gap:6pt}
.chip{background:var(--paper);border:.7pt solid var(--line);border-radius:20pt;padding:4pt 10pt;font-size:8pt;color:var(--navy);font-weight:500}
.chip.neg{border-color:#E7C3AE;color:var(--orange)}
.flow{display:grid;grid-template-columns:1fr 12pt 1fr 12pt 1fr 12pt 1fr;align-items:stretch}
.flow .st{background:var(--paper);border:.7pt solid var(--line);border-radius:6pt;padding:8pt 9pt;text-align:center}
.flow .st .lbl{font-size:6.2pt}
.flow .st b{display:block;color:var(--navy);font-size:8.6pt;margin-top:3pt}
.flow .st span{display:block;font-size:7pt;color:var(--meta);margin-top:2pt}
.flow .st.weak{border-style:dashed;border-color:#D5A486}
.flow .ar{display:flex;align-items:center;justify-content:center;color:var(--orange);font-weight:700}
.step{display:grid;grid-template-columns:26pt 1fr;gap:12pt;margin-bottom:8pt;align-items:start}
.step .n{align-self:start;width:26pt;height:26pt;border-radius:50%;background:var(--navy);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:12pt}
.step h3{margin:2pt 0 3pt;color:var(--navy);font-size:11pt;letter-spacing:-.01em}
.step p{margin:0 0 4pt;font-size:8.3pt}
.measure{background:var(--paper);border:.7pt solid var(--line);border-radius:5pt;padding:6pt 9pt;font-size:7.7pt;color:var(--meta)}
.measure b{color:var(--navy)}
ol.qs{margin:0;padding:0;list-style:none;counter-reset:q}
ol.qs li{counter-increment:q;display:grid;grid-template-columns:12pt 1fr;gap:4pt;font-size:7.8pt;margin:0 0 4pt}
ol.qs li:before{content:counter(q);font-weight:700;color:var(--orange)}
.fix{display:grid;grid-template-columns:22pt 1fr;gap:10pt;padding:10pt 0;border-bottom:.6pt solid var(--line);align-items:start}
.fix:last-child{border-bottom:0}
.fix .i{align-self:start;width:22pt;height:22pt;border-radius:5pt;background:var(--orange-soft);color:var(--orange);font-weight:800;display:flex;align-items:center;justify-content:center;font-size:9pt}
.fix h3{margin:0 0 3pt;font-size:10pt;color:var(--navy)}
.fix p{margin:0;font-size:8.3pt}
.fix .ev{margin-top:4pt;font-size:7.6pt;color:var(--meta)}
.small{font-size:7.2pt;color:var(--meta);margin:6pt 0 0}
table.comp{width:100%;border-collapse:collapse;font-size:8.2pt;background:var(--paper);border:.7pt solid var(--line);border-radius:6pt}
table.comp th{font-size:6.4pt;letter-spacing:.14em;text-transform:uppercase;color:var(--meta);text-align:left;padding:6pt 9pt;border-bottom:.6pt solid var(--line);font-weight:700}
table.comp td{padding:3.4pt 9pt;border-bottom:.6pt solid var(--line);font-variant-numeric:tabular-nums}
table.comp tr:last-child td{border-bottom:0}
table.comp tr.me td{background:#EEF2FC;color:var(--navy);font-weight:700}
table.comp .r{text-align:right}
table.comp .bar{height:6pt;background:var(--navy);border-radius:3pt}
table.comp tr:not(.me) .bar{background:#B9C2DA}
.where{display:grid;grid-template-columns:1fr 1fr;gap:9pt;margin-bottom:10pt}
.where .card{padding:10pt 12pt}
.where h3{margin:0 0 4pt;font-size:9.6pt;color:var(--navy)}
.where p{font-size:7.9pt;margin:0 0 3pt}
.where .nx{font-size:7.6pt;color:var(--meta)}
.where .nx a{color:var(--orange);font-weight:600}
.sig{display:inline-block;font-size:6.2pt;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:2pt 5pt;border-radius:3pt;margin-bottom:5pt}
.sig-strong{background:var(--orange-soft);color:var(--orange)}.sig-some{background:var(--amber-soft);color:var(--amber)}
.sig-low{background:var(--green-soft);color:var(--green)}.sig-unknown{background:#E9E6F1;color:#4A3F7A}
a{color:inherit;text-decoration:none}
.page>.ftr a{color:var(--navy);font-weight:600}
.callout a.cta{display:inline-block;margin-top:5pt;color:#fff;font-weight:700;text-decoration:underline;text-underline-offset:2pt}
.measure a{color:var(--orange);font-weight:600}
.cta-box a{color:#F3A57A;font-weight:700;text-decoration:underline;text-underline-offset:2pt}
.cover{padding:0}
.cover .top{background:var(--navy);color:#fff;padding:.62in .66in .55in;height:6.15in;position:relative}
.cover .top img{height:24pt}
.cover .top .loc{font-family:Mono,monospace;font-size:7.4pt;letter-spacing:.24em;color:#AFC0EE;margin-top:1.05in;text-transform:uppercase}
.cover .top .eyebrow{color:#F3A57A;margin-top:12pt}
.cover .top .eyebrow:before{background:#F3A57A}
.cover h1.c{color:#fff;font-size:32pt;line-height:1.06;max-width:6.4in;font-weight:700;letter-spacing:-.025em;margin:4pt 0 14pt}
.cover .who{font-size:11pt;font-weight:600}
.cover .who span{font-weight:400;color:#C6D0EF}
.cover .meta{font-size:8.2pt;color:#AFC0EE;margin-top:4pt}
.cover .stripe{position:absolute;left:0;right:0;bottom:0;height:5pt;background:linear-gradient(90deg,var(--orange) 0 34%,var(--blue) 34% 100%)}
.cover .bottom{padding:.42in .66in 0}
.cover .headline{font-size:11.2pt;line-height:1.52;max-width:6.9in;margin:6pt 0 18pt}
.cover .headline b{color:var(--navy)}
"""

OVERFLOW_JS = r"""<script>
(function(){
function run(){
  var out=[];
  document.querySelectorAll('.page').forEach(function(pg,i){
    var pr=pg.getBoundingClientRect();
    var src=pg.querySelector(':scope>.src'), ftr=pg.querySelector(':scope>.ftr');
    var limit=(src||ftr).getBoundingClientRect().top-3;
    var maxB=0,maxR=0,who='';
    pg.querySelectorAll('*').forEach(function(el){
      if(el.closest('.src,.ftr,.bignum,.top')) return;
      var r=el.getBoundingClientRect(); if(!r.width&&!r.height) return;
      if(r.bottom>maxB){maxB=r.bottom;who=(el.textContent||'').trim().slice(0,40);}
      if(!el.children.length && r.right>maxR) maxR=r.right;
    });
    if(maxB>limit) out.push('page '+(i+1)+': content runs '+Math.round(maxB-limit)+'px into the sources/footer area (near "'+who+'")');
    if(maxR>pr.right-40) out.push('page '+(i+1)+': content runs past the right margin');
    var top=pg.querySelector('.top');
    if(top){var tb=top.getBoundingClientRect().bottom;
      top.querySelectorAll('h1,.who,.meta').forEach(function(el){ if(el.getBoundingClientRect().bottom>tb-8) out.push('page 1: the cover title block is too tall (shorten the title)'); });}
  });
  document.body.setAttribute('data-overflow', out.length?out.join(' | '):'none');
}
if(document.fonts&&document.fonts.ready){document.fonts.ready.then(run);}else{window.addEventListener('load',run);}
})();
</script>"""


# ---------------------------------------------------------------- pieces
def kpi(k):
    cls = " o" if k.get("accent") else ""
    return (f'<div class="card kpi"><div class="lbl">{esc(k["label"])}</div>'
            f'<div class="v{cls}">{esc(k["value"])}</div><p>{md(k.get("note", ""))}</p></div>')


def kpis(items, cols=4, style=""):
    return f'<div class="grid{cols}" style="{style}">' + "".join(kpi(k) for k in items) + "</div>"


def callout(label, text, orange=False):
    return (f'<div class="callout{" orange" if orange else ""}"><div class="lbl">{esc(label)}</div>'
            f'<div class="q">{md(text)}</div></div>')


def card(h, text, tone="navy"):
    return f'<div class="card"><h4 class="{TONES.get(tone, "n")}">{esc(h)}</h4><p>{md(text)}</p></div>'


class Doc:
    def __init__(self, meta):
        self.meta = meta
        self.pages = []
        self.logo_dark = b64(ASSETS / "logo-dark.png", "image/png")
        self.logo_light = b64(ASSETS / "logo-light.png", "image/png")

    def page(self, num, section, eyebrow, title, dek, body, sources=""):
        self.pages.append(dict(num=num, section=section, eyebrow=eyebrow, title=title, dek=dek, body=body, sources=sources))


def render_page(doc, p, i, total):
    short = esc(doc.meta.get("short_name") or doc.meta["restaurant"]) + (" (fictional sample)" if doc.meta.get("sample") else "")
    src = f'<div class="src">{md(p["sources"])}</div>' if p["sources"] else ""
    dek = f'<p class="dek">{md(p["dek"])}</p>' if p["dek"] else ""
    return (f'<section class="page"><div class="hdr"><img src="{doc.logo_dark}" alt="Truvana Tech">'
            f'<div class="sec"><b>{p["num"]}</b> · {esc(p["section"])}</div></div>'
            f'<div class="bignum">{p["num"]}</div><div class="eyebrow">{esc(p["eyebrow"])}</div>'
            f'<h1>{md(p["title"])}</h1>{dek}{p["body"]}{src}'
            f'<div class="ftr"><span>{short} · Restaurant Health Report · free from {link("/", "truvanatech.com")}</span><span>p. {i} / {total}</span></div></section>')


# ---------------------------------------------------------------- sections
def sec_snapshot(d):
    rows = []
    for f in need(d, "facts", "snapshot"):
        cls, default = STATUS.get(f.get("status", "verify"), STATUS["verify"])
        label = f.get("tag") or default
        rows.append(f'<tr><td class="k">{esc(f["label"])}</td><td>{md(f["text"])}</td>'
                    f'<td class="t"><span class="tag {cls}">{esc(label)}</span></td></tr>')
    body = kpis(need(d, "kpis", "snapshot"), 4, "margin-bottom:14pt")
    body += f'<table class="facts">{"".join(rows)}</table>'
    body += f'<div style="margin-top:14pt">{callout("First question to answer", need(d, "first_question", "snapshot"))}</div>'
    return body, {}


def sec_demand(d):
    ratings = need(d, "ratings", "demand")
    mx = max(r["count"] for r in ratings) or 1
    rows = ['<div class="row head"><span>SITE · RATING</span><span>NUMBER OF RATINGS</span><span style="text-align:right">COUNT</span></div>']
    for r in ratings:
        o = " o" if r.get("channel") == "delivery" else ""
        w = max(2.5, 100 * r["count"] / mx)
        shown = r.get("count_text") or f'{r["count"]:,}'
        rows.append(f'<div class="row"><span><b style="color:var(--navy)">{esc(r["site"])}</b> · {esc(r["rating"])}★</span>'
                    f'<div class="track"><div class="fill{o}" style="width:{w:.1f}%"></div></div><span class="val{o}">{esc(shown)}</span></div>')
    body = f'<div class="card bars" style="margin-bottom:12pt">{"".join(rows)}</div>'
    chips = "".join(f'<span class="chip{" neg" if t.get("negative") else ""}">{esc(t["text"])}</span>' for t in d.get("themes", []))
    if chips:
        body += f'<div class="lbl" style="margin-bottom:6pt">What guests keep mentioning</div><div class="chips" style="margin-bottom:14pt">{chips}</div>'
    comp = d.get("competitors") or []
    comp_out = {}
    if comp:
        own = d.get("own") or next((r for r in ratings if r["site"].lower().startswith("google")), None)
        if not own:
            raise SystemExit("data.json: demand.competitors needs a Google entry in demand.ratings (or demand.own)")
        me_name = d.get("own_name") or "This restaurant"
        rows_c = [(me_name, float(own["rating"]), int(own["count"]), True)] + [(c["name"], float(c["rating"]), int(c["count"]), False) for c in comp]
        n = len(rows_c)
        by_rating = sorted(rows_c, key=lambda r: (-r[1], -r[2]))
        by_count = sorted(rows_c, key=lambda r: -r[2])
        r_rank = [r[3] for r in by_rating].index(True) + 1
        c_rank = [r[3] for r in by_count].index(True) + 1
        avg = sum(c[1] for c in rows_c if not c[3]) / len(comp)
        mx_c = max(r[2] for r in rows_c) or 1
        ordinal = lambda k: f"{k}{'th' if 10 <= k % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')}"
        trs = "".join(
            f'<tr class="{"me" if me else ""}"><td>{esc(name)}</td><td class="r">{rt:.1f}★</td><td class="r">{cnt:,}</td>'
            f'<td style="width:34%"><div class="bar" style="width:{max(3, 100 * cnt / mx_c):.0f}%"></div></td></tr>'
            for name, rt, cnt, me in by_rating)
        area = d.get("competitor_area", "Nearby restaurants of the same kind, Google Maps")
        summary = f"Rating: {ordinal(r_rank)} of {n} · Reviews: {ordinal(c_rank)} of {n} · Nearby average {avg:.1f}★"
        body += (f'<div class="lbl" style="margin-bottom:6pt">Compared with nearby restaurants · {esc(area)}</div>'
                 f'<table class="comp" style="margin-bottom:5pt"><tr><th>Restaurant</th><th class="r">Google</th><th class="r">Reviews</th><th>Review volume</th></tr>{trs}</table>'
                 f'<p class="small" style="margin:0 0 12pt;color:var(--navy);font-weight:600">{esc(summary)}</p>')
        comp_out = {"rating_rank": f"{ordinal(r_rank)} of {n}", "review_rank": f"{ordinal(c_rank)} of {n}",
                    "nearby_average_rating": f"{avg:.1f}", "rating_gap_vs_average": f"{float(own['rating']) - avg:+.1f}", "summary": summary}
    j = [] if comp else d.get("journey", [])
    if j:
        parts = []
        for n, s in enumerate(j[:4]):
            if n:
                parts.append('<div class="ar">›</div>')
            parts.append(f'<div class="st{" weak" if s.get("weak") else ""}"><div class="lbl">{esc(s["stage"])}</div>'
                         f'<b>{esc(s["title"])}</b><span>{esc(s.get("note", ""))}</span></div>')
        cols = " 12pt ".join(["1fr"] * len(j[:4]))
        body += (f'<div class="lbl" style="margin-bottom:6pt">The public guest journey today</div>'
                 f'<div class="flow" style="margin-bottom:14pt;grid-template-columns:{cols}">{"".join(parts)}</div>')
    body += f'<div class="grid2" style="margin-bottom:12pt">{card("Clearly working", need(d, "working", "demand"), "green")}{card("Not visible publicly", need(d, "not_visible", "demand"), "orange")}</div>'
    body += callout("Bottom line", need(d, "bottom_line", "demand"))
    total = sum(r["count"] for r in ratings)
    return body, {"ratings_total": total, "sites": len(ratings), "nearby": comp_out}


def sec_card_fees(d):
    rate = d.get("rate", {"percent": 2.6, "fixed": 0.15})
    p, fx = float(rate["percent"]), float(rate["fixed"])
    tickets = need(d, "tickets", "card_fees")
    calc = []
    for t in tickets:
        a = float(t["amount"])
        fee = a * p / 100 + fx
        calc.append((t["label"], a, fee, 100 * fee / a))
    mx = max(c[3] for c in calc)
    rate_label = f'{p:g}% + {round(fx * 100):g}¢'
    rows = []
    for n, (label, a, fee, eff) in enumerate(calc):
        o = " o" if eff >= 4 else ""
        rows.append(f'<div class="row"><span>{esc(label)}</span><div class="track"><div class="fill{o}" style="width:{100 * eff / mx:.1f}%"></div></div>'
                    f'<span class="val{o}">{pct(eff)}</span></div>')
    small = min(calc, key=lambda c: c[1])
    share = 100 * fx / small[2]
    if d.get("box_note"):
        box_note = d["box_note"]
    elif share >= 50:
        box_note = "Lowering the per-sale cents matters more here than shaving the percentage."
    else:
        box_note = "At these tickets the percentage is most of the fee, so the rate and monthly fees matter more than the cents."
    note = rate.get("note") or (f"{rate_label} is a common published flat rate for a tapped or inserted card. "
                                "It is used here as an example, not as this restaurant's actual rate.")
    left = (f'<div class="card bars"><div class="lbl" style="margin-bottom:4pt">Effective rate by ticket · at {esc(rate_label)} in person</div>'
            f'{"".join(rows)}<p class="small">{md(note)}</p></div>')
    right = (f'<div class="card kpi" style="display:flex;flex-direction:column;justify-content:center;text-align:center;background:var(--navy);border:0;color:#fff">'
             f'<div class="lbl" style="color:#AFC0EE">Fixed cents\' share of the fee on a {money(small[1])} sale</div>'
             f'<div class="v" style="color:#fff;font-size:40pt;margin:8pt 0">{share:.0f}%</div>'
             f'<p style="color:#C6D0EF">{round(fx * 100):g}¢ of the {small[2] * 100:.1f}¢ fee. {esc(box_note)}</p></div>')
    body = f'<div class="grid2" style="grid-template-columns:1.45fr 1fr;margin-bottom:12pt">{left}{right}</div>'
    sv = d.get("savings") or {}
    mode = sv.get("mode") or ("cents" if share >= 50 else "percent")
    savings_out = {}
    if mode == "cents":
        vols = sv.get("volumes") or d.get("volumes") or [{"label": "Slow month", "count": 1500}, {"label": "Steady month", "count": 3000}, {"label": "Busy month", "count": 4500}]
        saving = float(sv.get("per_sale", d.get("saving_per_sale", 0.10)))
        trs = ""
        for n, v in enumerate(vols):
            m, y = v["count"] * saving, v["count"] * saving * 12
            yv = f"<b class=up>{money(y)}</b>" if n == len(vols) - 1 else money(y)
            trs += f'<tr><td>{esc(v["label"])}</td><td>{v["count"]:,}</td><td>{money(m)}</td><td>{yv}</td></tr>'
            savings_out[v["label"]] = {"per_month": money(m), "per_year": money(y)}
        body += (f'<table class="data" style="margin-bottom:12pt"><tr><th>What {round(saving * 100):g}¢ per sale is worth</th>'
                 f'<th>Card sales / month</th><th>Per month</th><th>Per year</th></tr>{trs}</table>')
    elif mode == "percent":
        pts = float(sv.get("points", 0.25))
        vols = sv.get("monthly_sales") or [{"label": "Slow month", "amount": 40000}, {"label": "Steady month", "amount": 70000}, {"label": "Busy month", "amount": 100000}]
        trs = ""
        for n, v in enumerate(vols):
            m = v["amount"] * pts / 100
            y = m * 12
            yv = f"<b class=up>{money(y)}</b>" if n == len(vols) - 1 else money(y)
            trs += f'<tr><td>{esc(v["label"])}</td><td>{money(v["amount"])}</td><td>{money(m)}</td><td>{yv}</td></tr>'
            savings_out[v["label"]] = {"per_month": money(m), "per_year": money(y)}
        body += (f'<table class="data" style="margin-bottom:12pt"><tr><th>What {pts:g} percentage points is worth</th>'
                 f'<th>Card sales / month</th><th>Per month</th><th>Per year</th></tr>{trs}</table>')
    rules = card(d.get("rules_title", "Local rules to work within"), need(d, "rules_text", "card_fees"), "navy")
    unknown = card("What public data can't show", need(d, "unknowns_text", "card_fees"), "orange")
    body += f'<div class="grid2" style="margin-bottom:12pt">{rules}{unknown}</div>'
    body += (f'<div class="callout orange"><div class="lbl">{esc(CTA_FEES[0])}</div>'
             f'<div class="q">{esc(CTA_FEES[1])}<br>{link(CTA_FEES[2], "truvanatech.com/contact", "cta")}</div></div>')
    out = {"rate_label": rate_label, "smallest_ticket": money(small[1]), "smallest_effective": pct(small[3]),
           "fixed_share_smallest": f"{share:.0f}%", "by_ticket": {money(c[1]): pct(c[3]) for c in calc},
           "fixed_share_by_ticket": {money(c[1]): f"{100 * fx / c[2]:.0f}%" for c in calc},
           "savings_mode": mode, "savings": savings_out}
    return body, out


def sec_delivery(d):
    items = need(d, "items", "delivery")
    label = d.get("compare_label", "Delivery apps")
    rows, by_name, markups = [], {}, []
    for it in items:
        dr, mk = float(it["direct"]), float(it["marketplace"])
        diff = mk - dr
        by_name[it["name"]] = (dr, mk)
        markups.append((it["name"], diff, 100 * diff / dr if dr else 0.0))
        if abs(diff) < 0.005:
            rows.append(f'<tr class="zero"><td>{esc(it["name"])}</td><td>{money(dr)}</td><td>{money(mk)}</td><td>$0.00 / 0%</td></tr>')
        else:
            sign = "+" if diff > 0 else "−"
            rows.append(f'<tr><td>{esc(it["name"])}</td><td>{money(dr)}</td><td>{money(mk)}</td>'
                        f'<td class="up">{sign}{money(abs(diff))} / {abs(100 * diff / dr):.1f}%</td></tr>')
    body = (f'<table class="data" style="margin-bottom:11pt"><tr><th>Item</th><th>Direct (pickup)</th><th>{esc(label)}</th><th>Markup</th></tr>'
            f'{"".join(rows)}</table>')
    tiers = d.get("tiers", [15, 25, 30])
    def signed(x):
        return ("+" if x > 0.005 else "−" if x < -0.005 else "") + money(abs(x))
    out = {"items": {n: {"markup": signed(df), "markup_pct": f"{pc:+.1f}%"} for n, df, pc in markups}}
    nz = [m for m in markups if abs(m[1]) >= 0.005]
    if nz:
        out["markup_range"] = f"{signed(min(m[1] for m in nz))} to {signed(max(m[1] for m in nz))}"
        out["markup_pct_range"] = f"{min(m[2] for m in nz):+.1f}% to {max(m[2] for m in nz):+.1f}%"
    out["items_with_no_markup"] = [m[0] for m in markups if abs(m[1]) < 0.005]
    ex = d.get("example_order")
    sp = d.get("spotlight")
    blocks = []
    if ex:
        names = ex["items"]
        missing = [n for n in names if n not in by_name]
        if missing:
            raise SystemExit(f"data.json: example_order item(s) not in delivery.items: {missing}")
        ex_note = ex.get("note", "The tiers are the range of the apps' standard published plans; the actual plan is not public.")
        direct = sum(by_name[n][0] for n in names)
        app = sum(by_name[n][1] for n in names)
        trs = ""
        out["example"] = {"direct": money(direct), "app": money(app), "tiers": {}}
        for t in tiers:
            fee = round(app * t / 100, 2)
            keep = app - fee
            gap = keep - direct
            trs += f'<tr><td>{t:g}%</td><td>{money(fee)}</td><td>{money(keep)}</td><td class="up">{"−" if gap < 0 else "+"}{money(abs(gap))}</td></tr>'
            out["example"]["tiers"][f"{t:g}%"] = {"fee": money(fee), "keeps": money(keep), "vs_pickup": signed(gap)}
        blocks.append(
            f'<div class="card"><div class="lbl" style="margin-bottom:6pt">Example delivery order · {esc(" + ".join(names))}</div>'
            f'<table class="data" style="border:0;font-size:8pt"><tr><th>Commission tier</th><th>Fee to app</th><th>Store keeps</th><th>vs. pickup</th></tr>{trs}</table>'
            f'<p class="small">App subtotal {money(app)} vs. {money(direct)} at pickup. {esc(ex_note)}</p></div>')
    if sp:
        price = float(sp["price"])
        lo, hi = price * min(tiers) / 100, price * max(tiers) / 100
        out["spotlight"] = f"{money(lo)}–{money(hi)}"
        blocks.append(f'<div class="card kpi" style="display:flex;flex-direction:column;justify-content:center"><div class="lbl">{esc(sp.get("label", "Spotlight"))}</div>'
                      f'<div class="v o">{money(lo)}–{money(hi)}</div><p>{md(sp["note"])}</p></div>')
    if blocks:
        cols = "1.3fr 1fr" if len(blocks) == 2 else "1fr"
        body += f'<div class="grid2" style="grid-template-columns:{cols};margin-bottom:9pt">{"".join(blocks)}</div>'
    cards = d.get("cards", [])
    if cards:
        body += '<div class="grid2">' + "".join(card(c["title"], c["text"], c.get("tone", "navy")) for c in cards[:2]) + "</div>"
    return body, out


def sec_fixes(d):
    items = need(d, "items", "fixes")
    parts = "".join(
        f'<div class="fix"><div class="i">{n}</div><div><h3>{md(f["title"])}</h3><p>{md(f["text"])}</p>'
        f'<div class="ev">Fix: {md(f["fix"])}</div></div></div>' for n, f in enumerate(items, 1))
    body = f'<div class="card" style="padding:4pt 15pt;margin-bottom:14pt">{parts}</div>'
    if d.get("stats"):
        body += kpis(d["stats"][:3], 3)
    return body, {"fixes": len(items)}


def tool_link(step):
    t = step.get("tool")
    if not t:
        return ""
    if t not in FREE_TOOLS:
        raise SystemExit(f"data.json: plan step tool '{t}' is not one of {sorted(FREE_TOOLS)}")
    name, path = FREE_TOOLS[t]
    return f" <b>Free tool:</b> {link(path, name)}"


def sec_plan(d):
    where = need(d, "where_to_start", "plan")
    cards_html = ""
    for w in where[:4]:
        label, cls = SIGNALS.get(w.get("signal", "unknown"), SIGNALS["unknown"])
        cards_html += (f'<div class="card"><span class="sig {cls}">{label}</span><h3>{md(w["question"])}</h3>'
                       f'<p>{md(w["why"])}</p><p class="nx"><b>First step:</b> {md(w["next"])}{tool_link(w)}</p></div>')
    body = f'<div class="where">{cards_html}</div>'
    qs = "".join(f"<li>{md(q)}</li>" for q in need(d, "questions", "plan"))
    body += (f'<div class="grid2" style="grid-template-columns:1.15fr 1fr;margin-top:4pt">'
             f'<div class="card"><h4 class="n" style="margin-bottom:7pt">Questions to answer with your own numbers</h4><ol class="qs">{qs}</ol></div>'
             f'<div class="card cta-box" style="background:var(--navy);border:0;color:#fff"><h4 style="color:#F3A57A;margin-bottom:7pt">{esc(CTA_PLAN_TITLE)}</h4>'
             f'<p style="font-size:10pt;font-weight:500;line-height:1.45;color:#fff">{esc(CTA_PLAN_TEXT)}</p>'
             f'<p style="font-size:10pt;margin-top:9pt">{link("/contact", "Book a free meeting →")}</p>'
             f'<p style="font-size:7.6pt;color:#C6D0EF;margin-top:6pt">{link("/tools", "More free tools at truvanatech.com/tools")}</p></div></div>')
    basis = d.get("research_basis", [])
    if basis:
        spans = "".join(f"<span>{esc(b)}</span>" for b in basis)
        body += (f'<div class="card" style="margin-top:9pt;padding:7pt 12pt"><div class="lbl" style="margin-bottom:5pt">'
                 f'Research basis · accessed {esc(d.get("accessed", ""))}</div>'
                 f'<div class="grid2" style="gap:1pt 16pt;font-size:6.9pt;color:var(--meta)">{spans}</div></div>')
    return body, {}


SECTIONS = [
    ("snapshot", "Snapshot", "Snapshot", sec_snapshot),
    ("demand", "Demand signal", "Public demand signal", sec_demand),
    ("card_fees", "Card fees", "Card fee economics", sec_card_fees),
    ("delivery", "Delivery economics", "Matched public pricing", sec_delivery),
    ("fixes", "Quick fixes", "Found in public listings", sec_fixes),
    ("plan", "Where to start", "Where to start", sec_plan),
]


def build(data):
    meta = need(data, "meta", "root")
    for k in ("restaurant", "prepared"):
        need(meta, k, "meta")
    doc = Doc(meta)
    computed = {}
    num = 0
    for key, section, eyebrow, fn in SECTIONS:
        d = data.get(key)
        if not d:
            continue
        num += 1
        body, out = fn(d)
        computed[key] = out
        doc.page(f"{num:02d}", d.get("section", section), d.get("eyebrow", eyebrow), need(d, "title", key), d.get("dek", ""), body, d.get("sources", ""))

    total = len(doc.pages) + 1
    sample_tag = " · Sample, fictional restaurant" if meta.get("sample") else ""
    cover = need(data, "cover", "root")
    loc = esc(meta.get("area_label", ""))
    sub = f' <span>· {esc(meta["subtitle"])}</span>' if meta.get("subtitle") else ""
    metaline = " · ".join(x for x in [meta.get("address", ""), "Public-source analysis", f'Prepared {meta["prepared"]}'] if x)
    pages = [
        f'<section class="page cover"><div class="top"><img src="{doc.logo_light}" alt="Truvana Tech">'
        f'<div class="loc">{loc}</div><div class="eyebrow">Restaurant Health Report{sample_tag}</div>'
        f'<h1 class="c">{md(need(cover, "title", "cover"))}</h1><div class="who">{esc(meta["restaurant"])}{sub}</div>'
        f'<div class="meta">{esc(metaline)}</div><div class="stripe"></div></div>'
        f'<div class="bottom"><div class="eyebrow">Headline</div><p class="headline">{md(need(cover, "summary", "cover"))}</p>'
        f'{kpis(need(cover, "kpis", "cover"), 4)}</div>'
        f'<div class="ftr"><span>Made with the free Restaurant Health Report by Truvana Tech</span><span>{link("/", "truvanatech.com")}</span></div></section>'
    ]
    pages += [render_page(doc, p, i, total) for i, p in enumerate(doc.pages, 2)]
    title = f'{meta.get("short_name") or meta["restaurant"]} Restaurant Health Report'
    page_html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="expected-pages" content="{total}">'
                 f'<title>{esc(title)}</title><style>{css()}</style></head><body>{"".join(pages)}{OVERFLOW_JS}</body></html>')
    return page_html, total, computed


# ---------------------------------------------------------------- number check
SKIP_KEYS = {"sources", "research_basis", "accessed", "prepared", "address", "area_label"}
RX_D = re.compile(r"\$(\d[\d,]*(?:\.\d+)?)")
RX_P = re.compile(r"(\d+(?:\.\d+)?)\s?%")


def _walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def _rounds_to(a, txt):
    d = len(txt.split(".")[1]) if "." in txt else 0
    q = Decimal(1).scaleb(-d)
    return Decimal(repr(abs(a) + 1e-9)).quantize(q, ROUND_HALF_UP) == Decimal(txt).quantize(q)


def number_check(data, computed):
    allowed = []
    for _, v in _walk(data):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            allowed += [float(v), float(v) * 100]
    for _, v in _walk(computed):
        for m in re.findall(r"-?\d[\d,]*(?:\.\d+)?", str(v)):
            allowed.append(float(m.replace(",", "")))
    flagged = []
    for path, v in _walk(data):
        if not isinstance(v, str) or path.split(".")[-1] in SKIP_KEYS or ".sources" in path:
            continue
        for rx, unit in ((RX_D, "$"), (RX_P, "%")):
            for m in rx.finditer(v):
                txt = m.group(1).replace(",", "")
                if not any(_rounds_to(a, txt) for a in allowed):
                    flagged.append(f'{unit if unit == "$" else ""}{m.group(1)}{"%" if unit == "%" else ""}  ({path})')
    return flagged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    src = Path(a.data)
    data = json.loads(src.read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else src.with_name("report.html")
    page_html, total, computed = build(data)
    out.write_text(page_html, encoding="utf-8")
    print(f"Wrote {out} ({total} pages expected)")
    print("Computed numbers (use these exact values in cover KPIs and prose):")
    print(json.dumps(computed, indent=2, ensure_ascii=False))
    flagged = number_check(data, computed)
    if flagged:
        print("\nCHECK THESE NUMBERS: they appear in your text but not in data.json inputs or the computed output.")
        print("Each must come from evidence.md (e.g. a price range Google shows) or be replaced by a computed value:")
        for f in flagged:
            print("  - " + f)


if __name__ == "__main__":
    main()
