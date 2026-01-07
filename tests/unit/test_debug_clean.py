def clean_extracted_text_debug(text: str) -> str:
    """Debug version of the cleaning function."""
    if not text:
        return text
    
    # Check if text has corruption
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
    
    print(f"[DEBUG] corruption_ratio = {corruption_ratio:.2%}, threshold = 0.5, trigger = {corruption_ratio > 0.5}")
    
    if corruption_ratio > 0.5:
        print(f"[DEBUG] Cleaning triggered!")
        cleaned = ' '.join(text.split())
        print(f"[DEBUG] After join: length = {len(cleaned)}, first 100 = {repr(cleaned[:100])}")
        
        result = []
        chars_in_line = 0
        words = cleaned.split(' ')
        print(f"[DEBUG] Split into {len(words)} words")
        
        for i, word in enumerate(words):
            if chars_in_line + len(word) + 1 > 300:
                result.append('\n')
                chars_in_line = 0
            result.append(word)
            result.append(' ')
            chars_in_line += len(word) + 1
            
            if i < 5:
                print(f"[DEBUG] Word {i}: '{word}' ({len(word)} chars)")
        
        final = ''.join(result)
        print(f"[DEBUG] Final length: {len(final)}, first 100 = {repr(final[:100])}")
        return final
    
    print(f"[DEBUG] No cleaning needed")
    return text

# Test it
text = open('cold_strategist/workspace/the-psychology-of-money-by-morgan-housel 05/00_raw_text.txt','r',encoding='utf-8').read()
cleaned = clean_extracted_text_debug(text)
print(f"\nFinal output length: {len(cleaned)}")
print(f"Final first 100: {repr(cleaned[:100])}")
