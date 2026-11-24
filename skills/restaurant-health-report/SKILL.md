---
name: restaurant-health-report
description: Build a "Restaurant Health Report", a 7-page PDF check-up that helps any restaurant quickly understand where it stands, using public sources only. It covers ratings and reviews compared with nearby restaurants, card-fee costs at the restaurant's real ticket sizes, delivery-app vs. direct pricing, free listing fixes, and where to start (switch processors, add a kiosk, get reputation help, or cut delivery costs). Use when someone asks for a restaurant health report, a restaurant audit or check-up, or wants to understand a restaurant's online presence, fees or delivery economics. Made by Truvana Tech (truvanatech.com).
---

# Restaurant Health Report

Someone gives you a restaurant: its name plus a website, address or ordering link. You research it from public sources and return a clear 7-page PDF showing:

- what guests say about it
- what card fees and delivery apps really cost at its ticket sizes
- the listing mistakes it can fix this week for free

The person asking may be the owner, a manager, or someone helping them.

**Why this exists.** Truvana Tech reached out to more than 6,000 merchants and tested many payment solutions. Most owners it talked to watched only their card rate. Few were getting the most from their marketing or knew whether their reviews were good or bad next to nearby restaurants, and few knew where to start improving. This skill turns Truvana's analysis into a quick check-up that answers one question: **where should this restaurant start?** Should it switch card processors or pricing? Add a self-order kiosk to save labor? Get help with reviews and reputation? Or cut delivery-app costs?

**It's a check-up, not a full service.** Say what the public evidence shows and stop there. Every report ends with an offer from Truvana Tech's team to meet and go deeper. That offer, the footer and the free-tool links are part of the template; don't add, remove or reword them.

**In a chat AI?** If you are ChatGPT, Gemini, Claude.ai, DeepSeek, Kimi or any chat that can't run this skill's Python scripts, read the Rules and "Where to start" below, then follow `references/chat-mode.md` (https://raw.githubusercontent.com/YangzhenRuan/restaurant-health-report/main/skills/restaurant-health-report/references/chat-mode.md). It gives the steps, the arithmetic, the fallbacks and a ready-made HTML or Markdown report template.

Example output: `examples/sample-falafel/sample-report.pdf`. Its input is `examples/sample-falafel/data.json`. Read both before your first report. The sample restaurant is **fictional**; real reports never contain invented facts.

## Rules

1. **Only report what you saw yourself.** Every fact must come from a page you actually opened in this session, and you must record its URL in `evidence.md`.
   - A search-result snippet is not a source. Open the page, or leave the fact out.
   - If you couldn't open a page (it was blocked, needed a login or didn't load), say so. Don't guess what it says.
2. **Tag certainty honestly.** Every row in the snapshot facts table gets a status:
   - `verified` or `public`: you saw it.
   - `verify`: it's partly visible or may be out of date, so it needs confirming.
   - `not_confirmed`: it's an inference, for example "this POS is likely".
   - `not_public`: it can't be known from outside.
   - `client`: the person asking told you. Set `tag` to "From owner" or "From you".
3. **Don't invent prices or claims about any company.** That includes POS vendors, processors, delivery apps and Truvana Tech. Example rates such as "2.6% + 15¢" must be labelled as examples.
4. **Browse, never transact.** You may browse menus and pick a location on an ordering site to see its prices.
   - Never add to cart past the point of seeing a price.
   - Never check out, sign in, create an account or enter personal details.
   - Never solve a CAPTCHA or bypass a bot check. If a site blocks you, skip it and note that.
5. **Let the scripts do the arithmetic.** Put raw prices and counts in `data.json`, and let `scripts/build_report.py` compute rates, markups and commissions.
   - Copy its printed "computed numbers" into any prose that repeats them, such as cover KPIs and headlines. Never compute those by hand, not even "roughly a sixth".
   - The build prints **CHECK THESE NUMBERS** for any `$` or `%` in your text that isn't a data.json input or a computed value. For each one, either replace it with a computed value or confirm it's copied from evidence, for example Google's "$10–20 per person".
