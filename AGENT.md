# Contract for the daily run

You are the research half. Claude built the site; you only ever write **one file**:

```
days/YYYY-MM-DD.md
```

Do not touch `build.py`, `assets/`, `index.html`, or anything under `.github/`.
A bad research run must not be able to break the site.

## Steps

1. Read `config/follow.yml` — people first, then topics, in that order.
2. Find what is new since the previous day file in `days/`. Nothing older than that.
3. Write `days/<today>.md` in the format below.
4. Commit and push to `main`. The Action rebuilds and deploys; you do not run the build.

## Format

```markdown
---
date: 2026-09-04
generated_by: gemini
---

## Simon Willison
- **Title of the thing** (blog, 2026-09-03) [link](https://example.com/post)
  One or two sentences on what it is and why it matters.

## Topic: agent harnesses
- **Title** (github, 2026-09-04) [link](https://example.com/repo)
  One or two sentences.
```

## Rules

- **People before topics.** Topic headings must start with `Topic:` — that is what
  tags them on the page.
- **One `##` heading per person or topic.** Skip anyone with nothing new; no heading,
  no empty section. Do not pad.
- **Every item needs a source and a date** in the parenthetical, in that order:
  `(source, YYYY-MM-DD)`. The build renders it as `BLOG · 3 SEP`.
- **Every item needs a real link.** `[link](url)` — the title becomes the link.
- **The note is one or two sentences**, indented under the bullet. Optional but
  usually worth it. No marketing voice; say what it is and why it matters.
- **An empty day is fine.** Write the file with frontmatter and no sections. The page
  renders "Nothing new on the list today." Honest beats padded.
- **No run at all is also survivable** — the site keeps showing the newest day with a
  visible stale banner. Prefer an empty day file to silence.

The build tolerates a bullet that misses a link, a source or a note; it does not
tolerate you editing anything outside `days/`.
