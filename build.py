#!/usr/bin/env python3
"""Build the daily briefing site.

Reads days/YYYY-MM-DD.md and writes a static site to _site/. Stdlib only.
The research agent only ever writes day files; this turns that folder into
index.html, one page per day, and the archive.

    python build.py            # build to _site/
    python build.py --serve    # build, then serve on http://localhost:8000
"""

import html
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
DAYS_DIR = os.path.join(ROOT, "days")
OUT_DIR = os.path.join(ROOT, "_site")
ASSETS_DIR = os.path.join(ROOT, "assets")

DAY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

FONTS = ("https://fonts.googleapis.com/css2"
         "?family=IBM+Plex+Mono:wght@500;600"
         "&family=IBM+Plex+Sans:wght@400;600"
         "&family=Newsreader:opsz,wght@6..72,400;6..72,500"
         "&display=swap")


# ---------------------------------------------------------------------------
# a very small markdown subset
# ---------------------------------------------------------------------------

def split_frontmatter(text):
    """Return (meta dict, body). Frontmatter is flat `key: value` lines."""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip("'\"")
            return meta, text[end + 4:].lstrip("\n")
    return meta, text


LINK_RE = re.compile(r"\[([^\]]*)\]\((\S+?)\)")
BARE_URL_RE = re.compile(r"(?<![\"'=>\w])(https?://[^\s<>)\]]+)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<![*\w])\*([^*]+?)\*(?!\*)")
CODE_RE = re.compile(r"`([^`]+?)`")
PAREN_RE = re.compile(r"\(([^()]*)\)")


def inline(text):
    """Escape, then apply the inline markdown we actually use."""
    out = html.escape(text, quote=False)
    out = CODE_RE.sub(lambda m: "<code>{}</code>".format(m.group(1)), out)
    out = LINK_RE.sub(
        lambda m: '<a href="{}" rel="noopener">{}</a>'.format(
            html.escape(m.group(2), quote=True), m.group(1) or "link"), out)
    out = BARE_URL_RE.sub(
        lambda m: '<a href="{0}" rel="noopener">{0}</a>'.format(
            html.escape(m.group(1), quote=True)), out)
    out = BOLD_RE.sub(lambda m: "<strong>{}</strong>".format(m.group(1)), out)
    out = ITALIC_RE.sub(lambda m: "<em>{}</em>".format(m.group(1)), out)
    return out


def plain(text):
    """Inline markdown stripped to bare text."""
    out = LINK_RE.sub(lambda m: m.group(1), text)
    out = out.replace("**", "").replace("`", "")
    return out.strip()


def parse_item(head):
    """Pull `**Title** (source, date) [link](url)` apart.

    Every part is optional. Whatever is left after the recognised bits are
    lifted out becomes the title, so a bullet in any shape still renders.
    """
    rest = head

    url = ""
    m = LINK_RE.search(rest)
    if m:
        url = m.group(2)
        rest = (rest[:m.start()] + rest[m.end():])
    else:
        m = BARE_URL_RE.search(rest)
        if m:
            url = m.group(1)
            rest = rest[:m.start()] + rest[m.end():]

    source = ""
    m = PAREN_RE.search(rest)
    if m:
        source = m.group(1).strip()
        rest = rest[:m.start()] + rest[m.end():]

    m = BOLD_RE.search(rest)
    title = m.group(1).strip() if m else rest
    title = plain(title).strip(" —-–,;")
    if not title:
        title = plain(head) or "Untitled"

    return {"title": title, "source": source, "url": url}


