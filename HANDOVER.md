# The daily run

The briefing is produced by a **scheduled Claude Code cloud agent**, not by hand.

- **Fires**: 06:00 Sydney / 20:00 UTC, daily.
- **Writes**: `days/YYYY-MM-DD.md` (Sydney date), commits, pushes to `main`.
- **Then**: GitHub Actions builds and deploys. A fallback rebuild runs 21:30 UTC so
  the stale banner appears the same morning if the run did not land.

The contract it works to is [AGENT.md](AGENT.md). That is the single source of truth
— the routine's prompt deliberately does not restate it, so there is only one place
to edit when the rules change.

## The routine's prompt

```
Produce today's daily briefing for this repo.

Read AGENT.md first and follow it exactly — it is the contract and it covers the
file format, the two research passes, the summary standard and the permalink rule.
Then read config/follow.yml for the people, topics, feeds and search hints.

Write days/<today's Sydney date>.md, commit, and push to main. You run at 20:00 UTC,
which is already tomorrow in Sydney, so take the date from Sydney time — using the
UTC date will overwrite yesterday's page.

Do not modify anything outside days/. If a feed is dead or a rule in follow.yml looks
wrong, note it in the run summary rather than editing the file yourself.

Finish with a short report: item count, who had nothing, which sections came from the
news-about-them pass rather than their own output, and anything in follow.yml that
needs fixing.
```

## Changing it

- **Rules, format, summary standard** → edit `AGENT.md`. No need to touch the routine.
- **Who and what is followed** → edit `config/follow.yml`.
- **Time, or the prompt above** → `/schedule` in Claude Code, then pick this routine.
- **Pausing** → disable the routine; the site keeps serving the newest day with a
  visible stale banner, which is the designed failure mode.

## If a morning is missed

Nothing breaks. The page shows the most recent day with "No run has landed for today
— this is N days old". To fill a gap by hand, run the prompt above in a normal
session; there is nothing special about the scheduled context.
