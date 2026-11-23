# Research playbook

Plan about 30–60 minutes of agent time per report. Work through the sources below in order and log each one in `evidence.md` as you go.

## 1. The restaurant's own site

**Capture:**
- the legal or display name, exactly as written
- the address
- the phone number
- hours for each day
- the cuisine
- the number of locations
- the "Order" link and where it goes
- whether there's a menu with prices
- signs of a loyalty program, gift cards or catering

**Look out for:**
- **Franchise and multi-unit clues:** "franchise" pages, a location picker, or or a different owner mentioned by the person asking.
  - If sister locations use **different** POS or ordering systems (for example Toast at one store, Heartland at the others), the store is probably run separately. Note it.
- **Click through every action link:** Order, Catering, Gift cards and Reservations. A broken link, an old vendor's error page or a dead catering form is a top free fix.
- **Announced holiday or special hours** (banners, FAQ). Compare them with what Google and Yelp show for those days. A mismatch is a time-sensitive free fix.
- **Contradictions between pages:** for example, the FAQ says gift cards are in-store only, but the ordering page sells them.
- **The ordering platform.** Follow the Order button and note the domain or vendor. Common ones:
  - `toasttab.com` → Toast
  - `square.site` or Square Online → Square
  - `clover.com` → Clover
  - `order.online` → DoorDash Storefront
  - `chownow.com` → ChowNow
  - `menufy.com` → Menufy
  - `owner.com` → Owner
  - `popmenu.com` → Popmenu
  - `bentobox` → BentoBox
  - `per-diem.co` / `tryperdiem.com` → Per Diem, built for Square sellers
  - `olo.com` → Olo
  - `spoton.com` → SpotOn
  - `heartland` → Heartland
- **Finding a custom ordering page's vendor.** In a browser, run `performance.getEntriesByType('resource')` in the console to list the hosts the page loads. A CDN such as `cdn.per-diem.co` gives the vendor away.

## 2. The direct ordering page

**Capture:**
- prices for 8–12 core items: the hero item, mains, sides and a catering item
- the fulfillment options offered (pickup, delivery, curbside)
- whether there's a loyalty prompt or points
- order-ahead hours

**Notes:**
- If it's a brand-wide site, **select the target location** first, because prices can differ by location (they often do for franchise stores).
- Note the ordering hours and compare them with the store's hours.
- Choosing a location is fine. Never check out.

## 3. Delivery apps: Uber Eats, DoorDash, Grubhub

**Capture for each app:**
- the rating and rating count
- hours as shown (note which day you checked)
- prices for the **same items** you captured on the direct page
- any delivery or service fees the guest sees

**How to find the store page:**
- Search `"<restaurant>" "<street address>" site:ubereats.com` (or doordash.com, grubhub.com).
- DoorDash brand pages (`doordash.com/city/.../b/<brand>`) list every location with its store ID. Pick the one whose address matches.

**Quirks:**
- These sites usually block plain fetches, so use a browser tool.
- Grubhub hides the menu outside open hours; note "menu not open at time of check".
- **"Exclusive to Eats"** (or a DoorDash exclusive) on a listing is a big signal; note it. If the restaurant isn't on an app, say so. Don't use a same-name store in another city.
- If only some of the items match, compare only the ones that match. Never estimate a missing price.

## 4. Reviews: Google Maps, Yelp, Apple Maps (Tripadvisor optional)

**Capture:**
- rating and count
- the phone number and name **as each listing shows them** (mismatches are free fixes)
- price range ("$10–20 per person")
- review topic tags and the recurring praise and complaints

**Notes:**
- Add `hl=en` to Google Maps URLs, for example `https://www.google.com/maps/search/<name+address>?hl=en`, so the page reads in English whatever the browser language.
- Yelp may show "Verifying the device…". Wait a few seconds; if it doesn't clear, skip Yelp. Never solve a CAPTCHA.
- Apple Maps place pages (`maps.apple.com/place?...`) open in a normal browser and often hold stale phone numbers. Find one by searching `site:maps.apple.com "<name>" "<street>"`. If no result comes up or the page won't open, list Apple Maps under "Could not open" and move on.
- Don't quote more than a few words of any review. Summarize the themes instead.

## 5. Context (optional, only if quick)

- Local news on the store's history or size (Hoodline, Washington City Paper, Eater DC, the Washingtonian). Open the article itself, not just the snippet.
- The franchise brand's site, for the number of locations and franchise structure.

## 6. Rules and Truvana facts

- State card-surcharge and cash rules: `references/state-rules.md`. If the store is outside DC, MD or VA, look up that state's rule and cite its source.

## Inferences you may make, labelled as such

- **POS:** an inference from the ordering platform. Tag it `not_confirmed`, for example "Per Diem is built for Square, so Square is likely".
- **Average ticket:** from the menu prices and Google's "$ per person". Present it as a range.

## Things that are never public: don't guess them

- the processor or rate
- the contract end date
- the order mix by channel
- the commission plan
- loyalty membership numbers

These belong in "Questions to answer with your own numbers" on the last page.
