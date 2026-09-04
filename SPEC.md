---
type: Reference
description: Build spec for the daily briefing site, a static GitHub Pages page rebuilt each morning with news on Jonny's follow list and topics, with previous days archived.
tags: [reference, spec, software, publishing, follow-list]
generated: { by: claude, at: 2026-09-04 }
sources:
  - id: 2026-09-03
    resource: system/processed/2026-09-03.md
---

# Daily briefing site: spec

Copy this file into the new project folder as `SPEC.md` before building. Background and the reasoning behind it: [[daily-briefing-page]] and [[people-to-follow]].

## Core idea

One static page, hosted free on GitHub Pages, rebuilt every morning with what is new from a fixed list of people and topics. A readable version of Google Alerts: same inputs, one page instead of a stack of emails, scannable in a minute. Yesterday's page is archived, not overwritten.

## Split of work

- **Claude builds the site**: the static shell, the layout, the archive index, the GitHub Pages deploy. No research, no content.
- **Antigravity or Gemini does the daily run**: research the list, write today's file, roll yesterday's into the archive, commit and push.

So the site must be a dumb renderer of files an agent drops in. The contract between the two halves is the file format below, and it is the part worth getting right.

## Repo shape

```
/index.html            today's briefing (or a redirect to the newest day)
/archive/index.html    list of past days, newest first
/days/YYYY-MM-DD.md    one file per day, the agent writes these
/config/follow.yml     people and topics, hand-edited
/assets/               css, minimal
```

Markdown in, static HTML out. The agent only ever writes `days/YYYY-MM-DD.md`; the build turns the folder into the page and the archive. Nothing else in the repo changes day to day, so a bad research run cannot break the site.

## Day file format

```markdown
---
date: 2026-09-04
generated_by: gemini
---

## Simon Willison
- **Title of the thing** (blog, 2026-09-03) [link]
  One or two sentences on what it is and why it matters.

## Topic: agent harnesses
- ...
```

Rules: group by person first, then topics. Skip anyone with nothing new, do not pad. Each item needs a source link and a date. No item older than the last run.

## Design constraints

- Loads instantly on a phone, readable in portrait, no JavaScript needed to read it.
- Dated heading at the top so it is obvious the page is fresh.
- Archive is a plain dated list, no search needed at this size.
- Empty days render as an empty day, honestly.

## Open decisions

1. **Public or private.** GitHub Pages is public by default and this page is a fairly complete portrait of what Jonny is interested in. Decide before the first push. A private repo with Pages needs a paid plan; the alternative is a boring URL and no links to it.
2. **X coverage.** No usable feed. Either accept that X output is missed, or let the research agent search rather than subscribe.
3. **Cost of an unattended daily research pass** over a growing list of names.
4. **Frequency of failure**: what the page shows if the morning run does not happen. Suggested: yesterday's page with a visible stale date.

## The follow list

Fifteen entries, from [[people-to-follow]]. Where-they-publish is a starting point, not verified.

| Person | Why | Where to look |
|---|---|---|
| Andrej Karpathy | Founding OpenAI, ex-Tesla AI, the canonical teaching source | YouTube (primary), X |
| Simon Willison | Co-created Django, builds Datasette and the `llm` CLI; best running commentary on LLM tooling | Blog (high frequency), X |
| Boris Cherny | Created Claude Code, the tool the vault runs on | X, release notes |
| DHH (David Heinemeier Hansson) | Created Rails, 37signals CTO, cloud repatriation and anti-complexity | Blog, X |
| Mitchell Hashimoto | Ghostty; before that Terraform, Vault, Consul, Vagrant | Blog (build logs), X |
| Matt Pocock | Agent skills (the `grill-me` skill traces to his repo); TypeScript education | X, YouTube, blog |
| Addy Osmani | Google Chrome engineering leader, writes on AI-assisted engineering | X, own site, newsletter |
| Andrew Ng | Stanford, DeepLearning.AI, Google Brain founder | *The Batch* newsletter (weekly), X, LinkedIn |
| Armin Ronacher | Created Flask, Jinja2, Click; now Rust tooling; language design and anti-complexity | Blog, X |
| Daniel Chalef | Zep and Graphiti, temporal knowledge graphs. The Zep engineering blog is the real target | Zep blog, GitHub |
| Tyler Cowen | Marginal Revolution, several posts a day, plus *Conversations with Tyler* | Blog (highest volume here), podcast |
| Robin Hanson | Prediction market theory, Overcoming Bias | Blog |
| Scott Alexander | Astral Codex Ten, long-form essays on rationalism, AI, social science | Blog |
| Shayne Coplan | Founder of Polymarket, and the legal fight around prediction markets | X, interviews |
| *Unnamed learning channel* | Open slot: a YouTube channel about learning, watched 2026-09-02, name not recalled. Resolvable from YouTube history | YouTube |

## Topics

Second section of each day, drawn from the graph rather than from people:

- AI agents, harnesses and tooling (Claude Code, MCP, agent skills)
- Knowledge graphs, GraphRAG, temporal graphs
- Personal knowledge bases and local-first tools
- Prediction markets (Polymarket)
- Anything else worth pulling from `okf/index.md` when the list needs widening

Keep the topic list in `config/follow.yml` next to the people so one file drives the whole run.
