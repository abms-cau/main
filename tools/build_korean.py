#!/usr/bin/env python3
"""Generate the Korean pages (index-ko, research-ko, news-ko) from their English
originals, so the markup and SVGs stay in sync and only the copy differs.

The Korean wording lives in tools/korean_copy.txt — edit that file, not this one,
and not the -ko.html files (they are overwritten on every run).

    python3 tools/build_korean.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COPY = Path(__file__).resolve().parent / "korean_copy.txt"

KO_PAGES = {"index": "index-ko", "research": "research-ko", "news": "news-ko"}

NOTO = ('<link href="https://fonts.googleapis.com/css2?'
        'family=Noto+Sans+KR:wght@400;500;700;800&display=swap" rel="stylesheet">')

# slot id -> the exact English text in the source HTML that it replaces.
# Add a slot here and in korean_copy.txt to translate something new.
SLOTS = {
    # ---- nav + footer (every page) ----
    "nav.home": "Home",
    "nav.research": "Research",
    "nav.people": "People",
    "nav.publications": "Publications",
    "nav.news": "News",
    "nav.join": "Join Us",
    "band.heading": "We are looking for our next collaborators",
    "band.body": ("Undergraduate interns, master's and doctoral candidates — if the work here\n"
                  "      interests you, reach out directly."),
    "band.button": "Contact the Lab",
    "footer.blurb": "Advanced Biomicrosystems Laboratory — School of Integrative Engineering, Chung-Ang University.",
    "footer.explore": "Explore",
    "footer.contact": "Contact",
    "footer.office": "Bldg 305, Rm 405",
    "footer.city": "Seoul, Republic of Korea",
    "footer.copyright": "© 2026 ABMS Lab, Chung-Ang University",
    "footer.labname": "Advanced Biomicrosystems Laboratory",

    # ---- home ----
    "home.title": "ABMS Lab — Advanced Biomicrosystems Laboratory",
    "home.eyebrow": "Advanced Biomicrosystems Laboratory",
    "home.h1": "Engineering <em>Biomicrosystems</em><br>for Human-Relevant Biology",
    "home.sub": ("We develop next-generation biomicrosystems through innovative engineering platforms,\n"
                 "      enabling translation to human physiology, pathology, and advanced biomedical applications."),
    "home.cta": "Explore Our Research",
    "home.cap.label": "Core Capabilities",
    "home.cap.h2": "The expertise behind the platform",
    "home.cap.lede": ("Four areas of technical depth that the work above draws on, spanning device\n"
                      "        fabrication through to computational analysis."),
    "home.cap1.h3": "Microfluidic bioengineering",
    "home.cap1.p": "Device design and microfabrication tailored to the tissue being modeled, not adapted from off-the-shelf plates.",
    "home.cap2.h3": "Tumor microenvironment modeling",
    "home.cap2.p": "Reconstructing the physical and cellular context in which tumors actually behave.",
    "home.cap3.h3": "Biosensing &amp; readout",
    "home.cap3.p": "On-chip sensors that turn continuous biological activity into analyzable signal.",
    "home.cap4.h3": "Standardization &amp; precision medicine",
    "home.cap4.p": "Machine learning applied to making organoid and organ-on-chip data comparable across sources.",
    "home.join.label": "Join Us &amp; Contact",
    "home.join.h2": "The ABMS Lab welcomes motivated, passionate, and committed students.",
    "home.join.kr": "첨단 바이오마이크로시스템 연구실에서 함께 연구할 학부 인턴 및 대학원생을 모집합니다.",
    "home.join.en": ("Opportunities are available for undergraduate research interns and prospective\n"
                     "        M.S. and Ph.D. students.<br>\n"
                     "        Interested students are welcome to contact Prof. Moon for more information."),
    "home.contact.label": "Contact",
    "home.contact.h3": "Open to motivated students at every stage",
    "home.contact.pi.k": "Principal Investigator",
    "home.contact.pi.v": "Prof. Hye-ran Moon",
    "home.contact.email.k": "Email",
    "home.contact.office.k": "Office",
    "home.contact.office.v": "Bldg 305, Rm 405",
    "home.contact.inst.k": "Institution",
    "home.contact.inst.v": "Chung-Ang University",
    "home.contact.button": "Send an Inquiry",

    # ---- research ----
    "res.title": "Research — ABMS Lab",
    "res.crumb": "Research",
    "res.eyebrow": "Research",
    "res.h1": "From engineered tissue to standardized data",
    "res.sub": ("We design the device, culture the tissue inside it, instrument it with sensors,\n"
                "      and standardize the resulting measurements &mdash; physiologically faithful\n"
                "      in vitro models on one side, and the AI-based methods that make their data\n"
                "      comparable on the other."),
    "res.hint": "Select a topic to read more.",
    "res.01.cat": "In vitro models",
    "res.01.h3": "Advanced <em>in vitro</em> models",
    "res.01.lede": "Microphysiological systems that reconstruct the human tissue microenvironment.",
    "res.01.caption": ("Reconstructing the tumor microenvironment in a microphysiological system: "
                       "human cell sources, a tunable ECM, and controlled vascular, interstitial and lymphatic flow."),
    "res.01.alt": ("Diagram comparing the tumor microenvironment in vivo with a microphysiological system "
                   "in vitro, and the three building blocks used to rebuild it: human cell sources, ECM/matrix, "
                   "and controlled flow."),
    "res.02.cat": "Sensing",
    "res.02.h3": "Sensor-integrated organoid-on-a-chip",
    "res.02.lede": "Biosensors built into the device for continuous, real-time readout.",
    "res.03.cat": "Mechanobiology",
    "res.03.h3": "Mechanobiology",
    "res.03.lede": "How mechanical cues &mdash; flow, pressure, matrix stiffness &mdash; shape cell behaviour.",
    "res.04.cat": "Data &amp; AI",
    "res.04.h3": "Data standardization with AI/ML",
    "res.04.lede": "Making organoid and organ-chip data comparable across labs and devices.",
    "res.zoom": "Click to enlarge",

    # ---- news ----
    "news.title": "News — ABMS Lab",
    "news.crumb": "News",
    "news.eyebrow": "News",
    "news.h1": "Announcements and updates",
    "news.1.date": "September 2025",
    "news.1.tag": "Lab",
    "news.1.h3": "The ABMS Lab opens at Chung-Ang University",
    "news.1.body": ("The Advanced Biomicrosystems Laboratory has officially opened in the School of\n"
                    "            Integrative Engineering at Chung-Ang University, led by Prof. Hye-ran Moon."),
}

# Which slots belong to which page. Shared chrome applies everywhere.
SHARED = [k for k in SLOTS if k.startswith(("nav.", "band.", "footer."))]
PAGE_SLOTS = {
    "index": SHARED + [k for k in SLOTS if k.startswith("home.")],
    "research": SHARED + [k for k in SLOTS if k.startswith("res.")],
    "news": SHARED + [k for k in SLOTS if k.startswith("news.")],
}

# Slots whose English text is a bare word that also occurs elsewhere, so they
# must be matched with surrounding markup rather than on their own.
CONTEXT = {
    "nav.home": '>{}</a></li>',
    "nav.research": '>{}</a></li>',
    "nav.people": '>{}</a></li>',
    "nav.publications": '>{}</a></li>',
    "nav.news": '>{}</a></li>',
    "nav.join": '>{}</a></li>',
    "band.button": '>{}</a>',
    "home.cta": '>{}</a>',
    "home.contact.button": '>{}</a>',
    "footer.explore": '<h4>{}</h4>',
    "footer.contact": '<h4>{}</h4>',
    "footer.office": '<li>{}</li>',
    "footer.city": '<li>{}</li>',
    "footer.copyright": '<span>{}</span>',
    "footer.labname": '<span>{}</span>',
    "home.contact.label": '<span class="mono">{}</span>',
    "home.contact.pi.k": '<span class="cl">{}</span>',
    "home.contact.email.k": '<span class="cl">{}</span>',
    "home.contact.office.k": '<span class="cl">{}</span>',
    "home.contact.inst.k": '<span class="cl">{}</span>',
    "home.contact.pi.v": '<span class="cv">{}</span>',
    "home.contact.office.v": '<span class="cv">{}</span>',
    "home.contact.inst.v": '<span class="cv">{}</span>',
    "res.crumb": '<span>{}</span>',
    "news.crumb": '<span>{}</span>',
    "res.eyebrow": '<span class="eyebrow mono">{}</span>',
    "news.eyebrow": '<span class="eyebrow mono">{}</span>',
    "home.eyebrow": '<span class="eyebrow mono">{}</span>',
    "home.cap.label": '<span class="mono">{}</span>',
    "home.join.label": '<span class="mono">{}</span>',
    "res.01.cat": '<span class="rcat mono">{}</span>',
    "res.02.cat": '<span class="rcat mono">{}</span>',
    "res.03.cat": '<span class="rcat mono">{}</span>',
    "res.04.cat": '<span class="rcat mono">{}</span>',
    "news.1.date": '<span class="d">{}</span>',
    "news.1.tag": '<span class="ntag">{}</span>',
    "res.01.caption": 'data-cap="{}"',
    "res.01.alt": 'alt="{}"',
}

LANG_KO = ('    <a class="langbtn" href="{target}" hreflang="en" lang="en" '
           'aria-label="Read this page in English">EN</a>\n')
LANG_EN = ('    <a class="langbtn" href="{target}" hreflang="ko" lang="ko" '
           'aria-label="이 페이지를 한국어로 보기">한국어</a>\n')


def read_copy() -> dict:
    """Parse tools/korean_copy.txt: [slot.id] lines, '>' comment lines, then the text."""
    out, slot, buf = {}, None, []
    for raw in COPY.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("[") and line.endswith("]"):
            if slot:
                out[slot] = "\n".join(buf).strip("\n")
            slot, buf = line[1:-1].strip(), []
        elif line.startswith("#") or line.startswith(">"):
            continue
        elif slot is not None:
            buf.append(line)
    if slot:
        out[slot] = "\n".join(buf).strip("\n")
    return {k: v for k, v in out.items() if v.strip()}


def build_ko(stem: str, copy: dict) -> str:
    src = (ROOT / f"{stem}.html").read_text(encoding="utf-8")

    for en, ko in KO_PAGES.items():
        src = src.replace(f'href="{en}.html"', f'href="{ko}.html"')
        src = src.replace(f'href="{en}.html#', f'href="{ko}.html#')

    src = src.replace('<html lang="en">', '<html lang="ko">')
    src = src.replace('<link rel="stylesheet" href="abms-styles.css">',
                      NOTO + '\n<link rel="stylesheet" href="abms-styles.css">')
    misses = []
    for slot in PAGE_SLOTS[stem]:
        ko = copy.get(slot)
        if not ko:
            continue
        en = SLOTS[slot]
        wrap = CONTEXT.get(slot)
        a, b = (wrap.format(en), wrap.format(ko)) if wrap else (en, ko)
        if a in src:
            src = src.replace(a, b)
        elif slot not in SHARED:
            # shared chrome legitimately varies between pages; only flag the rest
            misses.append(slot)
    if misses:
        print(f"  ! {stem}: no match for {', '.join(misses)}", file=sys.stderr)

    # <title> is keyed per page
    for slot in ("home.title", "res.title", "news.title"):
        if slot in copy and SLOTS[slot] in src:
            src = src.replace(f"<title>{SLOTS[slot]}</title>", f"<title>{copy[slot]}</title>")

    src = re.sub(r'\n *<a class="langbtn".*?</a>\n', '\n', src, flags=re.S)
    return src.replace('    </ul>\n  </nav>',
                       '    </ul>\n' + LANG_KO.format(target=f"{stem}.html") + '  </nav>', 1)


def main() -> int:
    copy = read_copy()
    print(f"{len(copy)} slot(s) filled in korean_copy.txt")

    for stem, ko_stem in KO_PAGES.items():
        (ROOT / f"{ko_stem}.html").write_text(build_ko(stem, copy), encoding="utf-8")
        print(f"wrote {ko_stem}.html")

    for path in sorted(ROOT.glob("*.html")):
        if path.stem.endswith("-ko"):
            continue
        target = f"{KO_PAGES[path.stem]}.html" if path.stem in KO_PAGES else "index-ko.html"
        html = path.read_text(encoding="utf-8")
        new = re.sub(r'\n *<a class="langbtn".*?</a>\n', '\n', html, flags=re.S)
        new = new.replace('    </ul>\n  </nav>',
                          '    </ul>\n' + LANG_EN.format(target=target) + '  </nav>', 1)
        if new != html:
            path.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
