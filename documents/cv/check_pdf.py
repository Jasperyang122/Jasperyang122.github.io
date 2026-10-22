"""Check source coverage, links, author marks, fonts and page bounds."""
from pathlib import Path
import json
import re
import unicodedata

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('cv.md')
PDF = ROOT / 'public/cv/Jielun-Yang-CV-2026-10-22-ranked.pdf'


def plain(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text.replace('\\*', '').replace('*', '')


def normalized(text):
    text = unicodedata.normalize('NFKC', plain(text)).replace('–', '-').replace('—', '-')
    return re.sub(r'\s+', '', text)


reader = PdfReader(PDF)
with pdfplumber.open(PDF) as document:
    texts = [p.extract_text() for p in document.pages]
    all_text = '\n'.join(texts)
    date_text = '\n'.join(p.crop((73, 65, 154, 788)).extract_text() or ''
                           for p in document.pages)
    for page in document.pages:
        assert len(page.extract_text().strip()) > 100
        body_chars = [c for c in page.chars if 65 < c['top'] < 788]
        assert min(c['x0'] for c in body_chars) >= 73 - 0.2
        assert max(c['x1'] for c in body_chars) <= 555.32 + 0.2
        assert max(c['bottom'] for c in body_chars) < 788
    assert '\ufffd' not in all_text
    assert 'Germà Bel' in all_text
    assert sum(c['text'] == '*' for p in document.pages for c in p.chars) == 6
    bold_chars = ''.join(c['text'] for p in document.pages for c in p.chars
                         if 'TimesNewRomanPS-BoldMT' in c['fontname'])
    assert normalized(bold_chars).count('JielunYang') == 5
    # The material was typeset rather than rasterized: all body text uses the
    # exact 12-point Times New Roman family observed in the supplied reference.
    normal = [c for p in document.pages for c in p.chars
              if 'TimesNewRomanPSMT' in c['fontname'] and 65 < c['top'] < 788]
    assert normal and all(round(c['size'], 2) in (10, 12) for c in normal)
    assert sum(abs(c['size'] - 12) < 0.01 for c in normal) > 1000
    assert all('TimesNewRoman' in c['fontname'] for p in document.pages for c in p.chars)
    words = document.pages[0].extract_words()
    expected_date = next(w for w in words if '09/2027' in w['text'])
    hosted = next(w for w in words if w['text'] == 'hosted')
    host_name = next(w for w in words if w['text'] == 'Germà')
    assert abs(hosted['top'] - expected_date['top'] - 13.8) < 0.2
    assert abs(host_name['top'] - hosted['top']) < 0.2
    joint_words = document.pages[0].extract_words(extra_attrs=['fontname'])
    for word in joint_words:
        if word['text'] in ('Joint', 'doctoral', 'training:'):
            assert 'TimesNewRomanPSMT' in word['fontname']
    assert 'Research Interests' in all_text
    assert all_text.index('Education') < all_text.index('Research Interests') < all_text.index('Publications and Manuscripts')
    assert '72474181' in all_text
    assert 'Shaanxi Province' in all_text
    assert 'Participate in the National Natural Science Foundation' not in all_text
    assert 'Collected and organized platform enforcement' not in all_text
    assert 'Undergraduate Innovation' not in all_text
    assert 'Research Assistant (05/2025 - Present)' in all_text
    assert 'Research Assistant (02/2025 - 06/2025)' in all_text

source = SOURCE.read_text(encoding='utf-8')
checked = 0
for line in source.splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if line.startswith('- '):
        line = line[2:]
    if re.match(r'^\*\*.+, \d{2}/\d{4}', line):
        clean = plain(line)
        if clean.startswith('Research Assistant, '):
            chunks = clean.rsplit(', ', 2)
        else:
            chunks = clean.rsplit(', ', 1)
    else:
        chunks = [plain(line)]
    for chunk in chunks:
        assert normalized(chunk) in normalized(all_text + '\n' + date_text), chunk
        checked += 1

links = {annotation.get_object().get('/A', {}).get('/URI')
         for page in reader.pages for annotation in page.get('/Annots', [])}
expected = set(re.findall(r'\[[^\]]+\]\(([^)]+)\)', source))
assert expected <= links
assert 'mailto:yjl02122@163.com' in links
assert 'https://orcid.org/0009-0002-2563-597X' in links
assert not any(url and 'doi.org' in url for url in links)
assert 'https://web.ub.edu/en/' not in links
assert 'https://www.ub.edu/school-economics/researcher/bel-germa/' not in links
assert 'DOI' not in all_text
assert '[SSCI, JCR Q1]' in all_text
assert '[SCIE, JCR Q1]' in all_text
assert 'ABS' not in all_text
assert all_text.index('From Digital Rural Development') < all_text.index('Coupling Coordination')
assert 'Under review at Systems' not in all_text
assert 'GPA' not in all_text and 'Selected coursework' not in all_text
assert 'Wong' not in all_text and 'Mathew' not in all_text
print(json.dumps({'pages': len(reader.pages), 'source_checks': checked,
                  'bold_author_names': 5, 'correspondence_markers': 6,
                  'distinct_clickable_urls': len(links),
                  'pdf_bytes': PDF.stat().st_size}, indent=2))
