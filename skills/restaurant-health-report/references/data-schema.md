# data.json schema

Start from `examples/sample-falafel/data.json` and replace its content.

## Text conventions

- In any text field, `**bold**` renders as bold and `\n` as a line break.
- Everything else is escaped.

## Length budgets

The budgets below keep every page on one sheet. They are approximate; `render_pdf.py` tells you if a page overflowed.

## `meta`

| Field | Example | Notes |
|---|---|---|
| `restaurant` | "Olive & Za'atar" | Exact name, as the owner uses it |
| `short_name` | "Olive & Za'atar" | Used in footers |
| `subtitle` | "franchise location" | Optional, after the name on the cover. Use it for an operator or brand relationship; leave it out if it would only repeat `area_label` |
| `area_label` | "Georgetown · Washington, DC" | Small caps line on the cover |
| `address` | "123 Sample St NW, Washington, DC 20007" | |
| `prepared` | "November 23, 2026" | |
| `sample` | true | Only in the fictional sample. Marks the cover and footers as fictional. Delete it in real reports |

## `cover` (page 1)

- `title`: 2 lines, each ≤ 30 characters, joined with `\n`. Longer lines wrap at 32pt; three rendered lines is the maximum, and the layout check fails beyond that.
- `summary`: ≤ 650 characters. It says what's strong, what the opportunity is, and that the report uses public data only. Use `**bold**` on the 2–3 key facts.
- `kpis`: exactly 4 items of `{label, value, note, accent?}`.
  - `value` ≤ 7 characters, for example "4.7★", "$4.00" or "6.4%".
  - `note` ≤ 75 characters.
  - Set `accent: true` (orange) on the "problem" numbers.
  - **Take the values from the computed numbers** printed by `build_report.py`.

## `snapshot` (section 01)

- `title`: ≤ 65 characters.
- `dek`: ≤ 170 characters.
- `kpis`: 4 items, same rules as the cover.
- `facts`: 6–8 rows of `{label, text, status, tag?}`.
  - `label` ≤ 20 characters; `text` ≤ 150 characters.
  - `status` is one of `verified | public | law | verify | not_confirmed | not_public | client`.
  - `tag` overrides the badge text, for example "DC law".
  - Recommended rows: Operator, Format, Hours, Online ordering, Loyalty, POS, Card processing, Cash and card rules.
- `first_question`: ≤ 160 characters. The single question the owner should answer first, written as a quote.
- `sources`: ≤ 330 characters.

## `demand` (section 02)

- `title`, `dek`: same budgets as the snapshot.
- `ratings`: 3–6 items of `{site, rating, count, count_text?, channel?}`. With only 3, add a theme or two more, or a longer `working` / `not_visible`, so the page doesn't look empty.
  - `count` is a number; use the lower bound for "260+".
  - `count_text` is the displayed form, for example "260+".
  - `channel: "delivery"` colours the bar orange.
- `themes`: 5–9 items of `{text, negative?}`, each ≤ 40 characters.
- `competitors`: 3–5 items of `{name, rating, count}`, Google numbers for nearby restaurants of the same kind (see the playbook).
  - `own_name` names the restaurant's row.
  - `competitor_area` explains how they were chosen, ≤ 70 characters.
  - The script ranks the restaurant against them and prints `nearby` (rating rank, review rank, nearby average, gap). Use those values in titles and the cover.
  - When `competitors` is set, it replaces the journey row below.
- `journey`: 4 stages of `{stage, title, note, weak?}`. Only shown when there are no competitors.
  - `title` ≤ 16 characters; `note` ≤ 32 characters.
  - `weak: true` gives the stage a dashed border, for the weak link.
- `working`, `not_visible`: ≤ 230 characters each.
- `bottom_line`: ≤ 140 characters. The one sentence to remember from the report.
- `sources`: ≤ 330 characters.

## `card_fees` (section 03)

