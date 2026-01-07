import sys
sys.path.insert(0, '.')
import run_ingestion as r

text = open('workspace/the-psychology-of-money-by-morgan-housel 05/00_raw_text.txt','r',encoding='utf-8').read()

# Test the cleaning with detailed output
print("Testing clean_extracted_text function:")
print(f"Input: {len(text)} chars")
print(f"First 100 input: {repr(text[:100])}")

# Run the detection logic
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
print(f"Corruption detected: {corruption_ratio:.2%} > 50% = {corruption_ratio > 0.5}")

# Now call the function
cleaned = r.clean_extracted_text(text)
print(f"\nOutput: {len(cleaned)} chars")
print(f"First 100 output: {repr(cleaned[:100])}")
print(f"First 200 output:\n{cleaned[:200]}")
