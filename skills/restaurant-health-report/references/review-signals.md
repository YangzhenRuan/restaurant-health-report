# Review signals: what reviews complain about, and the fix to consider

Reviews often name an operations problem in the guest's own words: a long line, a wrong order, a phone nobody answers. When the same problem keeps coming up, the report names it, shows how often and quotes it, and points to the kind of fix that addresses it. This is the most useful part of the report for an owner, because it comes from their own guests. It only stays useful while it stays honest.

## The rules

1. **At least 2 separate reviews** must name the problem, from the last 18 months where the dates show. One review is enough only when the owner told you the same thing (`owner_agrees: true`). One angry review is not a pattern.
2. **Quote one review**, short (under 90 characters), word for word, with the site it's on. Count only the reviews you actually read.
3. **At most 3 signals**, strongest first (most reviews, most recent). Leave the rest out: the report is a check-up, not a catalog.
4. **Fit the restaurant.** Tableside ordering is for table service, a kiosk for counter service. Don't suggest what the restaurant already has (the owner may have told you: kiosk, online ordering, loyalty).
5. **"A fix to consider", never a promise.** Don't say it will cut the wait by some amount or raise the rating.
6. **No signal is a fine answer.** If reviews don't repeat a fixable problem, leave `review_signals` out; the page shows "Clearly working" and "Not visible publicly" instead.

## The map

| What guests keep saying | Fix key | Fix to consider (Truvana Tech) | Page |
|---|---|---|---|
| Long line, slow to order at the counter, "took forever to order" | `kiosk` | Self-order kiosk: guests order and pay on a bilingual kiosk, and the order goes straight to the kitchen. | truvanatech.com/self-order-kiosk |
| Wrong order, missing items, order mixed up, food came out of order, "they forgot my…" | `kds` | Kitchen display (KDS): every order on one kitchen screen, in English or Spanish, in the order it came in. | truvanatech.com/kitchen-display-system |
| Waited long to order or for the check at the table, hard to get a server's attention, slow table turns | `tableside` | Tableside ordering: handhelds and QR codes, so guests order and pay at the table. | truvanatech.com/tableside-ordering |
| Nobody answers the phone, always busy, phone order wrong | `phone` | AI phone answering: phone orders answered in English and Spanish, so no call is missed. | truvanatech.com/ai-phone-ordering |
| Delivery app problems (cold, late, wrong) together with app prices higher than in store, or guests asking for a way to order direct | `online` | Online ordering: orders from the restaurant's own page and app, with no commission. | truvanatech.com/online-ordering |
| "Used to come all the time", regulars mention no reward, guests asking about gift cards | `loyalty` | Loyalty and gift cards: points, gift cards and texts that bring guests back. | truvanatech.com/restaurant-loyalty-program |
| Card machine down, "cash only" surprises, complaints about a card fee or surcharge | `payments` | Statement review: a free statement review, every fee explained and a written quote. | truvanatech.com/contact |

Problems with no fix here (food quality, rude staff, cleanliness, parking, prices) are still worth reporting honestly in "what guests complain about". Just don't attach a product to them.

## In data.json

`demand.review_signals`: up to 3 of

```json
{"theme": "Long line at lunch", "count": 4, "quote": "Line out the door at noon, 20 minutes just to order", "source": "Google", "fix": "kiosk"}
```

Add `"owner_agrees": true` when the owner told you the same thing. The script checks the count and the fix key and draws the table. With signals, the "What guests keep mentioning" chips keep only the praise, since the complaints are in the table. The fix lines are template text: you pick the key, never the words.

Then use the same evidence on the "where to start" page: a kiosk, KDS or tableside signal makes the kiosk / labor question at least "Some signal". Give that card `area: "kiosk"`, `"kds"` or `"tableside"` to match.