- `title`, `dek`: the dek can run to ≤ 260 characters here.
- `title`: match the ticket size. Use "On a $4 sandwich, the 15¢ costs more than the 2.6%." only for small tickets. For $14+ tickets use something like "At $20 a ticket, the rate is what matters."
- `rate`: `{percent, fixed, note}`.
  - The default is `2.6` and `0.15`, a common published in-person flat rate.
  - `note` must say the rate is an example, not the store's own rate.
- `tickets`: 4–5 items of `{label, amount}`, real menu items or orders, smallest first. The script computes the effective rate for each.
- `box_note`: optional; the sentence in the dark box. By default the script picks it from the fixed-cents share of the smallest ticket: cents matter when the share is ≥ 50%, otherwise the rate matters.
- `savings`: optional table showing what a small improvement is worth. Label its volumes as illustrative in `sources`.
  - Defaults to `cents` mode when the fixed share is ≥ 50%, otherwise `percent` mode.
  - `{"mode": "cents", "per_sale": 0.10, "volumes": [{"label", "count"}]}`: count defaults to 1,500 / 3,000 / 4,500 card sales a month.
  - `{"mode": "percent", "points": 0.25, "monthly_sales": [{"label", "amount"}]}`: amount defaults to $40k / $70k / $100k of card sales a month.
  - `{"mode": "none"}` hides the table.
- `rules_title`: for example "DC rules to work within".
- `rules_text`: ≤ 320 characters, from `references/state-rules.md`.
- `unknowns_text`: ≤ 280 characters.
- The orange "Free statement review" box at the bottom of the page comes from the template; there is no field for it.
- `sources`: ≤ 330 characters.

## `delivery` (section 04, optional)

- `compare_label`: for example "Uber Eats / DoorDash". If the apps' prices differ, use the one you compared and say so in the dek. If the listing is exclusive to one app ("Exclusive to Eats"), say so in a delivery card and in the snapshot facts.
- The build prints per-item markups and `markup_range` in dollars and percent. Use those for KPIs and prose, such as "$1 to $7 above direct".
- `items`: 5–10 items of `{name, direct, marketplace}`. These must be prices you saw for the same item on both.
- `example_order`: `{items: [names from items], note}`. Use a realistic 2-item order.
- `tiers`: commission tiers to illustrate; default `[15, 25, 30]`.
- `spotlight`: optional `{label, price, note}`. Use it for an item with no markup and a high price, such as a catering platter.
- `cards`: 2 items of `{title, text, tone}`.
  - `tone` is `orange` (a problem), `green` (a strength) or `navy` (neutral).
  - `text` ≤ 270 characters each.
- `sources`: ≤ 330 characters.

## `fixes` (section 05)

- `items`: 3–4 items of `{title, text, fix}`.
  - `title` ≤ 70 characters; `text` ≤ 260 characters.
  - `fix` ≤ 170 characters, written as an instruction (the word "Fix:" is added for you).
- `stats`: 3 KPI items. Typically: listings checked, inconsistencies found, cost to fix.
- `sources`: ≤ 330 characters.

## `plan` (section 06)

- `where_to_start`: 4 items of `{question, signal, why, next, tool?}`.
  - Use the four questions in SKILL.md step 3, in that order unless the evidence says otherwise.
  - `signal` is one of `strong`, `some`, `low` or `unknown`.
  - `why` is the evidence, ≤ 150 characters. `next` is the first step, ≤ 80 characters, written lower-case after "First step:".
  - `tool` optionally adds a free-tool link: `card-fee-calculator`, `delivery-app-commission-calculator`, `credit-card-surcharge-checker`, `processor-contract-exit-cost` or `cash-discount-sign-maker`.
- `questions`: 4–5 items, ≤ 95 characters each.
- `accessed`: the date the research was done.
- The "Want a deeper look?" box (a quick check-up, not a full analysis; book a free meeting) comes from the template.
- `research_basis`: 6–8 short source names, ≤ 60 characters each.
