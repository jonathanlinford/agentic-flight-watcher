# agentic-flight-watcher

Agent instructions for a personal flight watcher. Each `*.trip.md` in this directory describes one trip; a cron job runs every 3 hours, researches prices for each trip, and emails when it's time to buy.

This file follows the [AGENTS.md](https://agents.md) convention; it is the single source of truth. `CLAUDE.md` is a symlink to this file so Claude Code picks it up automatically. Add similar symlinks for any other agent runtime that expects its own filename.

## Layout

```
agentic-flight-watcher/
├── AGENTS.md              ← this file; canonical agent instructions
├── CLAUDE.md              ← symlink to AGENTS.md (so Claude Code finds it)
├── home.md                ← home airport, traveler-to-email map, default prefs
├── dashboard.html         ← regenerated each cron run; open in a browser
├── <slug>.trip.md         ← one per active trip
├── <slug>.log.jsonl       ← appended each research run (price history)
├── archive/               ← completed/cancelled trips moved here
└── lib/
    ├── example.trip.md       ← template, copy to <slug>.trip.md in the root
    ├── build-dashboard.py    ← regenerates dashboard.html
    └── dashboard-template.html
```

## Trip file format

See `example.trip.md`. YAML frontmatter is the source of truth; the body is freeform notes the agent should read for nuance (preferred airlines, layover tolerance, "don't book the red-eye", etc.).

Required frontmatter fields: `destination`, `depart_window`, `return_window` (omit if one-way).

Optional: `origin` (defaults to home airport from `home.md`), `passengers` (defaults to home), `travelers` (list of names; controls who gets emailed; defaults to `[jonny]`), `target_price_usd`, `max_stops`, `cabin`, `airlines_preferred`, `airlines_excluded`, `trip_length_days` (for flexible-date round-trips), `notify_after` (don't email before this date).

## Home defaults

`home.md` holds the home airport, default passenger list, and default flight preferences (cabin, max stops, preferred/excluded airlines, etc.). For every trip, merge `home.md` first, then overlay the trip's frontmatter. Trip-level values always win. If a trip omits `origin`, use the primary airport from `home.md`.

## Tools available

- `fli`: flight search CLI (https://github.com/punitarani/fli). Install with `pipx install flights`. JSON output via `--format json`.
- An email-sending tool. This repo was originally built around `gwsp` / `gwsw` Google Workspace CLIs; substitute whatever the current Claude Code session can reach (Gmail MCP server, another CLI, etc.). The agent looks up recipient addresses from the `travelers:` mapping in `home.md`.
- `dev-browser` skill: fallback for cases `fli` can't handle (multi-city pricing nuance, specific airline checkout, etc.).

## Research procedure (runs every 3 hours)

When the cron fires, run this exactly:

1. **Enumerate trips.** For every `*.trip.md` (not in `archive/`), parse the frontmatter.

2. **Archive past trips.** If today (2026-05-18 reference, use real date) is after the latest date in either window, `git mv`-style move both `<slug>.trip.md` and `<slug>.log.jsonl` into `archive/`. Skip to next trip.

3. **Plan permutations.** Be smart, don't brute-force:
   - If `depart_window` is a single date, query it. If a range, use `fli dates <orig> <dest> --from … --to …` to find the cheapest day in the window (apply day-of-week filters from notes).
   - For round-trips with `trip_length_days`, pass `--round --duration N`.
   - Honor `max_stops`, `cabin`, `airlines_preferred`/`excluded`.
   - Set `--currency USD --language en --country US` for stable prices.
   - Cap to top ~5 itineraries by price; don't log dozens.

4. **Detect first run.** If `<slug>.log.jsonl` does not exist (or is empty), this is the trip's first research pass. After completing the research and logging (step 5), send an **initial briefing email** instead of the normal buy-signal email. The briefing covers:
   - The candidate routings you priced (e.g. each origin/destination pair from the trip notes).
   - Best current price per option, with airline/stops/duration.
   - Historic/typical pricing context for the route (use `fli`'s "low/typical/high" hint when available, or your own knowledge of the route's seasonality). Be explicit when you're estimating.
   - What we should expect from here: how prices typically move toward the trip date, any seasonality, when the booking-window sweet spot is per `home.md` heuristics, and what the buy-signal thresholds for this trip will trigger on.
   - Subject: `Flight watch started: <origin>→<destination>`.
   - Send to the email addresses mapped from the trip's `travelers` list via the `travelers:` table in `home.md`. The primary account holder is always included.
   - Mark the first log entry with `"initial_briefing":true` so we don't re-send it.

5. **Log observations.** Append one JSON line per cheapest-itinerary-found to `<slug>.log.jsonl`:
   ```json
   {"ts":"<ISO8601>","depart":"YYYY-MM-DD","return":"YYYY-MM-DD","price_usd":423,"airline":"DL","stops":0,"duration_min":355,"raw":{…}}
   ```
   One line per distinct (depart, return) pair you priced. This file is the historic data. Read it next run.

6. **Decide buy signal.** Skip this step if step 4 just sent the initial briefing. Otherwise, email if EITHER:
   - **Threshold hit:** `target_price_usd` is set in frontmatter and current best ≤ target.
   - **Price-drop heuristic:** ≥10 prior observations exist in the log, AND current best is in the bottom 15% of the trailing 30-day window AND ≤ 90% of the 7-day median. (Avoids flapping at the noise floor.)

   Suppress if:
   - `notify_after` is set and today is before it.
   - You already emailed a buy signal in the last 18 hours for this trip. Check the log for a `"notified":true` marker on a recent entry, and set it when you email.

7. **Email.** Send from the configured sender account. Recipients: the email addresses mapped from the trip's `travelers` list via the `travelers:` table in `home.md`; the primary account holder is always included. Subject: `Flight buy signal: <origin>→<destination> $<price>`. Body: itinerary details, link to book (Google Flights URL if available from fli output), price history summary (current vs 30-day low/median/high, number of observations), the reasoning ("threshold met" or "price-drop heuristic"). Mark the corresponding log entry with `"notified":true`.

8. **Be conservative with API calls.** `fli` hits Google Flights' internal API; space requests, don't loop tightly. If `fli` errors or returns nonsense, log the error and move on (don't fall into a retry loop). Use `dev-browser` only when `fli` genuinely can't answer (rare; document why in the log entry).

9. **Regenerate the dashboard.** After all trips have been processed (whether or not anything was emailed), run `python3 lib/build-dashboard.py` (from the project root) to rebuild `dashboard.html`. This is a fast, deterministic step that bundles every trip and observation log into a self-contained HTML page.

## Dashboard

`dashboard.html` is a self-contained HTML file (inline data, Chart.js and marked.js via CDN). Open it directly with `file://` in any browser. It shows every active and archived trip as a card with sparkline, a click-through detail view with full price history chart, observation table, configuration, and rendered notes. The build script is idempotent; running it without any new data simply refreshes the timestamp.

## Adding / completing a trip

- **Add:** copy `lib/example.trip.md` to `<slug>.trip.md` in the project root, edit frontmatter and notes.
- **Complete / cancel:** move both files to `archive/`. The hourly job also does this automatically once both windows are in the past.

## Cron

A durable job runs every 3 hours (registered in this Claude session). It auto-expires after 7 days, so re-run `/init` or ask Claude to "reschedule the flight cron" before then. To check or remove it, ask Claude to list/delete cron jobs.
