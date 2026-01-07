import json

data = json.load(open(r'c:\Users\naren\Sovereign\workspace\the-psychology-of-money-by-morgan-housel 05\02_principles.json', encoding='utf-8'))
print(f'Chapters extracted: {len(data["chapters"])}')
print()
for ch in data['chapters']:
    title = ch.get('chapter_title') or '(no title)'
    domains = ', '.join(ch.get('domains', []))[:40]
    print(f"Ch {ch['chapter_index']:2d}: {title[:50]:50s} | Domains: {domains}")
