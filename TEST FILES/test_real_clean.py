#!/usr/bin/env python3

import sys
sys.path.insert(0, r'c:\Users\naren\Sovereign')

from cold_strategist.ingest.core.pdf_reader import extract_text
import run_ingestion as r

# Extract directly from PDF
text = extract_text(r'c:\Users\naren\Sovereign\books\the-psychology-of-money-by-morgan-housel 05.pdf')

print(f"Original extracted: {len(text)} chars")
print(f"First 150: {repr(text[:150])}")
print()

# Test detection
lines = text.split('\n')[:100]

single_char_word_count = 0
total_word_count = 0

for line in lines:
    if len(line) < 10:
        continue
    
    words = [w for w in line.split(' ') if w]
    if not words:
        continue
    
    total_word_count += len(words)
    single_char_word_count += sum(1 for w in words if len(w) == 1)

corruption_ratio = single_char_word_count / total_word_count if total_word_count > 0 else 0
print(f"Corruption detection: {single_char_word_count}/{total_word_count} = {100*corruption_ratio:.1f}%")
print()

# Now clean it
cleaned = r.clean_extracted_text(text)

print(f"After cleaning: {len(cleaned)} chars ({100*(1-len(cleaned)/len(text)):.1f}% reduction)")
print(f"First 200: {repr(cleaned[:200])}")
print()
print("Sample text (first 500 chars):")
print(cleaned[:500])
