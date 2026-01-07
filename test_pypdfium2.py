#!/usr/bin/env python3

import pypdfium2 as pdfium

pdf_path = r'c:\Users\naren\Sovereign\books\the-psychology-of-money-by-morgan-housel 05.pdf'

pdf = pdfium.open(pdf_path)

# Check page count first
print(f"PDF has {len(pdf)} pages")

# Try to extract text from first 3 pages
text = ""
for page_idx in range(min(3, len(pdf))):
    page = pdf[page_idx]
    textpage = page.get_textpage()
    page_text = textpage.get_text()
    text += page_text
    print(f"Page {page_idx}: {len(page_text)} chars")

print(f"\nTotal extracted: {len(text)} chars")
print(f"First 500 chars:\n{text[:500]}\n")

# Check for spacing issues
lines = text.split('\n')[:5]
for i, line in enumerate(lines):
    print(f"Line {i}: {repr(line[:100])}")
