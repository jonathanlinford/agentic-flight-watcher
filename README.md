# agentic-flight-watcher

A Claude Code agent that watches flight prices for trips you describe in plain markdown, builds up a per-trip price history, and emails you when it's time to book.

## What this is

Drop a `<slug>.trip.md` file into the project root describing a trip: dates, destination, passengers, preferences, free-form notes. A scheduled Claude Code job runs every 3 hours, prices the most plausible itineraries using [`fli`](https://github.com/punitarani/fli) (an open-source Google Flights CLI), appends each observation to a JSONL price-history log, and sends you an email when:

1. the current price falls below a threshold you set in the trip file, or
2. it bottoms out relative to the trailing 30-day window.

The first run for any new trip sends a research briefing email so you know what's currently on the market and what to expect from here.

The project also ships a self-contained `dashboard.html` (no server required) that visualizes every trip, its price history, and the trip's full configuration.

## Why "agentic"?

Almost every step (parsing trip notes, deciding which date and routing permutations are worth pricing, judging whether the current price is good enough to wake the user up) is a judgment call. This isn't a static script with hardcoded rules; it's a list of instructions a language model executes each tick, with `AGENTS.md` as the system prompt and your trip notes as the spec.

## Agent-agnostic

Instructions live in `AGENTS.md` per the [AGENTS.md](https://agents.md) convention. `CLAUDE.md` is a symlink to `AGENTS.md` so Claude Code reads it without extra config. If you use a different agent runtime that looks for its own filename, add an analogous symlink (`ln -s AGENTS.md WHATEVER.md`); the content is the same.

## Layout

```
agentic-flight-watcher/
├── AGENTS.md                canonical agent instructions (read every cron run)
├── CLAUDE.md                symlink to AGENTS.md so Claude Code finds it
├── home.md                  your defaults (gitignored; copy from home.example.md)
├── home.example.md          template for home.md
├── dashboard.html           regenerated each run; open with file:// in any browser
├── <slug>.trip.md           one per active trip; you author these
├── <slug>.log.jsonl         price history per trip (auto-appended)
├── archive/                 completed or cancelled trips move here
└── lib/
    ├── example.trip.md         copy this to <slug>.trip.md to add a new trip
    ├── build-dashboard.py      regenerates dashboard.html
    └── dashboard-template.html the dashboard's single-page template
```

## How a cron tick works

1. Read every `<slug>.trip.md`, merging in defaults from `home.md`.
2. Auto-archive trips whose travel windows are in the past.
3. Price the most plausible itinerary permutations via `fli` (origin and destination alternates, flexible dates within the window, stop and airline filters).
4. If this is the first run for a trip (no log file yet), send a research briefing email and seed the log.
5. Otherwise append the observation to `<slug>.log.jsonl` and decide whether to send a buy-signal email.
6. Regenerate `dashboard.html`.

The full procedure is in `AGENTS.md` (and `CLAUDE.md`, which is a symlink to it).

## Requirements

- [Claude Code](https://claude.com/claude-code) (the CLI). The scheduled job runs inside a Claude Code session.
- Python 3.10+ (for the dashboard generator).
- [`fli`](https://github.com/punitarani/fli) for flight pricing. The PyPI package is called `flights`; the installed binary is `fli`.
- A way for the agent to send email. This repo was originally built around Google Workspace CLIs (`gwsp` / `gwsw`), but any tool the agent can call works. Edit the email step in `AGENTS.md` to match your tooling.

## Setup

1. Clone:

   ```sh
   git clone https://github.com/jonathanlinford/agentic-flight-watcher.git
   cd agentic-flight-watcher
   ```

2. Install `fli`:

   ```sh
   pipx install flights
   ```

3. Configure your home defaults:

   ```sh
   cp home.example.md home.md
   ```

   Edit `home.md` with your home airport, default passengers, traveler-to-email map, cabin and airline preferences, and booking heuristics.

4. Open the project in Claude Code:

   ```sh
   cd agentic-flight-watcher
   claude
   ```

5. Inside Claude Code, ask: *"schedule the flight watcher to run every 3 hours."* Claude will register a recurring job that fires the procedure in `CLAUDE.md`. The schedule lives in the Claude Code session and auto-expires after 7 days; ask Claude to reschedule when needed.

## Adding a trip

```sh
cp lib/example.trip.md tokyo-vacation.trip.md
```

Edit the new file. The YAML frontmatter at the top is the source of truth; everything outside it is freeform notes the agent reads for nuance.

Minimum frontmatter:

```yaml
---
destination: ORD
depart_window: [2026-10-14, 2026-10-14]
return_window: [2026-10-18, 2026-10-18]
travelers: [you, partner]
---
```

`lib/example.trip.md` documents every supported field. Notes can encode preferences the schema doesn't capture, e.g. "no red-eyes," "prefer Delta nonstop," "lap infant on the return." The agent reads the prose, not just the YAML.

## Completing a trip

Move both `<slug>.trip.md` and `<slug>.log.jsonl` into `archive/`. The cron job also does this automatically once both travel windows are in the past.

## The dashboard

`python3 lib/build-dashboard.py` regenerates `dashboard.html` from every trip and log file. The cron job runs this automatically. Open the file directly in any browser; it's fully self-contained (data inlined, Chart.js and marked.js loaded from CDN). No server needed.

## License

MIT. See `LICENSE`.

## Acknowledgments

- [`fli`](https://github.com/punitarani/fli) does the heavy lifting on flight pricing by reverse-engineering Google Flights.
- Chart.js and marked.js power the dashboard.
- Built on top of [Claude Code](https://claude.com/claude-code).