def parse_body(body):
    """Body -> [{'title', 'items': [{'head','note'}], 'prose': [...]}]."""
    sections = []
    state = {"current": None, "item": None}

    def new_section(title):
        sec = {"title": title, "items": [], "prose": []}
        sections.append(sec)
        state["current"] = sec

    def flush_item():
        if state["item"] is not None:
            if state["current"] is None:
                new_section("")
            state["current"]["items"].append(state["item"])
        state["item"] = None

    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("## "):
            flush_item()
            new_section(line[3:].strip())
            continue
        if line.startswith("#"):
            continue  # a stray H1 would only repeat the page title

        stripped = line.strip()
        bullet = stripped.startswith("- ") or stripped.startswith("* ")
        indented = line.startswith(" ") or line.startswith("\t")

        if bullet and not indented:
            flush_item()
            if state["current"] is None:
                new_section("")
            state["item"] = {"head": stripped[2:].strip(), "note": ""}
            continue
        if state["item"] is not None and indented:
            note = stripped[2:].strip() if bullet else stripped
            state["item"]["note"] = (state["item"]["note"] + " " + note).strip()
            continue

        flush_item()
        if state["current"] is None:
            new_section("")
        state["current"]["prose"].append(stripped)

    flush_item()
    return sections


def load_days():
    days = []
    if not os.path.isdir(DAYS_DIR):
        return days
    for name in sorted(os.listdir(DAYS_DIR), reverse=True):
        m = DAY_RE.match(name)
        if not m:
            continue
        with open(os.path.join(DAYS_DIR, name), encoding="utf-8") as fh:
            meta, body = split_frontmatter(fh.read())
        sections = parse_body(body)
        days.append({
            "slug": m.group(1),
            "meta": meta,
            "sections": sections,
            "count": sum(len(s["items"]) for s in sections),
        })
    return days


# ---------------------------------------------------------------------------
# dates
# ---------------------------------------------------------------------------

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]


