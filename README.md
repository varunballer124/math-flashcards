# 💗 Visual Math Flashcards

A spaced-repetition flashcard app built from the *Visual Math Flashcards* decks
(486 cards across 17 topics — Essential Quant Skills → Functions & Sequences).

## Why it works (the learning science)
- **Active recall** — you see only the topic; you retrieve the rule from memory, *then* flip.
- **Spaced repetition** (SM-2-lite) — hard cards return quickly, easy cards drift weeks out; you only ever review what's *due*.
- **Interleaving** — due cards are shuffled across topics (beats studying one block at a time).
- **Visible progress** — mastery bar, due count, per-session totals.

Progress is saved in the browser (`localStorage`) on whatever device you use, plus an Export/Import backup.

## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Rebuild the cards (only if the source PDFs change)
```bash
python build_manifest.py   # regenerates cards.json + front-title crops
```

## Deploy online (Streamlit Community Cloud — free, always-on URL)
1. Push this folder to a **private** GitHub repo.
2. Go to https://share.streamlit.io → **New app** → pick the repo, branch, and `app.py`.
3. (Recommended, since the cards are paid TTP material) In the app's **Settings → Sharing**,
   turn on **viewer authentication** and whitelist only her Google email — keeps it private.
4. Share the resulting `https://<name>.streamlit.app` link. She can add it to her home screen.

> Source material © Target Test Prep. This is a personal study tool — keep the deployment access-restricted, don't list it publicly.
