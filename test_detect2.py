#!/usr/bin/env python3

import sys
sys.path.insert(0, r'c:\Users\naren\Sovereign')

import run_ingestion as r

# Read the raw PDF text (space-separated)
text = open(r'c:\Users\naren\Sovereign\workspace\the-psychology-of-money-by-morgan-housel 05\00_raw_text.txt', 'r', encoding='utf-8').read()

print(f"Original file size: {len(text)} chars")

# Let me check the actual first 200 lines to see if corruption detection works
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

print(f"Single-char words: {single_char_word_count} / {total_word_count} = {100*single_char_word_count/total_word_count if total_word_count else 0:.1f}%")

if total_word_count > 0 and single_char_word_count / total_word_count > 0.7:
    print("Corruption detected! Triggering cleaning...")
else:
    print("No corruption detected")
