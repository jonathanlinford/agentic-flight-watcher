# Home defaults

Copy this file to `home.md` and edit it. Defaults declared here apply to every `*.trip.md` unless a trip overrides the field. Trip frontmatter always wins.

## Home location

- Acceptable origin airports, in preference order: AAA, BBB
- (Optional) Tie-breaker notes between airports, e.g. "BBB is closer, prefer when price and connections are equal-or-better."

## Travelers

Map each traveler name to an email address. Trip files reference travelers by name in their `travelers:` frontmatter; this is how the agent knows where to send buy-signal emails.

```yaml
travelers:
  you: you@example.com
  partner: partner@example.com
```

## Flight preferences

- Cabin: ECONOMY by default.
- Max stops: 1 (nonstop preferred).
- Layover floor: 60 minutes domestic, 90 minutes international.
- Avoid red-eyes when a daytime option is within a tolerable upcharge.
- Preferred connection hubs: ... ; avoid: ...

## Airline preferences

- Loyalty programs: ...
- Preferred carriers: ...
- Excluded carriers: F9, NK, G4 (ultra low-cost; opt out by default).

## Booking heuristics

- Domestic round-trips: target 4 to 8 weeks out.
- International round-trips: target 10 to 16 weeks out; willing to book up to 6 months out for known holiday windows.
- Currency: USD. Country: US. Language: en.
