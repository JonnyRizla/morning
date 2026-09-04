# Daily briefing

One static page, rebuilt each morning with what is new from a fixed list of people
and topics. Yesterday is archived, not overwritten. Full brief in [SPEC.md](SPEC.md).

## Run it

```bash
python build.py            # -> _site/
python build.py --serve    # -> _site/, then http://localhost:8000
```

Python 3.8+, stdlib only. No install step, no lockfile.

## Shape

```
build.py                 the whole build, ~350 lines
config/follow.yml        people and topics — the research agent reads this
days/YYYY-MM-DD.md       one file per day; the agent writes only these
assets/style.css         the design
AGENT.md                 the contract for the daily research run
HANDOVER.md              how the scheduled run is wired up
_site/                   build output, gitignored
```

The site is a dumb renderer of files the agent drops in `days/`. Nothing else changes
day to day, so a bad research run cannot break the page.

## Deploy

A scheduled Claude Code cloud agent writes the day file at 06:00 Sydney (20:00 UTC)
and pushes. GitHub Actions builds on every push to `main` and publishes to Pages,
plus a 21:30 UTC fallback rebuild so the stale banner appears the same morning if the
run did not land. See [HANDOVER.md](HANDOVER.md). To turn Pages on:

1. Push to a **public** repo (Pages on a private repo needs a paid plan).
2. Settings → Pages → Source: **GitHub Actions**.
3. Push. First run takes about a minute.

Pages is public, and this page is a fairly complete portrait of what you read — so the
pages carry `noindex, nofollow` and nothing links to them. Obscure URL, no search
engines. That is the whole privacy story; treat it as public.

## Open decisions still standing

- **X coverage** — no usable feed. The news-about-them pass partly covers this by
  searching rather than subscribing, but direct X posts are still missed.
- **Cost of an unattended daily pass** over a growing list of names.
- **The unnamed learning channel** in the follow list, resolvable from YouTube history.