6. **Write in plain English for a restaurant owner.** Use short sentences and concrete numbers. Don't use hype or jargon, and never talk down to the owner ("you're overpaying"). Show the arithmetic and let the numbers speak. Write in English unless the person asks otherwise.

## When you can't do something: fallbacks

Never stop because a capability is missing. Use the fallback, say which one you used, and keep going.

| Missing | Do this instead |
|---|---|
| A browser tool (sites block plain fetches) | Use web search results. Mark facts from a result snippet "verify" and name the page. |
| Web search too | Ask the person for the restaurant's website, Google rating and review count, and a few menu prices. What they don't give is `not_public` or left out. |
| A page won't open | Skip it, list it under "Could not open" in `evidence.md`. |
| Python | Follow `references/chat-mode.md`: fill `templates/chat-report.html` (or `.md` if you can only write text). |
| Chrome, Edge or WeasyPrint | Deliver `report.html`. It's self-contained and prints to PDF from any browser. |
| The owner's statement | Use the 2.6% + 15¢ example, labelled as an example, and ask for last month's card sales, total fees and the rate they were quoted. |
| Delivery-app listings | Drop the `delivery` section. Pages renumber themselves. |

## What the owner tells you: build the report around it

The person may tell you how the restaurant runs today, often in a block headed "What I told you". Every item is a `client` fact ("From owner"); don't ask again for anything given, and don't contradict it without evidence. Use each one:

| They tell you | Use it to |
|---|---|
| Card processor | Name it in the snapshot; read its public pricing page if it has one, and say only what that page says. |
| How they're charged, and its numbers | Read it by model (table below). Only a flat rate is a quote the statement can be checked against. |
| Last month's card sales, total fees, number of card sales | `card_fees.actual` `{monthly_sales, monthly_fees, transactions?, processor?}`: "Your real rate" box (effective rate, a year, per sale, average ticket) replaces the example savings table. |
| POS | Snapshot fact; don't guess the POS from the outside. Note what it does and doesn't connect to only if its own site says so. |
| Online ordering, delivery apps | Which ordering pages and apps to price; check the direct link works and is easy to find. |
| Loyalty, gift cards, marketing texts, reservations, phone ordering, other software | Snapshot facts; they settle the reviews and repeat-guests question and the phone question instead of "Not enough data". |
| Contract end, early-termination fee, equipment lease | A line in the card-fee page about when switching costs least; link the contract exit cost calculator. |
| Their biggest worry | Answer it first. Its "where to start" card goes first and the bottom line speaks to it. |

**How they're charged**, by model. Plain words in the report; never guess the model from outside.

| Model | What it means | What to do with it |
|---|---|---|
| One flat rate (e.g. 2.6% + 15¢) | The same rate on every card | `card_fees.actual.quoted` `{percent, fixed}`: the script shows what the statement adds on top (monthly, PCI, statement fees, or cards billed above the rate). |
| Interchange plus (markup % + ¢) | Card networks' cost passed through, plus the processor's markup | The markup is the only part the processor sets. Don't compare it with the statement's effective rate (interchange varies by card); report the markup and the effective rate side by side. |
| Tiered (qualified / non-qualified) | Cards sorted into rate tiers | The least transparent model: what lands in the higher tiers drives the cost. Say the statement shows the split; don't estimate it. |
| Monthly plan (monthly $ + ¢ per sale) | Subscription, interchange at cost | Effective rate from the statement includes the monthly fee; at low volume the monthly fee weighs most. |
| Cash discount or dual pricing (card price higher by N%) | Posted prices are card prices; cash pays less | Card customers cover most of the fee. Check it's a real discount (card price posted up front, both prices clear), and the state's rules. |
| Surcharge on credit cards (N%) | A percent added at the register | Credit cards only, never debit or prepaid; at most 3% on Visa (4% Mastercard) or the cost if lower; banned in Connecticut, Massachusetts, Maine and Puerto Rico; signs at the door and register; on the receipt. Flag what doesn't fit. |
| Convenience or service fee | A fee added at checkout for paying by card | Under Visa's rules a true convenience fee is a flat amount, only for a different channel (online, phone), never in person; added at the register it's treated as a surcharge, with the surcharge rules. Say so plainly. |
| Not sure | | Common. Ask for last month's card sales and total fees; the effective rate settles it. |

