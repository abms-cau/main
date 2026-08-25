# ABMS Lab Website

Advanced Biomicrosystems Laboratory — School of Integrative Engineering, Chung-Ang University.

Static site. No build step required for normal edits: the HTML files are committed
directly and served as-is.

## Structure

```
index.html            Home — hero, core capabilities, join us / contact
research.html         Research — the 01–04 platform sequence
people.html           People — PI profile (expandable CV) + team cards
publications.html     Publications — journal articles, book chapters, preprints
abms-styles.css       Shared stylesheet for all four pages
tools/
  publications_data.py    Publication list as structured data
  build_publications.py   Regenerates publications.html from that data
.github/workflows/
  deploy.yml          Auto-deploys to GitHub Pages on push to main
```

## Editing

**Text, links, people** — edit the `.html` file directly, commit, push. The site
redeploys automatically in about a minute.

**Colors, spacing, fonts** — edit `abms-styles.css` only. All four pages share it,
so one change applies everywhere. The brand colors are CSS variables at the top:

```css
--blue:  #3E7BD6;   /* logo blue, links, accents */
--red:   #D0021B;   /* logo red, highlight badges */
--navy:  #0A1F44;   /* dark banners */
```

## Adding a publication

Do **not** hand-edit `publications.html` — it is generated. Instead:

1. Add an entry to `PUBS` in `tools/publications_data.py`:

   ```python
   dict(y=2026,
        a="First Author*, Hye-Ran Moon*, Last Author",
        t="Title of the paper",
        j="Journal Name",
        d="49: 941-954",                       # volume: pages, or "" if unknown
        doi="https://doi.org/10.xxxx/yyyy",     # or None
        tags=["Equal contribution"]),           # or []
   ```

   Entries are grouped by year automatically; order within the list does not matter.
   `Hye-Ran Moon` / `Hye-ran Moon` is bolded automatically wherever it appears.

2. Regenerate and commit:

   ```bash
   python3 tools/build_publications.py
   git add -A && git commit -m "Add <journal> <year> paper" && git push
   ```

Recognized `tags` that render as a highlighted badge: `Journal cover`,
`Journal back cover`, `Frontispiece`, `Hot Topic: Microfluidics`,
`Top 20 most downloaded`, `Lab on a Chip HOT Article 2023`.
`Equal contribution` is intentionally **not** rendered as a badge — mark equal
contribution with `*` directly in the author string; the footnote explains it.

Book chapters and preprints are maintained as static blocks inside
`tools/build_publications.py`.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which publishes the
repository root to GitHub Pages.

One-time setup: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

The site is then live at `https://<username>.github.io/<repo>/`. To use a custom
domain, add a `CNAME` file containing the domain and point the DNS record at
GitHub Pages.

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Opening the files directly with `file://` also works, but a local server matches
production more closely.
