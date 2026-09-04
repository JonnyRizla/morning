# Contract for the daily run

You are the research half, running unattended as a scheduled agent at **06:00
Sydney (20:00 UTC)**. You only ever write **one file**:

```
days/YYYY-MM-DD.md
```

Do not touch `build.py`, `assets/`, `index.html`, or anything under `.github/`.
A bad research run must not be able to break the site.

**Use the Sydney date, not UTC.** You run at 20:00 UTC, which is already tomorrow
in Sydney — the file for a run starting 20:00 UTC on the 5th is `2026-09-06.md`.
Get this wrong and you overwrite yesterday's page.

## Steps

1. Read `config/follow.yml` — people first, then topics, in that order. It carries a
   `feed:` for most entries so you are not rediscovering sources every morning, and a
   `search:` hint for finding news *about* people who publish rarely.
2. For each person, run the two passes described below. Cover the window since the
   previous day file in `days/`; on a normal daily run that is about 24 hours, but
   because you run at Sydney dawn you are mostly catching the *previous* US working
   day. Do not exclude something for being dated "yesterday" in US time — that is
   the expected case, not a stale item.
3. Write `days/<today Sydney>.md` in the format below.
4. Commit and push to `main`. The Action rebuilds and deploys; you do not run the build.

## Two passes per person

**Pass one — their own output.** Their feed, blog, releases, channel. This leads the
section. A person's own work always outranks coverage of it.

**Pass two — news about them.** Only run this when pass one found nothing, or found
fewer than two items. Search for what has been written about them, what they have
been quoted in, what they shipped that someone else covered, interviews, podcast
appearances, funding or legal news. `config/follow.yml` carries a `search:` hint per
person to start from; do not treat it as the only query.

This exists because feed-only coverage leaves sections empty for months at a time —
Karpathy has not uploaded since February 2025 — while the person is still active and
being written about. An empty section for someone genuinely quiet is correct; an
empty section for someone who was on a podcast yesterday is a miss.

**Rank primary over secondary.** If someone published a post *and* was written about,
lead with the post. Mark secondary items plainly in the source field: use the
publication, not the person — `(techcrunch, 2026-08-31)`, not `(news, ...)`.

**Do not let pass two inflate the page.** If a search turns up nothing but SEO
listicles, recycled profiles, or "top 10 AI thinkers" filler, that person had nothing.
Say nothing rather than pad. Secondary coverage has to carry actual news.

## Format

```markdown
---
date: 2026-09-04
generated_by: gemini
---

## Simon Willison
- **Title of the thing** (blog, 2026-09-03) [link](https://example.com/permalink)
  The first paragraph of the summary. What the piece actually says.

  The second paragraph. Why it matters here.
```

Indented lines under a bullet are the summary. A blank line inside that indented
block starts a new paragraph — use it; two paragraphs read far better than one
dense block.

## Links must be permalinks

Link the specific thing, at a URL that will still show that thing in six months.

- **Yes**: `https://docs.anthropic.com/en/release-notes/claude-code#v2-1-260`, a
  GitHub commit SHA or PR number, a dated post URL, a tagged release.
- **No**: a release-notes index, `/blog`, `/latest`, a feed URL, a homepage, a
  search results page.

If a source only publishes a rolling page, link the rolling page but anchor to the
version or date if the page has anchors, and say in the summary which version or
date you are describing — so the item still makes sense once the page has moved on.

## Summaries: give the reader the content, not a description of it

This is the part worth spending your effort on. **100–180 words, usually two
paragraphs.** The old one-sentence version was useless and has been replaced.

**The failure to avoid** is writing *about* a piece from the outside:

> ✗ A reflection on economic growth metrics, consumption measures, and
> cross-country comparisons in living standards.

That tells the reader nothing they could not guess from the title. It is a
category, not information. Write what the piece actually claims:

> ✓ Cowen argues real GDP per capita understates living-standard gains because it
> misses quality improvements in goods whose nominal price has not moved — his
> example is that a 1990 television and a 2026 television both cost about $400 but
> are not the same product. He concedes the measure is still the least-bad
> available for cross-country work.
>
> Relevant to the data-centre power argument he has been running for weeks: the
> same measurement gap shows up in how compute spending gets counted.

**Rules for the summary:**

- **Lead with the substance.** The specific claim, the number, the name, the
  mechanism, the version, what changed. If you cannot say something specific, you
  have not read it closely enough — go back.
- **Second paragraph is the "so what"** — how it connects to something else on the
  follow list, to a running argument, to what the reader already uses. Skip it if
  there is genuinely no connection; do not manufacture one.
- **Banned openings**, because they always precede an empty sentence: "explores",
  "examines", "delves into", "discusses", "a reflection on", "a look at", "covers",
  "highlights", "sheds light on", "dives deep".
- **No marketing voice.** No "game-changing", "powerful", "seamless". Flat and
  specific beats enthusiastic and vague.
- **Say when you are uncertain.** "The post does not say whether…" is useful.
  Guessing and sounding confident is not.
- **Never invent.** No fabricated titles, dates, URLs, figures or quotes. If you
  cannot verify it, leave the item out. An item missing is fine; an item wrong
  poisons the whole page.

## Rules

- **People before topics.** Topic headings must start with `Topic:` — that is what
  tags them on the page.
- **One `##` heading per person or topic.** Skip anyone with nothing new; no heading,
  no empty section. Do not pad.
- **Every item needs a source and a date** in the parenthetical, in that order:
  `(source, YYYY-MM-DD)`. The build renders it as `BLOG · 3 SEP`.
- **Cap at 4 items per person**, and spend that budget on the best four, not the
  first four. Tyler Cowen alone can produce a dozen posts a day; picking is the job.
  The cap counts both passes together.
- **An empty day is fine.** Write the file with frontmatter and no sections. The page
  renders "Nothing new on the list today." Honest beats padded.
- **No run at all is also survivable** — the site keeps showing the newest day with a
  visible stale banner. Prefer an empty day file to silence.

## Housekeeping you should report, not fix

`config/follow.yml` marks some feeds `UNVERIFIED`. Fetch them as you go and tell the
user which ones 404 or have moved. Do not edit the file yourself — report, and let
the user decide.

The build tolerates a bullet that misses a link, a source or a summary; it does not
tolerate you editing anything outside `days/`.
