#!/usr/bin/env python3
"""Generate the Korean pages (index-ko, research-ko, news-ko) from their English
originals, so the markup and SVGs stay in sync and only the copy differs.

Run from the repo root:  python3 tools/build_korean.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pages that exist in both languages. Everything else stays English.
KO_PAGES = {"index": "index-ko", "research": "research-ko", "news": "news-ko"}

NOTO = ('<link href="https://fonts.googleapis.com/css2?'
        'family=Noto+Sans+KR:wght@400;500;700;800&display=swap" rel="stylesheet">')

# Shared chrome: nav, join block, CTA band, footer.
COMMON = [
    # nav
    ('<li><a href="index-ko.html" class="active">Home</a></li>',
     '<li><a href="index-ko.html" class="active">홈</a></li>'),
    ('<li><a href="index-ko.html">Home</a></li>', '<li><a href="index-ko.html">홈</a></li>'),
    ('<li><a href="research-ko.html" class="active">Research</a></li>',
     '<li><a href="research-ko.html" class="active">연구</a></li>'),
    ('<li><a href="research-ko.html">Research</a></li>', '<li><a href="research-ko.html">연구</a></li>'),
    ('<li><a href="news-ko.html" class="active">News</a></li>',
     '<li><a href="news-ko.html" class="active">소식</a></li>'),
    ('<li><a href="news-ko.html">News</a></li>', '<li><a href="news-ko.html">소식</a></li>'),
    ('<li><a href="people.html">People</a></li>', '<li><a href="people.html">구성원</a></li>'),
    ('<li><a href="publications.html">Publications</a></li>',
     '<li><a href="publications.html">논문</a></li>'),
    ('<li><a href="index-ko.html#join">Join Us</a></li>',
     '<li><a href="index-ko.html#join">함께하기</a></li>'),
    # CTA band
    ('<h2>We are looking for our next collaborators</h2>',
     '<h2>함께 연구할 분을 찾고 있습니다</h2>'),
    ("""      Undergraduate interns, master's and doctoral candidates — if the work here
      interests you, reach out directly.""",
     '      학부 인턴, 석사·박사 과정 모두 환영합니다. 연구가 흥미롭다면 편하게 연락 주세요.'),
    ('>Contact the Lab<', '>연구실에 연락하기<'),
    # footer
    ('<p>Advanced Biomicrosystems Laboratory — School of Integrative Engineering, Chung-Ang University.</p>',
     '<p>첨단 바이오마이크로시스템 연구실 — 중앙대학교 융합공학부</p>'),
    ('<h4>Explore</h4>', '<h4>바로가기</h4>'),
    ('<h4>Contact</h4>', '<h4>연락처</h4>'),
    ('<li><a href="research-ko.html">Research</a></li>', '<li><a href="research-ko.html">연구</a></li>'),
    ('<li>Bldg 305, Rm 405</li>', '<li>305관 405호</li>'),
    ('<li>Seoul, Republic of Korea</li>', '<li>서울특별시 동작구</li>'),
    ('<span>© 2026 ABMS Lab, Chung-Ang University</span>', '<span>© 2026 ABMS Lab, 중앙대학교</span>'),
    ('<span>Advanced Biomicrosystems Laboratory</span>', '<span>첨단 바이오마이크로시스템 연구실</span>'),
]

INDEX = [
    ('<title>ABMS Lab — Advanced Biomicrosystems Laboratory</title>',
     '<title>ABMS Lab — 첨단 바이오마이크로시스템 연구실</title>'),
    ('<span class="eyebrow mono">Advanced Biomicrosystems Laboratory</span>',
     '<span class="eyebrow mono">첨단 바이오마이크로시스템 연구실</span>'),
    ('<h1>Engineering <em>Biomicrosystems</em><br>for Human-Relevant Biology</h1>',
     '<h1>사람에 가까운 생물학을 위한<br><em>바이오마이크로시스템</em> 공학</h1>'),
    ("""      We develop next-generation biomicrosystems through innovative engineering platforms,
      enabling translation to human physiology, pathology, and advanced biomedical applications.""",
     '      혁신적인 공학 플랫폼을 바탕으로 차세대 바이오마이크로시스템을 개발하고,\n'
     '      이를 인체의 생리와 병리, 나아가 첨단 의생명 응용으로 이어갑니다.'),
    ('>Explore Our Research<', '>연구 살펴보기<'),
    ('<span class="mono">Core Capabilities</span>', '<span class="mono">핵심 역량</span>'),
    ('<h2>The expertise behind the platform</h2>', '<h2>플랫폼을 떠받치는 기술</h2>'),
    ("""        Four areas of technical depth that the work above draws on, spanning device
        fabrication through to computational analysis.""",
     '        소자 제작부터 전산 해석까지, 연구를 떠받치는 네 가지 기술 영역입니다.'),
    ('<h3>Microfluidic bioengineering</h3>', '<h3>미세유체 바이오공학</h3>'),
    ('<p>Device design and microfabrication tailored to the tissue being modeled, not adapted from off-the-shelf plates.</p>',
     '<p>기성 플레이트를 변형해 쓰는 대신, 모사하려는 조직에 맞춰 소자를 설계하고 직접 미세가공합니다.</p>'),
    ('<h3>Tumor microenvironment modeling</h3>', '<h3>종양미세환경 모델링</h3>'),
    ('<p>Reconstructing the physical and cellular context in which tumors actually behave.</p>',
     '<p>종양이 실제로 작동하는 물리적·세포적 환경을 그대로 재현합니다.</p>'),
    ('<h3>Biosensing &amp; readout</h3>', '<h3>바이오센싱과 신호 계측</h3>'),
    ('<p>On-chip sensors that turn continuous biological activity into analyzable signal.</p>',
     '<p>칩에 집적한 센서로 생물학적 활동을 끊김 없이 분석 가능한 신호로 바꿉니다.</p>'),
    ('<h3>Standardization &amp; precision medicine</h3>', '<h3>표준화와 정밀의료</h3>'),
    ('<p>Machine learning applied to making organoid and organ-on-chip data comparable across sources.</p>',
     '<p>기계학습을 적용해 오가노이드·오간칩 데이터를 출처가 달라도 비교할 수 있게 만듭니다.</p>'),
    # join
    ('<span class="mono">Join Us &amp; Contact</span>', '<span class="mono">함께하기 · 연락처</span>'),
    ('<h2>The ABMS Lab welcomes motivated, passionate, and committed students.</h2>',
     '<h2>ABMS 연구실은 호기심과 끈기를 갖춘 학생을 환영합니다.</h2>'),
    ("""        Opportunities are available for undergraduate research interns and prospective
        M.S. and Ph.D. students.<br>
        Interested students are welcome to contact Prof. Moon for more information.""",
     '        학부 연구 인턴, 그리고 석사·박사 과정 진학을 생각 중인 학생 모두 지원할 수 있습니다.<br>\n'
     '        관심 있는 학생은 문혜란 교수에게 편하게 연락 주시기 바랍니다.'),
    ('<span class="mono">Contact</span>', '<span class="mono">연락처</span>'),
    ('<h3>Open to motivated students at every stage</h3>', '<h3>어느 단계의 학생이든 환영합니다</h3>'),
    ('<span class="cl">Principal Investigator</span><span class="cv">Prof. Hye-ran Moon</span>',
     '<span class="cl">책임교수</span><span class="cv">문혜란 교수</span>'),
    ('<span class="cl">Email</span>', '<span class="cl">이메일</span>'),
    ('<span class="cl">Office</span><span class="cv">Bldg 305, Rm 405</span>',
     '<span class="cl">연구실</span><span class="cv">305관 405호</span>'),
    ('<span class="cl">Institution</span><span class="cv">Chung-Ang University</span>',
     '<span class="cl">소속</span><span class="cv">중앙대학교</span>'),
    ('>Send an Inquiry<', '>문의 메일 보내기<'),
]

RESEARCH = [
    ('<title>Research — ABMS Lab</title>', '<title>연구 — ABMS Lab</title>'),
    ('<a href="index-ko.html">Home</a> <span>/</span> <span>Research</span>',
     '<a href="index-ko.html">홈</a> <span>/</span> <span>연구</span>'),
    ('<span class="eyebrow mono">Research</span>', '<span class="eyebrow mono">연구</span>'),
    ('<h1>From engineered tissue to standardized data</h1>',
     '<h1>조직 모델에서 표준화된 데이터까지</h1>'),
    ("""      We design the device, culture the tissue inside it, instrument it with sensors,
      and standardize the resulting measurements &mdash; physiologically faithful
      in vitro models on one side, and the AI-based methods that make their data
      comparable on the other.""",
     '      소자를 설계하고, 그 안에서 조직을 배양하고, 센서로 계측하고, 그렇게 얻은 측정값을\n'
     '      표준화합니다. 한쪽에는 생리학적으로 충실한 in vitro 모델이, 다른 한쪽에는 그 데이터를\n'
     '      서로 비교할 수 있게 만드는 AI 기반 방법이 있습니다.'),
    ('<p class="racc-hint">Select a topic to read more.</p>',
     '<p class="racc-hint">주제를 누르면 자세히 볼 수 있습니다.</p>'),
    # 01
    ('<span class="rcat mono">In vitro models</span>', '<span class="rcat mono">in vitro 모델</span>'),
    ('<h3>Advanced <em>in vitro</em> models</h3>', '<h3>차세대 <em>in vitro</em> 모델</h3>'),
    ('<span class="rlede">Microphysiological systems that reconstruct the human tissue microenvironment.</span>',
     '<span class="rlede">사람 조직의 미세환경을 근사하지 않고 그대로 재구성하는 미세생리시스템.</span>'),
    # 02
    ('<span class="rcat mono">Sensing</span>', '<span class="rcat mono">센싱</span>'),
    ('<h3>Sensor-integrated organoid-on-a-chip</h3>', '<h3>센서 집적 오가노이드 온 칩</h3>'),
    ('<span class="rlede">Biosensors built into the device for continuous, real-time readout.</span>',
     '<span class="rlede">소자 안에 센서를 심어 끊김 없이 실시간으로 계측합니다.</span>'),
    # 03
    ('<span class="rcat mono">Mechanobiology</span>', '<span class="rcat mono">메카노바이올로지</span>'),
    ('<h3>Mechanobiology</h3>', '<h3>메카노바이올로지</h3>'),
    ('<span class="rlede">How mechanical cues &mdash; flow, pressure, matrix stiffness &mdash; shape cell behaviour.</span>',
     '<span class="rlede">유동, 압력, 기질 강성 같은 역학적 신호가 세포 거동을 어떻게 바꾸는지 규명합니다.</span>'),
    # 04
    ('<span class="rcat mono">Data &amp; AI</span>', '<span class="rcat mono">데이터와 AI</span>'),
    ('<h3>Data standardization with AI/ML</h3>', '<h3>AI/ML 기반 데이터 표준화</h3>'),
    ('<span class="rlede">Making organoid and organ-chip data comparable across labs and devices.</span>',
     '<span class="rlede">연구실과 장비가 달라도 오가노이드·오간칩 데이터를 비교할 수 있게 만듭니다.</span>'),
    # figure
    ('data-cap="Reconstructing the tumor microenvironment in a microphysiological system: '
     'human cell sources, a tunable ECM, and controlled vascular, interstitial and lymphatic flow."',
     'data-cap="미세생리시스템에서 종양미세환경을 재구성합니다 — 인체 유래 세포, 조절 가능한 ECM, '
     '그리고 혈관·간질·림프 유동의 제어."'),
    ('alt="Diagram comparing the tumor microenvironment in vivo with a microphysiological system '
     'in vitro, and the three building blocks used to rebuild it: human cell sources, ECM/matrix, '
     'and controlled flow."',
     'alt="생체 내 종양미세환경과 in vitro 미세생리시스템을 비교하고, 이를 재현하는 세 가지 구성요소'
     '(인체 유래 세포, ECM·기질, 제어된 유동)를 보여주는 도식."'),
    ('              Click to enlarge', '              클릭하면 확대됩니다'),
    ('aria-label="Enlarged figure"', 'aria-label="확대한 그림"'),
    ('<button type="button" class="lb-close" id="lbClose" aria-label="Close">',
     '<button type="button" class="lb-close" id="lbClose" aria-label="닫기">'),
]

NEWS = [
    ('<title>News — ABMS Lab</title>', '<title>소식 — ABMS Lab</title>'),
    ('<a href="index-ko.html">Home</a> <span>/</span> <span>News</span>',
     '<a href="index-ko.html">홈</a> <span>/</span> <span>소식</span>'),
    ('<span class="eyebrow mono">News</span>', '<span class="eyebrow mono">소식</span>'),
    ('<h1>Announcements and updates</h1>', '<h1>공지와 소식</h1>'),
    ('<span class="d">September 2025</span>', '<span class="d">2025년 9월</span>'),
    ('<span class="ntag">Lab</span>', '<span class="ntag">연구실</span>'),
    ('<h3>The ABMS Lab opens at Chung-Ang University</h3>',
     '<h3>중앙대학교에 ABMS 연구실이 문을 열었습니다</h3>'),
    ("""            The Advanced Biomicrosystems Laboratory has officially opened in the School of
            Integrative Engineering at Chung-Ang University, led by Prof. Hye-ran Moon.""",
     '            첨단 바이오마이크로시스템 연구실이 중앙대학교 융합공학부에 공식 개소했습니다.\n'
     '            책임교수는 문혜란 교수입니다.'),
]

PER_PAGE = {"index": INDEX, "research": RESEARCH, "news": NEWS}

LANG_KO = ('    <a class="langbtn" href="{target}" hreflang="en" lang="en" '
           'aria-label="Read this page in English">EN</a>\n')
LANG_EN = ('    <a class="langbtn" href="{target}" hreflang="ko" lang="ko" '
           'aria-label="이 페이지를 한국어로 보기">한국어</a>\n')


def add_lang_button(html: str, link: str) -> str:
    """Insert the language toggle just before the nav's closing tag."""
    html = re.sub(r'\n *<a class="langbtn".*?</a>\n', '\n', html, flags=re.S)
    return html.replace('    </ul>\n  </nav>', '    </ul>\n' + link + '  </nav>', 1)


