#!/usr/bin/env python3
"""Generate /Users/jonny/flights/dashboard.html from all *.trip.md and *.log.jsonl files."""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "lib" / "dashboard-template.html"
OUTPUT = ROOT / "dashboard.html"
PLACEHOLDER = "__DASHBOARD_DATA__"


def parse_yaml_lite(text: str) -> dict:
    """Minimal YAML for our trip frontmatter (flat keys, simple lists, scalars)."""
    out = {}
    for raw in text.splitlines():
        line = re.sub(r"(?<!\\)#.*$", "", raw).rstrip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip("'\"") for v in val[1:-1].split(",")]
            items = [coerce_scalar(v) for v in items if v]
            out[key] = items
        else:
            out[key] = coerce_scalar(val.strip("'\""))
    return out


def coerce_scalar(v):
    if isinstance(v, (int, float)):
        return v
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v


def split_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def load_trip(path: pathlib.Path, archived: bool, log_path: pathlib.Path):
    text = path.read_text()
    fm_text, body = split_frontmatter(text)
    fm = parse_yaml_lite(fm_text) if fm_text else {}
    slug = path.name[: -len(".trip.md")]
    observations = []
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                observations.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return {
        "slug": slug,
        "archived": archived,
        "frontmatter": fm,
        "body": body.strip(),
        "observations": observations,
    }


def collect(directory: pathlib.Path, archived: bool):
    trips = []
    if not directory.exists():
        return trips
    for trip_path in sorted(directory.glob("*.trip.md")):
        slug = trip_path.name[: -len(".trip.md")]
        log_path = directory / f"{slug}.log.jsonl"
        trips.append(load_trip(trip_path, archived, log_path))
    return trips


def main():
    if not TEMPLATE.exists():
        print(f"Missing template: {TEMPLATE}", file=sys.stderr)
        sys.exit(1)

    active = collect(ROOT, archived=False)
    archive = collect(ROOT / "archive", archived=True)

    data = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds"),
        "trips": active + archive,
    }

    template = TEMPLATE.read_text()
    payload = json.dumps(data, ensure_ascii=False)
    # Escape </script just in case a trip body contains it.
    payload = payload.replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, payload)
    OUTPUT.write_text(html)
    print(f"Wrote {OUTPUT} ({len(active)} active, {len(archive)} archived)")


if __name__ == "__main__":
    main()
