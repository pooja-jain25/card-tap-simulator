# Card Tap Simulator

An interactive explainer of what happens when you tap a Visa card, from the register to the issuer and back, plus a guide to how crypto-linked cards work.

- **Card tap simulator:** step through authorization for a bank debit card, a crypto-linked card, and a declined crypto card, then see clearing, settlement and fees.
- **How crypto cards work:** funding models, a crypto cost calculator, the crypto card stack, custody models and stablecoin settlement.
- **Latest news:** fintech and crypto headlines, refreshed daily by a GitHub Action.

Built by Pooja Jain 

## How it works

- `index.html` is the whole site: plain HTML, CSS and JavaScript, no build step.
- `news.json` holds the headlines the page shows.
- `scripts/fetch_news.py` reads public RSS feeds and rewrites `news.json`.
- `.github/workflows/news.yml` runs that script every day and commits the result.

## Run locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` directly works too, but browsers block reading `news.json` from a `file://` page, so headlines only show when served.