The rules by state, with sources: https://truvanatech.com/cash-discount (Truvana Tech's guide; cite it) and `references/state-rules.md` for DC, Maryland and Virginia. The Visa and Mastercard settlement that would change surcharging and card acceptance had preliminary approval in June 2026, not final: never describe it as in effect.

What they tell you beats what you infer: a told fact is `client`, an inferred one is `not_confirmed`. What they don't tell you, research as usual.

## Workflow

### 1. Set up

Make a working folder named after the restaurant, for example `health-reports/<restaurant-slug>/`. Copy `examples/sample-falafel/data.json` into it as a starting point and delete its `"sample": true` line. Create `evidence.md` from `references/evidence-template.md`.

Ask the person only if you can't find the restaurant at all. Otherwise start. Record anything they told you as `client` facts, such as "it's a franchise location" or "I'm the owner".

### 2. Research

Follow `references/research-playbook.md`. It lists every source, what to capture from each, and where sites block automated fetching.

Use a real browser tool if you have one (Claude in Chrome, the Codex browser and so on). Delivery apps, Yelp and Google Maps often refuse plain HTTP fetches.

Record everything in `evidence.md` as you go: the URL, what you saw, and the date.

### 3. Find the main finding and where to start

Before writing, decide two things.

**The one-sentence bottom line.** Look at what the data actually says:

- **Small tickets ($3–$12 items).** The fixed per-sale card fee is most of the cost, so the card-fee page matters most. This is the sample report's story.
- **Mid or large tickets ($14+).** The percentage is most of the fee, so the rate, the monthly fees and the contract matter more than the cents. The script switches the card-fee box and the savings table automatically when the fixed share is under 50%.
- **Direct ordering exists and is cheaper, but hidden.** Guests order on the apps at higher prices, or the listing is exclusive to one app. Delivery economics and making direct ordering the default matter most.
- **No direct ordering at all.** Show what the apps keep per order.
- **Wrong phone, hours or name across listings.** The free fixes come first, since they're the easiest wins.
- **Weak or uneven ratings.** Report the recurring themes honestly. Suggest operational fixes only where the reviews point to them.
- **Franchise or multi-unit store.** Note which systems the brand seems to mandate and which look like the operator's choice. If one location runs a different POS or ordering system from its sister stores, note it: the location is probably run separately.

**Where to start.** Answer the four questions on the last page (`plan.where_to_start`), each with a signal that matches the evidence:

| Question | A strong signal looks like | Don't claim |
|---|---|---|
| Switch card processor or pricing? | small tickets (fixed share ≥ 50%), a surcharge or cash discount that's missing or confusing, no visible card-fee policy | the current rate, unless you have the statement |
| Add a self-order kiosk to save labor? | reviews about lines, waits or wrong orders; a busy counter-service menu; staff shortages mentioned in reviews | labor costs or order counts (not public) |
| Get help with reviews and reputation? | rating below the nearby average, far fewer reviews than nearby rivals, recurring complaints, listing mistakes | that reviews are fake, or that replying will raise the rating by a set amount |
| Cut delivery-app costs? | app prices close to direct prices, high-priced items with no markup, no direct ordering | the commission plan, unless it's public |

Use `strong`, `some`, `low` or `unknown` (not enough data). `unknown` is a good answer; it tells the owner what to measure.

Give each card an `area`: `payments`, `kiosk`, `kds`, `tableside`, `reputation`, `delivery` or `phone`. On a strong or some signal, the template adds a fixed "How Truvana Tech can help" line for that area: a statement review, a bilingual kiosk with a kitchen display, loyalty and texts, commission-free online ordering, or AI phone answering. Don't write your own version of it. The plan page's title should name the order to start in, for example "Where to start: payments first, then delivery."

