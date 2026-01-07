import re

text = open('cold_strategist/workspace/the-psychology-of-money-by-morgan-housel 05/00_raw_text.txt','r',encoding='utf-8').read()

# Test the detection
lines = text.split('\n')[:100]
corrupted_lines = 0

for line in lines:
    if len(line) < 10:
        continue
    
    words = [w for w in line.split(' ') if w]
    
    if not words:
        continue
    
    single_char_words = sum(1 for w in words if len(w) == 1)
    ratio = single_char_words / len(words) if words else 0
    
    if ratio > 0.7:
        corrupted_lines += 1

corruption_ratio = corrupted_lines / len(lines) if lines else 0

print(f"Corruption ratio: {corruption_ratio:.2%}")
print(f"Corrupted lines: {corrupted_lines} / {len(lines)}")

# Show first line stats
if lines and lines[0]:
    words = [w for w in lines[0].split(' ') if w]
    single_char = sum(1 for w in words if len(w) == 1)
    print(f"First line: {len(words)} words, {single_char} single-char ({100*single_char/len(words):.1f}%)")
    print(f"Sample: {lines[0][:100]}")
