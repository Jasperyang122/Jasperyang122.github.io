# English CV

The current PDF is generated from `cv.md` by `build_pdf.py`. Edit this Markdown
file to update the CV. Research interests follow education; research experience
gives roles, institutions, dates and brief research summaries.

The layout follows the user-provided WONGMYH-CV.pdf reference: A4 pages,
centered Times New Roman bold name, two-column contact block, 12-point Times New Roman
body text, 14-point mixed-case section headings, date column for education,
hanging citations, and running name and update-date furniture. It has no fixed
page count and does not import biographical claims from the reference. All text
uses the Times New Roman family. The joint doctoral training host starts on a
new line after the expected date.

Update the Markdown first, then use the bundled Python runtime with ReportLab:

```powershell
& 'C:\Users\Jasper\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' documents/cv/build_pdf.py --updated 2026-10-22
```

Render every PDF page and inspect typography, wrapping, section spacing and page
breaks. Check that the citations, correspondence markers and contact links remain
correct. Published citations carry verified indexing and JCR quartile labels,
not DOI links. The joint doctoral training label is regular weight; its
university and host are plain text. Ranking evidence and the verification date
are recorded in `journal_rankings.json`. Do not infer a ranking for a paper
from the journal to which it has been submitted.

Update `content/cv.md` to point to the verified PDF. Publication
still requires the user's instruction to publish.

The DOCX in this directory is the earlier Word-template draft, not the source
of the current reference-based PDF. Earlier PDFs are drafts and should not be
staged for website publication.
