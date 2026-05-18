---
# Required
destination: HND          # IATA code; here, Tokyo Haneda
depart_window: [2026-09-12, 2026-09-19]   # search any day in this range
return_window: [2026-09-26, 2026-10-03]

# Optional (delete lines you don't want)
origin: SEA               # IATA code; if omitted, agent uses the primary airport from home.md
passengers: 2             # paid seats; defaults to home.md value
travelers: [you, partner] # names mapped to emails via home.md travelers table
target_price_usd: 1400    # per paid seat; email immediately when cheapest <= this
trip_length_days: 14      # for flexible round-trips, prefer durations close to this
max_stops: 1              # 0 = nonstop only, 1 = one stop ok, etc.
cabin: ECONOMY            # ECONOMY | PREMIUM_ECONOMY | BUSINESS | FIRST
airlines_preferred: [DL, AS, JL, NH]
airlines_excluded: [F9, NK, G4]
notify_after: 2026-06-01  # don't bother emailing before this date
---

# Tokyo trip notes

Free-form notes for the agent to read. Use these to encode preferences and constraints the frontmatter schema doesn't capture. The agent will read the prose, not just the YAML.

- Partner is jet-lag-sensitive. Prefer daytime arrivals into HND, and avoid red-eyes if a daytime option is within ~$200 per seat.
- We have JAL Mileage Bank accounts; slight preference for JL or oneworld so we can earn miles.
- Avoid Saturday departures if possible (work travel collides on Fridays).
- OK with one layover in NRT, ICN, or HKG; avoid LAX and SFO connections (we've had bad luck routing through them).
