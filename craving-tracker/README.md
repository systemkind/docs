# Rewire — a craving tracker you'll actually keep using

Built from the idea that **every intense craving is a dopamine spike, not pleasure** —
your brain predicting what should happen next, opening a **~60-second window of
heightened plasticity**. Feed the urge and you strengthen the old wiring. Take a
different action inside that window and you build a *competing* pathway. The
bigger the urge, the more plastic the moment.

This folder gives you **three ways to run that protocol** plus **automation** so you
keep coming back to it. Pick one, or use them together — they share the same idea
and an interchangeable JSON export.

---

## Option 1 — The web app (best for phones, zero install)

**File:** [`index.html`](./index.html)

A single self-contained file. No server, no accounts, no network — your data lives
in the browser (`localStorage`).

- Tap **"I'm having a craving"** → a 60-second ring counts down with a breathing
  pacer and the reframe ("Yes — another chance to rewire").
- After the window, log intensity (1–5), the trigger, and what you'll do instead.
- See your **streak, today's count, total**, a 14-day bar chart, and recent rewires.
- **Export / Import** JSON to back up or move devices.
- **Remind me** uses browser notifications while the app is open.

**Use it regularly:** open `index.html`, then on iOS Safari tap **Share → Add to
Home Screen** (Android Chrome: **⋮ → Add to Home screen**). It launches full-screen
like an app and works offline.

> Want it on your phone without plugging in a cable? Email yourself the file, or
> drop it in iCloud/Drive and open it once — it caches into the browser.

---

## Option 2 — The CLI (best for desktop, trivially automatable)

**File:** [`craving.py`](./craving.py) — pure Python 3, no dependencies.

```bash
# Optional: make it a global command
chmod +x craving-tracker/craving.py
ln -s "$PWD/craving-tracker/craving.py" /usr/local/bin/craving   # or add an alias

craving            # full 60-second protocol, then logs it
craving quick "scrolling reflex" -i 4   # fast log, no timer
craving stats      # streak, totals, top triggers, 14-day sparkline
craving recent 15  # last 15 entries
craving export     # -> craving-export.csv
```

Data is stored at `~/.craving/log.jsonl` (override with `CRAVING_HOME`). It's plain
JSON-lines, so it's easy to back up, sync, or chart yourself.

Sample `craving stats`:

```
  ── Rewiring progress ───────────────────────────────
  Total rewires        128
  Current streak       9 days 🔥
  Longest streak       14 days
  Last 14 days         ▂▅▃▇▄▂▅█▆▃▄▆▂▅  (61 rewires)
  Top triggers
    boredom               ▓▓▓▓▓▓▓▓ 8
    after dinner          ▓▓▓▓▓ 5
```

---

## Option 3 — Automation (so you don't have to remember)

**File:** [`craving-reminder.sh`](./craving-reminder.sh) — fires a desktop/phone
notification, optionally with your weekly digest. Auto-detects macOS, Linux, or
Termux notifiers.

```bash
chmod +x craving-tracker/craving-reminder.sh
craving-tracker/craving-reminder.sh          # just a nudge
craving-tracker/craving-reminder.sh digest   # nudge + your stats
```

### Schedule it

**Linux / macOS — cron** (`crontab -e`):

```cron
# Three gentle nudges a day
0 11,16,21 * * *  /full/path/to/craving-tracker/craving-reminder.sh
# Sunday-evening weekly digest
0 19 * * 0        /full/path/to/craving-tracker/craving-reminder.sh digest
```

**macOS — launchd** (survives reboots, fires even if cron is asleep). Save as
`~/Library/LaunchAgents/com.you.rewire.plist` and `launchctl load` it:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.you.rewire</string>
  <key>ProgramArguments</key>
  <array>
    <string>/full/path/to/craving-tracker/craving-reminder.sh</string>
    <string>digest</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict></plist>
```

> **Tip:** the strongest automation is environmental — pair these reminders with
> the cue itself. A phone-addiction example: set the reminder to fire when you'd
> normally doom-scroll, and keep the web app on your home screen where the app you
> quit used to be.

---

## Which should I use?

| You want…                                  | Use            |
|--------------------------------------------|----------------|
| Something on your phone, in the moment      | **Web app**    |
| To log fast from a terminal / script it     | **CLI**        |
| To be reminded without thinking about it    | **Automation** |
| All of the above                            | Web app on your phone + cron digest on your laptop |

All three are interchangeable on data: the web app exports JSON, and the same
shape can be fed back in or charted alongside the CLI's `~/.craving/log.jsonl`.

---

## The protocol, in four steps

1. **Notice** the craving the instant it spikes.
2. **Reframe:** "This is a prediction, not a need — and a chance to rewire."
3. **Ride the 60 seconds.** Breathe. Let the wave rise, peak, and fall.
4. **Act differently** and **log it.** The new action is the new wiring.

## The neuroscience (why 60 seconds)

A dopamine spike itself is fast (~100–500 ms) and decays in seconds, but its
downstream effects open a broader **eligibility window** for synaptic plasticity
and cue-reward tagging — seconds to tens of seconds, up to ~1 minute in some
paradigms. What you do *immediately after a cue* is far more likely to shape that
pathway than what you do later. The strengthening is circuit-specific, not global.

- Yagishita, S. et al. (2014). *A critical time window for dopamine actions on the structural plasticity of dendritic spines.* Science, 345(6204), 1616–1620.
- Reynolds, J. N. J., Hyland, B. I., & Wickens, J. R. (2001). *A cellular mechanism of reward-related learning.* Nature, 413, 67–70.
- Gerstner, W., Lehmann, M., Liakoni, V., Corneil, D., & Brea, J. (2018). *Eligibility traces and plasticity.* Neuron, 97(2), 273–289.
- Lisman, J., Grace, A. A., & Duzel, E. (2011). *A neoHebbian framework for episodic memory; role of dopamine-dependent late LTP.* Neuron, 72(5), 703–717.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

*Not medical advice. A self-tracking tool, not a treatment.*
