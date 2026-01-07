text = open('cold_strategist/workspace/the-psychology-of-money-by-morgan-housel 05/00_raw_text.txt','r',encoding='utf-8').read()

# Debug the detection step by step
lines = text.split('\n')[:100]
print(f"Number of lines in first 100: {len(lines)}")

# Count lines with the corruption pattern
corrupted_lines = 0

for i, line in enumerate(lines):
    if len(line) < 10:
        if i < 5:
            print(f"Line {i}: too short ({len(line)})")
        continue
    
    # Split by space to get "words"
    words = [w for w in line.split(' ') if w]
    
    if not words:
        print(f"Line {i}: no words")
        continue
    
    # If most "words" are single characters, this is corrupted
    single_char_words = sum(1 for w in words if len(w) == 1)
    ratio = single_char_words / len(words) if words else 0
    
    if i < 5:
        print(f"Line {i}: {len(words)} words, {single_char_words} single-char, ratio={ratio:.2%}")
    
    if ratio > 0.7:
        corrupted_lines += 1

corruption_ratio = corrupted_lines / len(lines) if lines else 0
print(f"\nTotal corrupted lines: {corrupted_lines} / {len(lines)} = {corruption_ratio:.2%}")
print(f"Threshold: > 0.5 = {corruption_ratio > 0.5}")
