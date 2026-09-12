#!/usr/bin/env python3
"""Generate a growing, GitHub-compatible contribution Snake animation."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from html import escape
from pathlib import Path


COLS = 53
ROWS = 7
WIDTH = 1000
HEIGHT = 230
X0 = 46
Y0 = 62
DX = 17.35
DY = 18
CELL = 12
DURATION = 24
ACTIVE_FRACTION = 0.86
GROWTH_STEPS = (3, 4, 6, 9, 13, 18, 26, 38, 55, 80, 115, 160, 220)


@dataclass(frozen=True)
class Day:
    date: str
    count: int


THEMES = {
    "light": {
        "background": "#f6f8fa",
        "border": "#d0d7de",
        "empty": "#ebedf0",
        "levels": ["#ddd6fe", "#c4b5fd", "#8b5cf6", "#6d28d9"],
        "body": "#6d28d9",
        "head": "#4c1d95",
        "eye": "#ffffff",
        "food": "#16a34a",
        "text": "#24292f",
        "muted": "#57606a",
    },
    "dark": {
        "background": "#0d1117",
        "border": "#30363d",
        "empty": "#161b22",
        "levels": ["#312e81", "#5b21b6", "#7c3aed", "#a78bfa"],
        "body": "#a78bfa",
        "head": "#c4b5fd",
        "eye": "#111827",
        "food": "#39d353",
        "text": "#f0f6fc",
        "muted": "#8b949e",
    },
}


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""


def fetch_days(username: str, token: str) -> list[list[Day]]:
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": username}}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "moussaab-contribution-snake",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"GitHub GraphQL request failed ({error.code}): {detail}") from error

    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL errors: {payload['errors']}")
    user = payload.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")

    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"][-COLS:]
    parsed = [
        [Day(item["date"], int(item["contributionCount"])) for item in week["contributionDays"]]
        for week in weeks
    ]
    return pad_weeks(parsed)


def demo_days(username: str) -> list[list[Day]]:
    """Create deterministic fixture data for local rendering and tests."""
    randomizer = random.Random(username)
    start = date.today() - timedelta(days=(COLS * ROWS - 1))
    weeks: list[list[Day]] = []
    for column in range(COLS):
        week = []
        for row in range(ROWS):
            count = randomizer.choices([0, 1, 2, 4, 8], weights=[46, 20, 16, 11, 7])[0]
            week.append(Day(str(start + timedelta(days=column * ROWS + row)), count))
        weeks.append(week)
    return weeks


def pad_weeks(weeks: list[list[Day]]) -> list[list[Day]]:
    blank = [Day("", 0) for _ in range(ROWS)]
    normalized = [week[:ROWS] + blank[len(week[:ROWS]):] for week in weeks]
    return [blank for _ in range(max(0, COLS - len(normalized)))] + normalized[-COLS:]


def route_points() -> list[tuple[float, float, int, int]]:
    points = []
    for row in range(ROWS):
        columns = range(COLS) if row % 2 == 0 else range(COLS - 1, -1, -1)
        for column in columns:
            points.append((X0 + column * DX, Y0 + row * DY, column, row))
    return points


def contribution_level(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


def build_svg(username: str, weeks: list[list[Day]], theme_name: str) -> str:
    theme = THEMES[theme_name]
    points = route_points()
    path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y, _, _ in points)
    total = sum(math.dist(points[i][:2], points[i + 1][:2]) for i in range(len(points) - 1))
    growth_lengths = [min(DX * steps, total) for steps in GROWTH_STEPS]
    growth_lengths.append(total)
    growth_times = [ACTIVE_FRACTION * index / (len(growth_lengths) - 1) for index in range(len(growth_lengths))]
    growth_values = ";".join(f"{length:.1f} {total:.1f}" for length in growth_lengths)
    growth_key_times = ";".join(f"{time:.4f}" for time in growth_times)
    initial = growth_lengths[0]
    grid = []
    pulses = []

    for index, (x, y, column, row) in enumerate(points):
        day = weeks[column][row]
        level = contribution_level(day.count)
        color = theme["empty"] if level == 0 else theme["levels"][level - 1]
        title = escape(f"{day.date}: {day.count} contribution{'s' if day.count != 1 else ''}")
        progress = index / (len(points) - 1) * ACTIVE_FRACTION
        reset = min(progress + 0.012, ACTIVE_FRACTION)
        animation = ""
        if day.count > 0:
            animation = (
                f'<animate attributeName="opacity" values="1;1;.12;.12;1" '
                f'keyTimes="0;{progress:.4f};{reset:.4f};.96;1" '
                f'dur="{DURATION}s" repeatCount="indefinite"/>'
            )
        grid.append(
            f'<rect x="{x-CELL/2:.1f}" y="{y-CELL/2:.1f}" width="{CELL}" height="{CELL}" rx="3" fill="{color}">'
            f'<title>{title}</title>{animation}</rect>'
        )
        if day.count > 0:
            pulse_end = min(progress + 0.025, 0.95)
            pulses.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="none" stroke="{theme["food"]}" stroke-width="2" opacity="0">'
                f'<animate attributeName="r" values="5;5;12;12;5" keyTimes="0;{progress:.4f};{pulse_end:.4f};.96;1" dur="{DURATION}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{progress:.4f};{pulse_end:.4f};.96;1" dur="{DURATION}s" repeatCount="indefinite"/>'
                '</circle>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Moussaab contribution snake</title>
  <desc id="desc">An animated snake consumes Moussaab's contribution grid, grows across the board, and pauses at full length.</desc>
  <rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="18" fill="{theme['background']}" stroke="{theme['border']}"/>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
    <text x="46" y="31" fill="{theme['text']}" font-size="15" font-weight="700">MOUSSAAB CONTRIBUTION SNAKE</text>
    <text x="954" y="31" fill="{theme['muted']}" font-size="12" text-anchor="end">EAT · GROW · COMPLETE</text>
  </g>
  <g>{''.join(grid)}</g>
  <g>{''.join(pulses)}</g>
  <path d="{path}" fill="none" stroke="{theme['body']}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{initial:.1f} {total:.1f}">
    <animate attributeName="stroke-dasharray" values="{growth_values}" keyTimes="{growth_key_times}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite"/>
  </path>
  <g>
    <animateMotion path="{path}" keyPoints="0;1;1" keyTimes="0;{ACTIVE_FRACTION};1" calcMode="linear" dur="{DURATION}s" rotate="auto" repeatCount="indefinite"/>
    <rect x="-10" y="-10" width="23" height="20" rx="8" fill="{theme['head']}"/>
    <circle cx="5" cy="-4" r="2.2" fill="{theme['eye']}"/><circle cx="5" cy="4" r="2.2" fill="{theme['eye']}"/>
  </g>
  <g text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{ACTIVE_FRACTION};.89;.96;1" dur="{DURATION}s" repeatCount="indefinite"/>
    <rect x="325" y="89" width="350" height="54" rx="12" fill="{theme['background']}" stroke="{theme['body']}" stroke-width="2"/>
    <text x="500" y="122" fill="{theme['text']}" font-size="18" font-weight="800">GRID COMPLETE · FULL LENGTH</text>
  </g>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="iammoussaab")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN", ""))
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--demo", action="store_true", help="Use deterministic local fixture data")
    args = parser.parse_args()

    if args.demo:
        weeks = demo_days(args.username)
    elif args.token:
        weeks = fetch_days(args.username, args.token)
    else:
        raise SystemExit("GITHUB_TOKEN is required unless --demo is used")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "github-snake.svg").write_text(build_svg(args.username, weeks, "light"), encoding="utf-8")
    (args.output_dir / "github-snake-dark.svg").write_text(build_svg(args.username, weeks, "dark"), encoding="utf-8")
    print(f"Generated light and dark contribution snakes in {args.output_dir}")


if __name__ == "__main__":
    main()