def parse_slug(slug):
    try:
        return datetime.strptime(slug.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def pretty_date(slug):
    d = parse_slug(slug)
    if d is None:
        return slug
    return "{} {} {} {}".format(
        WEEKDAYS[d.weekday()], d.day, MONTHS_LONG[d.month - 1], d.year)


def short_date(text):
    d = parse_slug(text)
    return text if d is None else "{} {}".format(d.day, MONTHS[d.month - 1])


def days_ago(slug):
    d = parse_slug(slug)
    return None if d is None else (date.today() - d).days


def dispatch_line(source):
    """`blog, 2026-09-03` -> `BLOG · 3 SEP`. Anything else passes through."""
    if not source:
        return ""
    parts = [p.strip() for p in source.split(",") if p.strip()]
    return " · ".join(short_date(p) for p in parts)


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def page(title, body, depth=0, description=""):
    prefix = "../" * depth
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<main>
{body}
</main>
</body>
</html>
""".format(title=html.escape(title), desc=html.escape(description, quote=True),
           fonts=html.escape(FONTS, quote=True), prefix=prefix, body=body)


def render_heading(title, count):
    is_topic = title.lower().startswith("topic")
    label = title.split(":", 1)[1].strip() if (is_topic and ":" in title) else title
    tally = "{}".format(count) if count else ""
    parts = ['<h2 class="{}">'.format("topic" if is_topic else "person")]
    if is_topic:
        parts.append('<span class="tag">Topic</span>')
    parts.append('<span class="name">{}</span>'.format(inline(label)))
    if tally:
        parts.append('<span class="count">{}</span>'.format(tally))
    parts.append("</h2>")
    return "".join(parts)


def render_sections(sections):
    parts = []
    for sec in sections:
        parts.append("<section>")
        if sec["title"]:
            parts.append(render_heading(sec["title"], len(sec["items"])))
        for p in sec["prose"]:
            parts.append('<p class="note">{}</p>'.format(inline(p)))
        if sec["items"]:
            parts.append("<ul>")
            for it in sec["items"]:
                parsed = parse_item(it["head"])
                title = html.escape(parsed["title"], quote=False)
                if parsed["url"]:
                    title = '<a href="{}" rel="noopener">{}</a>'.format(
                        html.escape(parsed["url"], quote=True), title)
                parts.append("<li>")
                parts.append('<div class="head">{}</div>'.format(title))
                line = dispatch_line(parsed["source"])
                if line:
                    parts.append('<p class="dispatch">{}</p>'.format(
                        html.escape(line, quote=False)))
                if it["note"]:
                    parts.append('<p class="note">{}</p>'.format(inline(it["note"])))
                parts.append("</li>")
            parts.append("</ul>")
        parts.append("</section>")
    return "\n".join(parts)


def render_day(day, depth, is_index, newest_slug=None):
    parts = ['<header class="masthead">',
             '<p class="kicker">Daily briefing</p>',
             "<h1>{}</h1>".format(html.escape(pretty_date(day["slug"])))]
    ago = days_ago(day["slug"])
    if is_index and ago is not None and ago > 0:
        aged = ("this is yesterday's" if ago == 1
                else "this is {} days old".format(ago))
        parts.append('<p class="stale">No run has landed for today '
                     "&mdash; {}.</p>".format(aged))
    parts.append("</header>")

    if day["count"] == 0 and not any(s["prose"] for s in day["sections"]):
        parts.append('<p class="empty">Nothing new on the list today.</p>')
    else:
        parts.append(render_sections(day["sections"]))

    prefix = "../" * depth
    nav = ['<nav class="foot">']
    if not is_index and newest_slug and newest_slug != day["slug"]:
        nav.append('<a href="{}index.html">Today</a>'.format(prefix))
    nav.append('<a href="{}archive/index.html">Archive</a>'.format(prefix))
    by = day["meta"].get("generated_by")
    if by:
        nav.append('<span class="by">via {}</span>'.format(html.escape(by)))
    nav.append("</nav>")
    parts.append("\n".join(nav))
    return "\n".join(parts)


def render_archive(days):
    parts = ['<header class="masthead">',
             '<p class="kicker">Daily briefing</p>',
             "<h1>Archive</h1>",
             "</header>"]
    if not days:
        parts.append('<p class="empty">No briefings yet.</p>')
    else:
        parts.append('<ul class="archive">')
        for d in days:
            n = d["count"]
            label = "empty" if n == 0 else ("1 item" if n == 1 else "%d items" % n)
            parts.append(
                '<li><a href="../days/{slug}.html">{pretty}</a>'
                '<span class="count">{label}</span></li>'.format(
                    slug=d["slug"], pretty=html.escape(pretty_date(d["slug"])),
                    label=label))
        parts.append("</ul>")
    parts.append('<nav class="foot"><a href="../index.html">Today</a></nav>')
    return "\n".join(parts)


# ---------------------------------------------------------------------------

def build():
    days = load_days()
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(os.path.join(OUT_DIR, "days"))
    os.makedirs(os.path.join(OUT_DIR, "archive"))

    if os.path.isdir(ASSETS_DIR):
        shutil.copytree(ASSETS_DIR, os.path.join(OUT_DIR, "assets"))
    open(os.path.join(OUT_DIR, ".nojekyll"), "w").close()  # no Jekyll pass

    newest = days[0] if days else None

    for d in days:
        body = render_day(d, depth=1, is_index=False,
                          newest_slug=newest["slug"] if newest else None)
        with open(os.path.join(OUT_DIR, "days", d["slug"] + ".html"), "w",
                  encoding="utf-8") as fh:
            fh.write(page("Briefing " + d["slug"], body, depth=1))

    if newest:
        body = render_day(newest, depth=0, is_index=True)
        title = "Daily Briefing"
    else:
        body = ('<header class="masthead"><p class="kicker">Daily briefing</p>'
                "<h1>Nothing here yet</h1></header>"
                '<p class="empty">Drop a file in days/ to get started.</p>')
        title = "Daily Briefing"
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page(title, body, depth=0,
                      description="What is new from the follow list."))

    with open(os.path.join(OUT_DIR, "archive", "index.html"), "w",
              encoding="utf-8") as fh:
        fh.write(page("Briefing Archive", render_archive(days), depth=1))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print("built {} day(s) -> {}  [{}]".format(len(days), OUT_DIR, stamp))
    if newest:
        print("newest: {} ({} items)".format(newest["slug"], newest["count"]))


def main(argv):
    build()
    if "--serve" in argv:
        import http.server
        import functools
        handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                    directory=OUT_DIR)
        print("serving http://localhost:8000  (ctrl-c to stop)")
        http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
