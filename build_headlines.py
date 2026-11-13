#!/usr/bin/env python3
"""Build headlines.json from the RSS/Atom feeds listed in feeds.json.

Standard library only. No API keys, no paid services.
Each story's summary is the short blurb the outlet itself publishes in its feed
(trimmed); nothing is rewritten or generated.

Usage:  python scripts/build_headlines.py [--feeds feeds.json] [--out headlines.json]
"""
import argparse
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

ET_TZ = ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (compatible; NewsBriefBot/1.0)"
STOP = set("the and for with from that this are was were has have will after over into about says say new its his her their how why what who you your out not but can may more than".split())


def fetch(url, tries=2):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except Exception as e:  # network errors, HTTP errors, timeouts
            last = e
    raise last


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def text_of(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def clean(s):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*The post .{0,200}? appeared first on .{0,100}$", "", s)
    s = re.sub(r"\s*(Read more|Continue reading|Click here).{0,40}$", "", s, flags=re.I)
    return s.strip()


def trim(s, limit=260):
    if len(s) <= limit:
        return s
    cut = s[:limit]
    m = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if m >= limit * 0.55:
        return cut[: m + 1]
    return cut.rsplit(" ", 1)[0].rstrip(",;:- ") + "…"


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def parse_feed(data):
    root = ET.fromstring(data)
    out = []
    for it in root.iter():
        kind = local(it.tag)
        if kind not in ("item", "entry"):
            continue
        f = {"title": "", "link": "", "desc": "", "date": None}
        for ch in it:
            n = local(ch.tag)
            if n == "title":
                f["title"] = clean(text_of(ch))
            elif n == "link":
                href = ch.get("href")
                if href and (ch.get("rel") in (None, "alternate")):
                    f["link"] = f["link"] or href
                elif not href and text_of(ch):
                    f["link"] = text_of(ch)
            elif n in ("description", "summary") and not f["desc"]:
                f["desc"] = clean(text_of(ch))
            elif n in ("encoded", "content") and not f["desc"]:
                f["desc"] = clean(text_of(ch))
            elif n in ("pubDate", "published", "updated", "date") and not f["date"]:
                f["date"] = parse_date(text_of(ch))
        if f["title"] and f["link"].startswith(("http://", "https://")):
            out.append(f)
    return out


def tokens(t):
    t = re.sub(r"[^a-z0-9\s]", " ", t.lower())
    return {w for w in t.split() if len(w) > 2 and w not in STOP}


def sim(a, b):
    if not a or not b:
        return 0.0
    n = len(a & b)
    return n / (len(a) + len(b) - n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feeds", default="feeds.json")
    ap.add_argument("--out", default="headlines.json")
    args = ap.parse_args()

    cfg = json.load(open(args.feeds, encoding="utf-8"))
    days = cfg.get("days", 3)
    cap = cfg.get("max_items_per_section", 15)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    by_section = {s["id"]: [] for s in cfg["sections"]}
    ok, failed = 0, []

    for fd in cfg["feeds"]:
        try:
            items = parse_feed(fetch(fd["url"]))
            if not items:
                raise ValueError("no items found")
        except Exception as e:
            failed.append(fd["name"] + " (" + fd["section"] + "): " + str(e)[:80])
            print("FAILED  ", fd["name"], fd["url"], "-", e, file=sys.stderr)
            continue
        ok += 1
        kept = 0
        for it in items:
            d = it["date"] or now          # undated items count as "now"
            if d < cutoff or d > now + timedelta(hours=6):
                continue
            by_section[fd["section"]].append({**it, "date": d, "outlet": fd["name"], "bias": fd.get("bias")})
            kept += 1
        print("ok      ", fd["name"], "-", kept, "recent of", len(items), file=sys.stderr)

    sections_out = []
    for sec in cfg["sections"]:
        arts = sorted(by_section[sec["id"]], key=lambda a: a["date"], reverse=True)
        groups = []
        for a in arts:
            tk = tokens(a["title"])
            g = next((x for x in groups if sim(x["tk"], tk) >= 0.5), None)
            if not g:
                g = {"tk": tk, "items": [], "outlets": set()}
                groups.append(g)
            if a["outlet"] in g["outlets"]:
                continue
            g["outlets"].add(a["outlet"])
            g["items"].append(a)

        stories = []
        for g in groups:
            its = g["items"]
            # Prefer a "Balanced" outlet for the headline and blurb; otherwise the first seen.
            pref = [i for i in its if i["bias"] == 0] or its
            head = pref[0]
            blurbs = [i for i in pref + its if i["desc"] and i["desc"].lower()[:40] != i["title"].lower()[:40]]
            summary = trim(max(blurbs[:3], key=lambda i: len(i["desc"]))["desc"]) if blurbs else ""
            newest = max(i["date"] for i in its)
            et = newest.astimezone(ET_TZ)
            stories.append({
                "date": et.strftime("%Y-%m-%d"),
                "time": et.strftime("%-I:%M %p"),
                "headline": head["title"],
                "summary": summary,
                "sources": [{"outlet": i["outlet"], "title": i["title"], "url": i["link"], "bias": i["bias"]} for i in its[:5]],
                "_k": (et.strftime("%Y-%m-%d"), len(its), newest.timestamp()),
            })
        stories.sort(key=lambda s: s["_k"], reverse=True)
        for s in stories:
            del s["_k"]
        sections_out.append({"id": sec["id"], "name": sec["name"], "items": stories[:cap]})

    total = len(cfg["feeds"])
    if ok == 0:
        print("All feeds failed; leaving the existing headlines file untouched.", file=sys.stderr)
        sys.exit(1)

    out = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": days,
        "feed_status": {"ok": ok, "total": total, "failed": failed},
        "sections": sections_out,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n = sum(len(s["items"]) for s in sections_out)
    print("wrote", args.out, "-", n, "stories,", ok, "of", total, "feeds ok", file=sys.stderr)


if __name__ == "__main__":
    main()