def build_ko(stem: str) -> str:
    src = (ROOT / f"{stem}.html").read_text(encoding="utf-8")

    # point the shared chrome at the Korean pages before translating link text
    for en, ko in KO_PAGES.items():
        src = src.replace(f'href="{en}.html"', f'href="{ko}.html"')
        src = src.replace(f'href="{en}.html#', f'href="{ko}.html#')

    src = src.replace('<html lang="en">', '<html lang="ko">')
    src = src.replace('<link rel="stylesheet" href="abms-styles.css">',
                      NOTO + '\n<link rel="stylesheet" href="abms-styles.css">')

    missing = []
    for en, ko in COMMON + PER_PAGE[stem]:
        if en in src:
            src = src.replace(en, ko)
        elif ko not in src:
            missing.append(en[:72])
    if missing:
        print(f"  ! {stem}: {len(missing)} string(s) not found", file=sys.stderr)
        for m in missing:
            print(f"      {m}", file=sys.stderr)

    return add_lang_button(src, LANG_KO.format(target=f"{stem}.html"))


def main() -> int:
    # Korean pages
    for stem, ko_stem in KO_PAGES.items():
        out = build_ko(stem)
        (ROOT / f"{ko_stem}.html").write_text(out, encoding="utf-8")
        print(f"wrote {ko_stem}.html")

    # English pages get the 한국어 button; pages without a Korean twin point at the Korean home
    for path in sorted(ROOT.glob("*.html")):
        if path.stem.endswith("-ko"):
            continue
        target = f"{KO_PAGES[path.stem]}.html" if path.stem in KO_PAGES else "index-ko.html"
        html = path.read_text(encoding="utf-8")
        new = add_lang_button(html, LANG_EN.format(target=target))
        if new != html:
            path.write_text(new, encoding="utf-8")
            print(f"updated {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
