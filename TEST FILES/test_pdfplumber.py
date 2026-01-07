#!/usr/bin/env python3

import pdfplumber

pdf_path = r'c:\Users\naren\Sovereign\books\the-psychology-of-money-by-morgan-housel 05.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ""
    for page in pdf.pages[:3]:  # Just first 3 pages for testing
        text += page.extract_text()
        text += "\n"

print(f"Extracted: {len(text)} chars")
print(f"First 500 chars:\n{text[:500]}\n")

# Check for spacing issues
lines = text.split('\n')[:5]
for i, line in enumerate(lines):
    print(f"Line {i}: {repr(line[:100])}")
