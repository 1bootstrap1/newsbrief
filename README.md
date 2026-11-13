# News Brief

A small static site: a weekly multi-source news brief (world, national, local, sports), a market snapshot, and an analysis tab. No build step, no dependencies.

## Files

| File | Purpose |
|---|---|
| `index.html` | Layout, styling and rendering code. Rarely changes. |
| `edition.json` | **The content.** Replace this file to publish a new edition. |
| `sw.js` | Service worker: loads fresh content when online, last saved copy when offline. |
| `manifest.webmanifest`, `icon-*.png` | Let you "Add to Home Screen" so it opens like an app. |

## Host it on GitHub Pages

1. Create a new repository on GitHub (e.g. `newsbrief`). Public is simplest; Pages on a private repo needs a paid plan.
2. Upload all files in this folder to the repository root (**Add file → Upload files**), then commit.
3. Go to **Settings → Pages**. Under **Build and deployment**, set **Source: Deploy from a branch**, branch **main**, folder **/ (root)**, and save.
4. After a minute the site is live at `https://<your-username>.github.io/<repo-name>/`.

## Put it on your phone

- **iPhone (Safari):** open the address, tap Share, then **Add to Home Screen**.
- **Android (Chrome):** open the address, tap the menu, then **Install app** / **Add to Home screen**.

## Publish a new edition

Replace `edition.json` (on GitHub: open the file, pencil icon, paste, commit; or upload over it). The page picks it up on the next load. The **Reload** button forces a refresh.

`edition.json` shape: `title`, `edition_date`, `range{start,end}`, `purpose`, `footer`, `sections[]` (each with `items[]` of `date`, `headline`, `summary`, optional `note`, and `sources[]` with `outlet`, `title`, `url`, `bias`), `markets`, and `analysis`. Source `bias` is -2 Left, -1 Lean Left, 0 Balanced, 1 Lean Right, 2 Right, or `null` for Unrated.

## Notes

- Opening `index.html` directly from disk will not work, because browsers block `fetch` on `file://`. Use the hosted address, or run `python3 -m http.server` in this folder and visit `http://localhost:8000`.
- Everything on the page is public once hosted on a public repo.
