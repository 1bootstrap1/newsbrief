# News Brief: flat files, drag and drop

Every file here goes in the **top level** of your GitHub repository. No folders.

## Set up (about 3 minutes)

1. Create a **public** repository on GitHub.
2. Click **Add file → Upload files**. Drag in **all** of these files, then click **Commit changes**.
3. **Settings → Pages**: Source = *Deploy from a branch*, branch `main`, folder `/ (root)`, Save.
4. After a minute your site is at `https://<your-username>.github.io/<repo-name>/`.
5. On your phone, open that address and use **Add to Home Screen**.

That gives you the **Summary** and **Analysis** tabs (from `edition.json`).

## Update the Summary/Analysis tabs

Ask Claude for a new `edition.json`, then drag it into the repo (Add file → Upload files). Uploading a file with the same name replaces the old one.

## Optional: the automatic Headlines tab

The Headlines tab needs a file called `headlines.json`, which is rebuilt automatically by a free GitHub Action. Without it the tab simply does not appear, and nothing else is affected.

Files for it: `build_headlines.py`, `feeds.json` (the outlets; edit it to add or remove feeds) and `OPTIONAL-headlines-workflow.yml`.

GitHub only runs workflows from a folder named `.github/workflows`, so that one file cannot sit at the top level. To add it:

1. **Actions** tab → **set up a workflow yourself** (GitHub creates the folder for you).
2. Name the file `headlines.yml`, delete the sample text, paste in the contents of `OPTIONAL-headlines-workflow.yml`, and commit.
3. **Actions → Update headlines → Run workflow** once. After a minute `headlines.json` appears and the tab shows up.

It then refreshes itself three times a day. If you skip this part, you can delete `build_headlines.py`, `feeds.json` and the OPTIONAL file from the repo.

## Notes

- Opening `index.html` straight from disk will not work (browsers block it). Use the hosted address.
- Everything is public when the repository is public.
