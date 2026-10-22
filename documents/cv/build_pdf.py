"""Build the English CV in the academic layout supplied in WONGMYH-CV.pdf.

Content comes only from cv.md and the site's identity/contact configuration.
The reference controls typography and layout, not biographical claims.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import argparse
import datetime
import re
import tomllib

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
PAGE_W, PAGE_H = 595.32, 841.92
LEFT, RIGHT, TOP, BOTTOM = 73.1, 40.0, 72.0, 54.0
WIDTH = PAGE_W - LEFT - RIGHT
LINK_COLOR = '#0000FF'


def make_styles():
    body = ParagraphStyle('Body', fontName='CVTimes', fontSize=12, leading=13.8,
                          alignment=TA_LEFT, spaceAfter=13.8,
                          allowWidows=0, allowOrphans=0)
    return {
        'body': body,
        'title': ParagraphStyle('Title', parent=body, fontName='CVTimesBold',
                                fontSize=16, leading=19.2, alignment=TA_CENTER,
                                spaceAfter=16, keepWithNext=True),
        'contact': ParagraphStyle('Contact', parent=body, spaceAfter=0),
        'section': ParagraphStyle('Section', parent=body, fontName='CVTimesBold',
                                  fontSize=14, leading=16.8, spaceBefore=20,
                                  spaceAfter=14, keepWithNext=True),
        'subsection': ParagraphStyle('Subsection', parent=body,
                                     fontName='CVTimesBoldItalic',
                                     spaceBefore=13.8, spaceAfter=10,
                                     keepWithNext=True),
        'degree': ParagraphStyle('Degree', parent=body, spaceAfter=0),
        'date': ParagraphStyle('Date', parent=body, spaceAfter=0),
        'citation': ParagraphStyle('Citation', parent=body, leftIndent=42,
                                   firstLineIndent=-42, spaceAfter=13.8),
        'role': ParagraphStyle('Role', parent=body, fontName='CVTimesBoldItalic',
                               spaceAfter=0, keepWithNext=True),
        'institution': ParagraphStyle('Institution', parent=body, spaceAfter=6,
                                      keepWithNext=True),
        'summary': ParagraphStyle('Summary', parent=body, spaceAfter=0),
        'bullet': ParagraphStyle('Bullet', parent=body, leftIndent=14,
                                 bulletIndent=0, bulletFontName='CVTimes',
                                 bulletFontSize=12, spaceAfter=4),
        'skill': ParagraphStyle('Skill', parent=body, spaceAfter=6),
        'note': ParagraphStyle('Note', parent=body, fontSize=10, leading=12,
                               spaceBefore=0, spaceAfter=0),
    }


TOKEN = re.compile(r'\\\*|\*\*(.+?)\*\*|\*([^*]+)\*|\[([^\]]+)\]\(([^)]+)\)')


def inline(text):
    result, pos = [], 0
    for match in TOKEN.finditer(text):
        result.append(escape(text[pos:match.start()].replace('–', '-').replace('—', '-')))
        if match.group(0) == r'\*':
            result.append('*')
        elif match.group(1) is not None:
            result.append('<b>' + inline(match.group(1)) + '</b>')
        elif match.group(2) is not None:
            result.append('<i>' + inline(match.group(2)) + '</i>')
        else:
            result.append('<link href="' + escape(match.group(4), {'"': '&quot;'})
                          + '" color="' + LINK_COLOR + '"><u>'
                          + inline(match.group(3)) + '</u></link>')
        pos = match.end()
    result.append(escape(text[pos:].replace('–', '-').replace('—', '-')))
    return ''.join(result)


def entries(text):
    return [re.sub(r'\s*\n\s*', ' ', part).strip()
            for part in re.split(r'(?m)^- ', text)[1:]]


def read_sections(path):
    sections = {}
    for part in re.split(r'(?m)^## ', path.read_text(encoding='utf-8'))[1:]:
        title, content = part.split('\n', 1)
        sections[title.strip()] = content.strip()
    return sections


def build(output, updated, font_dir):
    for name, filename in [
        ('CVTimes', 'times.ttf'), ('CVTimesBold', 'timesbd.ttf'),
        ('CVTimesItalic', 'timesi.ttf'), ('CVTimesBoldItalic', 'timesbi.ttf'),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily('CVTimes', normal='CVTimes', bold='CVTimesBold',
                                  italic='CVTimesItalic', boldItalic='CVTimesBoldItalic')
    styles = make_styles()
    sections = read_sections(Path(__file__).with_name('cv.md'))
    config = tomllib.loads((ROOT / 'content/config.toml').read_text(encoding='utf-8'))
    name = config['author']['name']
    email = config['social']['email']
    site_url = 'https://jasperyang122.github.io/'
    orcid = re.search(r'\d{4}-\d{4}-\d{4}-[\dX]{4}', config['social']['orcid']).group(0)

    def para(text, style='body'):
        return Paragraph(inline(text), styles[style])

    def chrome(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.black)
        canvas.setFont('CVTimes', 10)
        if doc.page > 1:
            canvas.drawString(45, PAGE_H - 50, name)
        canvas.drawCentredString(PAGE_W / 2, 23, str(doc.page))
        canvas.drawRightString(PAGE_W - RIGHT, 23,
                               'Last updated: ' + updated.strftime('%B %d, %Y').replace(' 0', ' '))
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(output), pagesize=(PAGE_W, PAGE_H),
                          leftMargin=LEFT, rightMargin=RIGHT,
                          topMargin=TOP, bottomMargin=BOTTOM,
                          title='Jielun Yang Curriculum Vitae', author='Jielun Yang')
    frame = Frame(LEFT, BOTTOM, WIDTH, PAGE_H - TOP - BOTTOM,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                  id='body')
    doc.addPageTemplates(PageTemplate(id='Academic', frames=[frame], onPage=chrome))
    story = [para('Jielun (Jasper) YANG', 'title')]

    # Explicit breaks are limited to this identity block; source content is
    # wrapped by the layout engine throughout the CV.
    contact_left = Paragraph('Ph.D. Student<br/>School of Management<br/>'
                             'Harbin Institute of Technology<br/>Harbin, China', styles['contact'])
    contact_right = Table([
        [para('E-mail:', 'contact'), para(f'[{email}](mailto:{email})', 'contact')],
        [para('ORCID:', 'contact'), para(f'[{orcid}](https://orcid.org/{orcid})', 'contact')],
        [para('Website:', 'contact'), para(f'[jasperyang122.github.io]({site_url})', 'contact')],
    ], colWidths=[54, WIDTH - 215 - 54])
    zero_padding = TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0),
                               ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                               ('TOPPADDING', (0, 0), (-1, -1), 0),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP')])
    contact_right.setStyle(zero_padding)
    contact = Table([[contact_left, contact_right]], colWidths=[215, WIDTH - 215])
    contact.setStyle(zero_padding)
    story.extend([contact, Spacer(1, 6), para('Education', 'section')])

    for record in re.split(r'(?m)^### ', sections['Education'])[1:]:
        institution, content = record.split('\n', 1)
        degree, dates = re.search(r'\*\*(.+), (\d{2}/\d{4}.+?)\*\*', content).groups()
        start, end = re.split(r'\s+[–-]\s+', dates)
        date_p = Paragraph(escape(start) + ' -<br/>' + escape(end), styles['date'])
        right = [para(degree, 'degree'), para(institution.strip(), 'degree')]
        for item in entries(content):
            if item.startswith('Joint doctoral training:') and ', hosted by ' in item:
                training, host = item.split(', hosted by ', 1)
                right.append(Paragraph(inline(training + ',') + '<br/>'
                                       + inline('hosted by ' + host), styles['degree']))
            else:
                right.append(para(item, 'degree'))
        table = Table([[date_p, right]], colWidths=[81, WIDTH - 81])
        table.setStyle(zero_padding)
        story.append(KeepTogether([table, Spacer(1, 13.8)]))

    story.append(para('Research Interests', 'section'))
    interests = entries(sections['Research Interests'])
    story.append(Paragraph('<br/>'.join(inline(item) for item in interests), styles['body']))
    story.append(para('Publications and Manuscripts', 'section'))
    for group in re.split(r'(?m)^### ', sections['Publications and Manuscripts'])[1:]:
        title, content = group.split('\n', 1)
        content = content.split(r'\* Corresponding author.')[0]
        block = [para(title.strip(), 'subsection')]
        block.extend(para(item, 'citation') for item in entries(content))
        story.append(KeepTogether(block))
    story.append(para(r'\* Corresponding author.', 'note'))

    story.append(para('Research Experience', 'section'))
    records = re.split(r'(?m)^### ', sections['Research Experience'])[1:]
    for index, record in enumerate(records):
        institution, content = record.split('\n', 1)
        role, unit, dates = re.search(r'\*\*(Research Assistant), (.+), (\d{2}/\d{4}.+?)\*\*', content).groups()
        block = []
        if index:
            block.append(Spacer(1, 13.8))
        block.extend([para(f'{role} ({dates})', 'role'),
                       para(f'{unit}, {institution.strip()}', 'institution')])
        block.extend(para(item, 'summary') for item in entries(content))
        story.append(KeepTogether(block))

    story.append(para('Research Methods and Skills', 'section'))
    for item in entries(sections['Research Methods and Skills']):
        story.append(para(item, 'skill'))
    doc.build(story)
    print('Created:', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--updated', default='2026-10-22')
    parser.add_argument('--font-dir', type=Path, default=Path('C:/Windows/Fonts'))
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'public/cv/Jielun-Yang-CV-2026-10-22-ranked.pdf')
    args = parser.parse_args()
    build(args.output, datetime.date.fromisoformat(args.updated), args.font_dir)
