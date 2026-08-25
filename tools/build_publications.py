#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate publications.html from tools/publications_data.py.

Usage:  python3 tools/build_publications.py

Reuses the existing publications.html for the shared header / page banner /
footer, so edits to those (nav links, banner text) survive regeneration.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from publications_data import PUBS  # noqa: E402

PAGE = os.path.join(ROOT, "publications.html")

# Tags rendered as a red "highlight" badge. "Equal contribution" is deliberately
# excluded — equal contribution is shown with * in the author string instead.
HIGHLIGHT = {
    "Journal cover",
    "Journal back cover",
    "Frontispiece",
    "Hot Topic: Microfluidics",
    "Top 20 most downloaded",
    "Lab on a Chip HOT Article 2023",
}
HIDDEN_TAGS = {"Equal contribution"}


def authors(a):
    return re.sub(r"(Hye-[Rr]an Moon)", r"<b>\1</b>", html.escape(a))


def entry(n, p):
    title = html.escape(p["t"])
    ti = (f'<a href="{p["doi"]}" target="_blank" rel="noopener">{title}</a>'
          if p.get("doi") else title)
    chips = "".join(
        f'<span class="badge{" hl" if t in HIGHLIGHT else ""}">{html.escape(t)}</span>'
        for t in p.get("tags", []) if t not in HIDDEN_TAGS
    )
    badges = f'\n            <div class="badges">{chips}</div>' if chips else ""
    det = f' <span class="dt">{html.escape(p["d"])}</span>' if p.get("d") else ""
    return (
        '        <div class="pub">\n'
        f'          <div class="n">{n:02d}</div>\n'
        "          <div>\n"
        f'            <div class="ti">{ti}</div>\n'
        f'            <div class="au">{authors(p["a"])}</div>\n'
        f'            <div class="jr"><em>{html.escape(p["j"])}</em>{det}</div>{badges}\n'
        "          </div>\n"
        "        </div>"
    )


def journal_blocks():
    years = sorted({p["y"] for p in PUBS}, reverse=True)
    idx = len(PUBS)
    out = []
    for y in years:
        rows = []
        for p in [x for x in PUBS if x["y"] == y]:
            rows.append(entry(idx, p))
            idx -= 1
        out.append(
            '      <div class="yearblock">\n'
            '        <div class="yearbar">\n'
            f'          <span class="yr">{y}</span>\n'
            "        </div>\n"
            + "\n".join(rows)
            + "\n      </div>"
        )
    return "\n".join(out)


# --- Static sections. Edit here to add a book chapter or preprint. -----------
BOOKS = """
    <div class="pubgroup second">
      <h2>Book Chapters</h2>
    </div>

    <div class="yearblock">
      <div class="yearbar"><span class="yr">2024</span></div>
      <div class="pub">
        <div class="n">02</div>
        <div>
          <div class="ti"><a href="https://doi.org/10.1007/978-1-0716-3674-9_17" target="_blank" rel="noopener">Tumor-Microenvironment-on-Chip Platform for Assessing Drug Response in 3D Dynamic Culture</a></div>
          <div class="au">Hakan Berk Aydin, <b>Hye-ran Moon</b>, Bumsoo Han, Altug Ozcelikkale, Ahmet Acar</div>
          <div class="jr">In: Z. Sumbalova Koledova (ed.), <em>3D Cell Culture</em> <span class="dt">Methods in Molecular Biology, vol. 2764 &middot; Humana, New York &middot; 265&ndash;278</span></div>
        </div>
      </div>
    </div>

    <div class="yearblock">
      <div class="yearbar"><span class="yr">2020</span></div>
      <div class="pub">
        <div class="n">01</div>
        <div>
          <div class="ti"><a href="https://doi.org/10.1016/B978-0-08-102983-1.00015-6" target="_blank" rel="noopener">Engineered tumor models for cancer biology and treatment</a></div>
          <div class="au"><b>Hye-ran Moon</b>, Bumsoo Han</div>
          <div class="jr">In: K. Park (ed.), <em>Biomaterials for Cancer Therapeutics</em>, 2nd ed. <span class="dt">Woodhead Publishing &middot; 423&ndash;443</span></div>
        </div>
      </div>
    </div>
"""

PREPRINTS = """
    <div class="pubgroup second">
      <h2>Preprints</h2>
    </div>

    <div class="yearblock">
      <div class="yearbar"><span class="yr">2026</span></div>
      <div class="pub">
        <div class="n">01</div>
        <div>
          <div class="ti">Extravascular coagulation stabilizes pro-fibrotic stromal states via tumor-intrinsic PAR1 signaling in pancreatic ductal adenocarcinoma</div>
          <div class="au">Sae Rome Choi, Natalia Ospina-Mu&ntilde;oz, <b>Hye-ran Moon</b>, Bumsoo Han</div>
          <div class="jr"><em>Preprint</em> <span class="dt">Under review</span></div>
        </div>
      </div>
    </div>
"""

FOOTNOTE = """
    <p class="pubnote">
      * Equal contribution. Titles link to the publisher's page where a DOI is available.
      A complete and continuously updated list is available on
      <a href="https://scholar.google.com/citations?user=2_Djq7kAAAAJ&amp;hl=en" target="_blank" rel="noopener">Google Scholar</a>.
    </p>
"""


def main():
    base = open(PAGE, encoding="utf-8").read()

    # Keep everything up to and including the page banner, and everything from
    # the CTA band onward — only the publication list itself is regenerated.
    head = base[: base.index('<section class="pubs">')]
    tail = base[base.index("<!-- ============ CTA BAND ============ -->"):]

    body = (
        '<section class="pubs">\n'
        '  <div class="wrap">\n'
        '    <div class="pubgroup">\n'
        "      <h2>Journal Articles</h2>\n"
        "    </div>\n\n"
        + journal_blocks()
        + BOOKS
        + PREPRINTS
        + FOOTNOTE
        + "  </div>\n</section>\n\n"
    )

    open(PAGE, "w", encoding="utf-8").write(head + body + tail)

    n_books = BOOKS.count('class="pub"')
    n_pre = PREPRINTS.count('class="pub"')
    print(f"publications.html rebuilt: {len(PUBS)} journal articles, "
          f"{n_books} book chapters, {n_pre} preprints")


if __name__ == "__main__":
    main()
