path = r"c:\Users\user\AI-webagent_extractor\darwin_scraper_complete.py"
s = open(path, 'r', encoding='utf-8').read()
print('triple_count=', s.count('"""'))
idxs = [i for i in range(len(s)) if s.startswith('"""', i)]
print('first_three_idx=', idxs[0] if idxs else -1)
if idxs:
    i = idxs[0]
    print('\ncontext around first triple-quote:\n')
    print(s[max(0,i-120):i+120])
