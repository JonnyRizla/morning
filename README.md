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
_site/                   build output, gitignored
```

The site is a dumb renderer of files the agent drops in `days/`. Nothing else changes
day to day, so a bad research run cannot break the page.

## Deploy

GitHub Actions builds on every push to `main` and publishes to Pages, plus a 07:30 UTC
rebuild so the stale banner's day count stays honest. To turn it on:

1. Push to a **public** repo (Pages on a private repo needs a paid plan).
2. Settings → Pages → Source: **GitHub Actions**.
3. Push. First run takes about a minute.

Pages is public, and this page is a fairly complete portrait of what you read — so the
pages carry `noindex, nofollow` and nothing links to them. Obscure URL, no search
engines. That is the whole privacy story; treat it as public.

## First real run

`days/` currently holds two seed files marked `generated_by: sample-data` so the layout
can be checked. Delete both before the agent's first run.

## Open decisions still standing

- **X coverage** — no usable feed. Either accept X output is missed, or let the research
  agent search rather than subscribe.
- **Cost of an unattended daily pass** over a growing list of names.
- **The unnamed learning channel** in the follow list, resolvable from YouTube history.
