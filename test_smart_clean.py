#!/usr/bin/env python3

import sys
sys.path.insert(0, r'c:\Users\naren\Sovereign')

import run_ingestion as r

# Read the raw text
text = open(r'c:\Users\naren\Sovereign\workspace\the-psychology-of-money-by-morgan-housel 05\00_raw_text.txt', 'r', encoding='utf-8').read()

print(f"Original: {len(text)} chars")
print(f"First 100: '{text[:100]}'")
print()

cleaned = r.clean_extracted_text(text)

print(f"Cleaned: {len(cleaned)} chars ({100*(1-len(cleaned)/len(text)):.1f}% reduction)")
print(f"First 100: '{cleaned[:100]}'")
print(f"First 200: {cleaned[:200]}")
print()

# Show a longer sample
sample = cleaned[0:500]
print("Sample (500 chars):")
print(sample)
