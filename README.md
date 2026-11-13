# News Brief

A static site with three optional tabs:

| Tab | Data file | How it updates |
|---|---|---|
| **Headlines** | `headlines.json` | Automatically, 3 times a day, by a free GitHub Action that reads public RSS feeds. |
| **Summary** | `edition.json` | By hand: replace the file with a new blended-summary edition. |
| **Analysis** | `edition.json` | Same file as Summary (its `analysis` section). |

A tab shows only if its data loads. To drop a piece later, just delete its file (or the `analysis` block). No code changes needed.

## Files

- `index.html`: layout, styling and rendering code. Rarely changes.
- `feeds.json`: the list of news feeds (outlet, address, section, perspective rating). **Edit this to add or remove outlets.**
- `scripts/build_headlines.py`: reads the feeds and writes `headlines.json`. Standard library only, no keys, no cost.
- `.github/workflows/headlines.yml`: the schedule (about 6 AM, 11 AM and 5 PM Eastern).
- `sw.js`, `manifest.webmanifest`, `icon-*.png`: offline support and "Add to Home Screen".

## Setup (one time)

1. Upload everything in this folder to the repository root, **including the `.github` and `scripts` folders**. The repo must be public for free GitHub Pages.
2. **Settings → Pages**: Source = *Deploy from a branch*, branch `main`, folder `/ (root)`.
3. **Run the first update by hand**: **Actions** tab → *Update headlines* → **Run workflow**. (If Actions is disabled, click the green button to enable it.) After about a minute `headlines.json` appears in the repo and the Headlines tab shows up on the site.
4. If the run fails with a permissions error: **Settings → Actions → General → Workflow permissions → Read and write permissions**, save, and run it again.

## Checking and fixing feeds

The feed addresses in `feeds.json` were written from memory and some may be wrong or may block automated requests. After the first run, the Headlines tab lists any feeds that did not load. To fix one, open `feeds.json` on GitHub, correct or delete that line, and commit. The next run picks it up. The full log is under **Actions → the run → Build headlines.json**.

To find a feed address for an outlet, search the web for "<outlet name> RSS feed".

## New Summary/Analysis edition

Replace `edition.json` (on GitHub: open the file, pencil icon, paste, commit). Shape: `title`, `edition_date`, `range{start,end}`, `purpose`, `footer`, `sections[]` (items with `date`, `headline`, `summary`, optional `note`, `sources[]` with `outlet`, `title`, `url`, `bias`), `markets` (the scrolling ticker, optional), and `analysis` (optional). Perspective `bias`: -2 Left, -1 Lean Left, 0 Balanced, 1 Lean Right, 2 Right, `null` = Unrated.

## Notes

- Opening `index.html` straight from disk will not work (browsers block it). Use the hosted address, or run `python3 -m http.server` here and visit `http://localhost:8000`.
- The Headlines blurbs are each outlet's own feed text, trimmed. They are not rewritten or fact-checked.
- GitHub pauses scheduled workflows in repositories with no activity for 60 days. The automatic commits should count, but if Headlines goes stale, look at the Actions tab and re-enable it.
- Everything is public when the repository is public.
