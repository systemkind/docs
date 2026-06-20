#!/usr/bin/env python3
"""
craving — a 60-second "rewire" logger.

Every intense craving is a dopamine spike: your brain predicting what you should
do next, opening a ~60-second window of heightened plasticity. Ride out the
window, take a different action, and you wire a *competing* pathway instead of
feeding the old one. The bigger the urge, the more plastic that moment is.

This is a zero-dependency CLI to run that protocol and track it over time.

Usage:
  craving                  Run the full 60-second protocol and log it
  craving log              Same as above
  craving quick "trigger"  Log a rewire fast, no timer   (-i/--intensity 1-5)
  craving stats            Streak, totals, top triggers, last-14-days sparkline
  craving recent [N]       Show the last N entries (default 10)
  craving export [FILE]    Write all entries to CSV (default craving-export.csv)

Flags:
  --no-wait                Skip the 60s countdown in `log`
  -i, --intensity 1-5      Set intensity for `quick`

Data lives in ~/.craving/log.jsonl  (override the dir with $CRAVING_HOME).
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

WINDOW_SECONDS = 60
SPARK = "▁▂▃▄▅▆▇█"


def home() -> Path:
    base = os.environ.get("CRAVING_HOME")
    d = Path(base).expanduser() if base else Path.home() / ".craving"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_path() -> Path:
    return home() / "log.jsonl"


def load() -> list[dict]:
    p = log_path()
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def append(entry: dict) -> None:
    with log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def entry_date(e: dict) -> date:
    return datetime.fromisoformat(e["ts"]).date()


# ---------------------------------------------------------------------------
# stats helpers
# ---------------------------------------------------------------------------

def current_streak(days: set[date], today: date | None = None) -> int:
    today = today or date.today()
    if today in days:
        cur = today
    elif (today - timedelta(days=1)) in days:
        cur = today - timedelta(days=1)
    else:
        return 0
    n = 0
    while cur in days:
        n += 1
        cur -= timedelta(days=1)
    return n


def longest_streak(days: set[date]) -> int:
    if not days:
        return 0
    best = run = 1
    ordered = sorted(days)
    for prev, cur in zip(ordered, ordered[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
    return best


def sparkline(counts: list[int]) -> str:
    if not counts:
        return ""
    hi = max(counts)
    if hi == 0:
        return SPARK[0] * len(counts)
    return "".join(SPARK[min(len(SPARK) - 1, round(c / hi * (len(SPARK) - 1)))] for c in counts)


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def cmd_log(no_wait: bool = False) -> None:
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  YES — another chance to rewire your brain.   │")
    print("  └─────────────────────────────────────────────┘")
    print()
    print("  This craving is a prediction, not a command. It's a dopamine")
    print("  spike, and it opens a ~60s window where this pathway is plastic.")
    print("  Don't feed the old wiring. Sit with the wave and let it crest.\n")

    if not no_wait:
        print("  Breathe slow. The urge will rise, peak, and fall on its own.\n")
        try:
            cues = ["breathe in...", "hold...", "breathe out...", "let it pass..."]
            for r in range(WINDOW_SECONDS, 0, -1):
                cue = cues[(WINDOW_SECONDS - r) // 4 % len(cues)]
                bar = "█" * ((WINDOW_SECONDS - r) * 24 // WINDOW_SECONDS)
                bar = bar.ljust(24, "░")
                sys.stdout.write(f"\r   ⏳ {r:>2}s  [{bar}]  {cue:<14}")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\r" + " " * 60 + "\r")
        except KeyboardInterrupt:
            sys.stdout.write("\r" + " " * 60 + "\r")
            print("  (window cut short — logging anyway)\n")

    print("  Window's open. Lock in the new wiring. A few quick questions:\n")
    intensity = ask_intensity()
    trigger = input("  What set it off? (trigger)        > ").strip()
    instead = input("  What will you do instead?         > ").strip()
    note = input("  Anything else? (optional note)     > ").strip()

    entry = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "intensity": intensity,
        "trigger": trigger,
        "instead": instead,
        "note": note,
    }
    append(entry)
    _confirm(entry)


def cmd_quick(trigger: str, intensity: int | None) -> None:
    entry = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "intensity": intensity or 0,
        "trigger": trigger,
        "instead": "",
        "note": "",
    }
    append(entry)
    _confirm(entry)


def _confirm(entry: dict) -> None:
    rows = load()
    days = {entry_date(e) for e in rows}
    today_count = sum(1 for e in rows if entry_date(e) == date.today())
    streak = current_streak(days)
    print()
    print(f"  ✔ Rewire logged. #{today_count} today · {len(rows)} total · {streak}-day streak 🔥")
    print("  You just took a chance away from the old pathway. Good.\n")


def cmd_stats() -> None:
    rows = load()
    if not rows:
        print("\n  No rewires logged yet. Run `craving` next time an urge hits.\n")
        return
    days = {entry_date(e) for e in rows}
    today = date.today()
    today_count = sum(1 for e in rows if entry_date(e) == today)
    last14 = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
    counts = [sum(1 for e in rows if entry_date(e) == d) for d in last14]
    triggers = Counter(
        e["trigger"].strip().lower() for e in rows if e.get("trigger", "").strip()
    )
    intensities = [e["intensity"] for e in rows if e.get("intensity")]
    first = min(entry_date(e) for e in rows)

    print()
    print("  ── Rewiring progress ───────────────────────────────")
    print(f"  Total rewires        {len(rows)}")
    print(f"  Today                {today_count}")
    print(f"  Current streak       {current_streak(days)} days 🔥")
    print(f"  Longest streak       {longest_streak(days)} days")
    print(f"  Active days          {len(days)} (since {first.isoformat()})")
    if intensities:
        print(f"  Avg intensity        {sum(intensities)/len(intensities):.1f} / 5")
    print()
    print(f"  Last 14 days         {sparkline(counts)}  ({sum(counts)} rewires)")
    print(f"                       {last14[0].strftime('%b %d')} → {last14[-1].strftime('%b %d')}")
    if triggers:
        print()
        print("  Top triggers")
        for name, n in triggers.most_common(5):
            bar = "▓" * min(20, n)
            print(f"    {name[:22]:<22} {bar} {n}")
    print()


def cmd_recent(n: int) -> None:
    rows = load()[-n:]
    if not rows:
        print("\n  Nothing logged yet.\n")
        return
    print()
    for e in rows:
        ts = datetime.fromisoformat(e["ts"]).strftime("%b %d %H:%M")
        inten = f"[{e['intensity']}/5]" if e.get("intensity") else "[-/5]"
        trig = e.get("trigger", "") or "—"
        line = f"  {ts}  {inten}  {trig}"
        if e.get("instead"):
            line += f"  →  {e['instead']}"
        print(line)
    print()


def cmd_export(path: str) -> None:
    rows = load()
    fields = ["ts", "intensity", "trigger", "instead", "note"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for e in rows:
            w.writerow({k: e.get(k, "") for k in fields})
    print(f"\n  Exported {len(rows)} rewires → {path}\n")


def ask_intensity() -> int:
    while True:
        raw = input("  How intense was it? (1-5)         > ").strip()
        if not raw:
            return 0
        if raw.isdigit() and 1 <= int(raw) <= 5:
            return int(raw)
        print("    (enter a number 1-5, or leave blank)")


# ---------------------------------------------------------------------------
# arg parsing — tiny, no deps
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    args = argv[1:]
    cmd = args[0] if args and not args[0].startswith("-") else "log"
    rest = args[1:] if args and not args[0].startswith("-") else args

    if cmd in ("-h", "--help", "help"):
        print(__doc__)
        return 0

    if cmd == "log":
        cmd_log(no_wait="--no-wait" in rest)
    elif cmd == "quick":
        intensity = None
        skip = set()
        for flag in ("-i", "--intensity"):
            if flag in rest:
                idx = rest.index(flag)
                skip.add(idx)
                try:
                    intensity = int(rest[idx + 1])
                    skip.add(idx + 1)
                except (IndexError, ValueError):
                    pass
        pos = [a for i, a in enumerate(rest) if i not in skip and not a.startswith("-")]
        if not pos:
            print("  usage: craving quick \"trigger\" [-i 1-5]")
            return 1
        cmd_quick(" ".join(pos), intensity)
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "recent":
        n = int(rest[0]) if rest and rest[0].isdigit() else 10
        cmd_recent(n)
    elif cmd == "export":
        path = next((a for a in rest if not a.startswith("-")), "craving-export.csv")
        cmd_export(path)
    else:
        print(f"  unknown command: {cmd}\n")
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except KeyboardInterrupt:
        print("\n  (cancelled)\n")
        raise SystemExit(130)
