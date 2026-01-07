import sys
import re
sys.path.insert(0, '.')
import run_ingestion as r

text = open('workspace/the-psychology-of-money-by-morgan-housel 05/00_raw_text.txt','r',encoding='utf-8').read()
print(f"Original: {len(text)} chars")
print(f"First 100: {repr(text[:100])}")

cleaned = r.clean_extracted_text(text)
print(f"\nCleaned: {len(cleaned)} chars")
print(f"First 100: {repr(cleaned[:100])}")
print(f"First 200: {cleaned[:200]}")

# Check if it worked
print(f"\nChange in size: {len(text)} -> {len(cleaned)} ({100*(1 - len(cleaned)/len(text)):.1f}% reduction)")
