import json

data = json.load(open(r'c:\Users\naren\Sovereign\workspace\the-psychology-of-money-by-morgan-housel 05\01_chapters.json', encoding='utf-8'))
ch10 = data['chapters'][9]
print(f'Chapter 10 text length: {len(ch10["chapter_text"])}')
print('First 500 chars:')
print(repr(ch10['chapter_text'][:500]))
print('\nActual text:')
print(ch10['chapter_text'][:500])
