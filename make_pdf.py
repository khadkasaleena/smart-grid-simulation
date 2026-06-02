"""
make_pdf.py
Two-pass PDF export of the report with a real, page-numbered Table of Contents.

Pass 1: build the .docx (live TOC field) and convert to PDF, then read back the
        page number of every heading with PyMuPDF.
Pass 2: rebuild the .docx with a static, page-numbered TOC and convert to the
        final PDF.

Run:  python make_pdf.py
Output: StudentID_Salina_Khadka_Assignment.pdf
"""

import os
import subprocess
import sys

import fitz  # PyMuPDF
from docx import Document

import build_report

HERE = os.path.dirname(os.path.abspath(__file__))
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


def docx_to_pdf(docx_path):
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf",
                    "--outdir", HERE, docx_path],
                   check=True, capture_output=True)
    return os.path.splitext(docx_path)[0] + ".pdf"


def heading_entries(docx_path):
    """Return [(text, level)] for Heading 1/2, excluding the TOC heading."""
    doc = Document(docx_path)
    entries = []
    for p in doc.paragraphs:
        s = p.style.name
        if s == "Heading 1" and p.text.strip() != "Table of Contents":
            entries.append((p.text.strip(), 1))
        elif s == "Heading 2":
            entries.append((p.text.strip(), 2))
    return entries


def find_pages(pdf_path, entries):
    """For each heading, return its first 1-based page number in the PDF.

    Headings appear in document order, so we only search from the previous
    heading's page onward. This avoids false matches when a filename string
    (e.g. 'scenarios.py') is mentioned inside an earlier file's code.
    """
    doc = fitz.open(pdf_path)
    result = []
    start = 0
    for text, level in entries:
        page_no = None
        for i in range(start, len(doc)):
            if doc[i].search_for(text, quads=False):
                page_no = i + 1
                start = i  # next heading is at or after this page
                break
        result.append((text, level, page_no if page_no else start + 1))
    doc.close()
    return result


def main():
    # --- Pass 1: field-TOC docx -> pdf, then read heading pages -----------
    field_docx = build_report.main(out_name="_report_pass1.docx")
    pass1_pdf = docx_to_pdf(field_docx)
    entries = heading_entries(field_docx)
    toc = find_pages(pass1_pdf, entries)
    print("Heading page map:")
    for t, lvl, pg in toc:
        print(f"  [{lvl}] p.{pg}  {t}")

    # --- Pass 2: static-TOC docx -> final pdf -----------------------------
    static_docx = build_report.main(static_toc=toc, out_name="_report_pass2.docx")
    final_pdf = docx_to_pdf(static_docx)

    target = os.path.join(HERE, "StudentID_Salina_Khadka_Assignment.pdf")
    os.replace(final_pdf, target)

    # Clean up intermediates.
    for f in ["_report_pass1.docx", "_report_pass1.pdf", "_report_pass2.docx"]:
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            os.remove(p)

    print("\nSaved:", target)


if __name__ == "__main__":
    main()
