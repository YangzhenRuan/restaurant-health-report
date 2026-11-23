# Pre-delivery checklist

Run every item. Fix anything that fails, rebuild and rerender.

## Facts
- [ ] Every fact in the PDF appears in `evidence.md` with a URL you opened this session.
- [ ] No fact rests on a search snippet alone.
- [ ] The restaurant name, address and phone are spelled exactly as on its own site.
- [ ] Each fact row's status matches the evidence: inferences are `not_confirmed`, and partner info is `client`.
- [ ] Prices compared are the same item, same size, same location. Anything that didn't match is left out.
- [ ] Day-dependent facts say when they were checked, for example "on the Monday checked".
- [ ] Each page's `sources` line names the pages behind its numbers.

## Numbers
- [ ] Nearby competitors are the same kind of restaurant, really nearby, and each was opened on Google Maps.
- [ ] Every "where to start" signal matches evidence shown in the report. `unknown` is used where the evidence is missing.
- [ ] Cover KPIs and headlines use the exact values `build_report.py` printed. Don't round differently, and don't paraphrase a computed value into a different one ("about a sixth").
- [ ] Example rates and transaction volumes are labelled as examples or illustrative.
- [ ] No price, rate or savings figure for any company (vendor, app, processor, Truvana Tech) is invented.
- [ ] The Truvana Tech footer, CTA box and free-tool links are untouched (they come from the template).

## Tone
- [ ] Plain English, short sentences, nothing that reads as hype.
- [ ] Every page has a clear takeaway in its title.
- [ ] The free fixes are genuinely free, and actionable by the owner this week.
- [ ] Nothing talks down to the owner ("you're overpaying"). Show the arithmetic.
- [ ] Reviews are summarized, not quoted at length.

## Layout
- [ ] `render_pdf.py` printed **OK**: no OVERFLOW, and the page count matches.
- [ ] `build_report.py` printed no CHECK THESE NUMBERS line, or every number listed is in `evidence.md`.
- [ ] Prose matches the ticket size: no "the cents matter most" claim when the fixed share is under 50%.
- [ ] You looked at every page (the PDF or `preview.png`): nothing is cut off, no overlaps, and no empty cards.
- [ ] The section numbers run in order. If you dropped a section, the rest renumber automatically.

## Handoff
- [ ] Gave the person the PDF path, a 5-line summary and a "double-check" list.
