<p align="center">
  <img src="assets/banner.png" alt="agentic-flight-watcher: a trip.md on the left, a price-history chart trending down to $285 on the right" width="100%">
</p>

# agentic-flight-watcher

Describe a trip in plain markdown. An agent prices it every few hours, keeps a per-trip price history, and emails you when it's time to book. A self-contained `dashboard.html` renders everything at a glance.

## Layout

```
agentic-flight-watcher/
├── AGENTS.md              agent instructions, read every cron tick
├── CLAUDE.md              symlink to AGENTS.md so Claude Code picks it up
├── home.md                your defaults (gitignored; copy from home.example.md)
├── home.example.md        template for home.md
├── dashboard.html         self-contained price-history view
├── <slug>.trip.md         one per active trip; you author these
├── <slug>.log.jsonl       observation log per trip (auto-appended)
├── archive/               completed and cancelled trips
└── lib/                   templates plus the dashboard generator
```

## Setup

### Agentic setup

After cloning, ask any agent that reads `AGENTS.md` (Claude Code, etc.):

> Set up this project per the Manual setup section in `README.md`. Install `fli`, walk me through filling in `home.md` from the template, schedule the cron, and help me add my first trip.

The agent handles every step. The one thing it can't do is run the `pipx install` line on your machine; it will pause and ask you to.

### Manual setup

1. `pipx install flights` (PyPI package is `flights`; the installed binary is `fli`).
2. `cp home.example.md home.md` and edit. The only required fields are your home airport and the `travelers:` name-to-email map; everything else is commented and optional.
3. `claude` from the repo root, then ask: *"schedule the flight watcher to run every 3 hours per AGENTS.md, durable."* Claude Code's scheduled tasks fire only while a Claude session is running and auto-expire after 7 days, so keep `claude` open in a persistent terminal (`tmux`, `screen`) and ask Claude to reschedule weekly. To delegate to system cron, wrap `claude -p "execute the procedure in AGENTS.md"` in a crontab line.
4. To verify, ask Claude *"run the procedure once now."* It will research any trips you've added, regenerate `dashboard.html`, and report back.

## Trips

```sh
cp lib/example.trip.md tokyo-vacation.trip.md
```

Edit the YAML frontmatter (`destination`, `depart_window`, `return_window`, `travelers` at minimum) and add free-form notes underneath. The agent reads the prose too: "no red-eyes," "prefer Delta nonstop with the lap infant on the return," "drive to ORD instead of connecting" are all valid. `lib/example.trip.md` documents every supported field.

To complete a trip, move its `.trip.md` and `.log.jsonl` into `archive/`. The cron also does this automatically once both travel windows are in the past.

## Dashboard

`lib/build-dashboard.py` regenerates `dashboard.html` from every trip and log file. The cron runs it each tick. The output is a single file with all data inlined and Chart.js plus marked.js pulled from CDN. Open it with `file://` in any browser; no server.

## How it works

Each cron tick the agent reads every `<slug>.trip.md`, merges defaults from `home.md`, prices the most plausible itinerary permutations with [`fli`](https://github.com/punitarani/fli), appends observations to the trip's log, decides whether to email a buy signal, and regenerates the dashboard. A trip's first run sends a research briefing email instead of a buy signal so you start with context. The full procedure lives in `AGENTS.md`.

## Requirements

- [Claude Code](https://claude.com/claude-code), Python 3.10+, [`fli`](https://github.com/punitarani/fli).
- The **`dev-browser`** skill for Claude Code. `fli` covers most queries, but multi-city itineraries, basic-vs-main fare splits, lap-infant confirmation, and transient Google Flights API regressions all need a real browser fallback. The agent uses `dev-browser` for those.
- **A Google Workspace CLI is preferred** (the original setup uses `gws` with `gwsp` / `gwsw` aliases for two accounts). It gives the agent two things in one place: notification email for buy signals, and calendar access so the agent can sanity-check trip dates against your actual calendar before recommending a booking. Substitute Gmail MCP or any other email tool Claude Code can reach if you don't run `gws`; calendar-aware logic will be limited or unavailable in that case. The send step in `AGENTS.md` is the only place to swap.

## Agent runtime

Instructions live in `AGENTS.md` per the [AGENTS.md convention](https://agents.md). `CLAUDE.md` is a 9-byte symlink to it so Claude Code finds it without extra config. For other runtimes, `ln -s AGENTS.md WHATEVER.md`.

## License & credits

MIT. Built on [`fli`](https://github.com/punitarani/fli), Chart.js, marked.js, and [Claude Code](https://claude.com/claude-code).
