import sys
sys.path.insert(0, '.')
import run_ingestion as r

text = open('cold_strategist/workspace/the-psychology-of-money-by-morgan-housel 05/00_raw_text.txt','r',encoding='utf-8').read()
print(f"Original length: {len(text)}")
print(f"Original first 100 chars: {repr(text[:100])}")

cleaned = r.clean_extracted_text(text)
print(f"Cleaned length: {len(cleaned)}")
print(f"Cleaned first 100 chars: {repr(cleaned[:100])}")
print(f"Cleaned first 200 chars: {cleaned[:200]}")

# Check if it changed
if len(text) == len(cleaned):
    print("WARNING: Text did not change!")
else:
    print(f"Text was cleaned ({len(text)} -> {len(cleaned)})")