Pick a cover headline that is short, true and specific. For example: "The demand is proven. The margin is in the small print."

**What reviews point to.** Read the reviews for operations problems guests keep naming: long lines, wrong or missing orders, slow table service, an unanswered phone. When one comes up in at least 2 separate reviews, add it to `demand.review_signals` with a count, a short quote and the fix to consider (kiosk, KDS, tableside ordering, AI phone answering, online ordering, loyalty, statement review). Up to 3, strongest first. The rules and the full map are in `references/review-signals.md`. It's the most persuasive part of the report because it comes from the restaurant's own guests, so never stretch it: one review is not a pattern, and food or service complaints get no product attached.

### 4. Write `data.json`, in two passes

The schema, with length budgets per field, is in `references/data-schema.md`. The sections are `cover`, `snapshot`, `demand`, `card_fees`, `delivery`, `fixes` and `plan`.

Leave out a section you have no data for. For example, drop `delivery` if the store isn't on any app; pages renumber automatically. Every `sources` line must name the pages behind that page's numbers.

1. **Numbers first.** Fill in the raw inputs: ratings, prices, tickets and delivery items. Use short placeholder titles and KPIs, then run `build_report.py` once and read the computed numbers.
2. **Then the prose.** Write titles, KPIs, the summary and fixes using those exact computed values.

### 5. Build and render

```bash
python3 <skill-dir>/scripts/build_report.py health-reports/<slug>/data.json
python3 <skill-dir>/scripts/render_pdf.py health-reports/<slug>/report.html --preview
```

`render_pdf.py` uses Chrome, Edge or Chromium in headless mode, falling back to WeasyPrint. It measures every page and exits with code 2 (**OVERFLOW**, naming the page) when text runs into the sources line or footer, past the margin, or out of the cover title block. Pages have a fixed size, so overflow is clipped rather than adding pages; that is why the measurement matters. Shorten the text on the named page and run both commands again until it prints **OK**.

Open the PDF, or `preview.png`, and look at every page before you deliver.

### 6. Self-check

Run every item in `references/qa-checklist.md`. The ones that matter most:

- Every number in the prose matches the computed numbers and the evidence.
- No fact rests only on a search snippet.
- The statuses are honest.
- No page overflows.
- Nearby competitors are the same kind of restaurant, really nearby, and their numbers come from their own listing pages.
- Every "where to start" signal cites evidence in the report.
- The restaurant's name and address are spelled exactly as on its own site. If the site's location name differs from the postal city (for example a neighborhood name), use the site's name in `area_label` and the postal address in `address`.

### 7. Deliver

Give the person:

- the PDF path
- a 5-line summary: the headline, the 3 strongest findings and the first question to answer
- a short **"double-check"** list covering anything tagged `verify`, anything you couldn't open, and anything that changes by day (hours, prices)

Keep `evidence.md` next to the PDF.

## Files

| Path | What it is |
|------|-----------|
| `scripts/build_report.py` | data.json → self-contained report.html (fonts and logos embedded), prints the computed numbers |
| `scripts/render_pdf.py` | report.html → PDF, with a layout check and a `--preview` PNG |
| `references/research-playbook.md` | Sources to check, what to capture, blocking quirks |
| `references/data-schema.md` | Every field, with length budgets that keep pages from overflowing |
| `references/state-rules.md` | DC / MD / VA cash and card-surcharge rules |
| `references/qa-checklist.md` | Pre-delivery checklist |
| `references/evidence-template.md` | Template for the evidence log |
| `examples/sample-falafel/` | A complete fictional example (data, PDF) |
| `references/chat-mode.md` | How to make the report in a chat AI without the scripts |
| `references/review-signals.md` | Review complaints → the fix to consider: evidence rules and the map |
| `templates/chat-report.html`, `templates/chat-report.md` | Report templates for chat mode, with the fixed Truvana Tech lines |
