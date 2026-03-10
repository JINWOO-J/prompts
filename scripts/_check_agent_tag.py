import json, urllib.request

res = urllib.request.urlopen('http://localhost:8000/api/prompts?page_size=10000')
data = json.loads(res.read())
prompts = data.get('prompts', [])
count = sum(1 for p in prompts if 'agent' in p.get('tags', []))
print(f"agent 태그 프롬프트: {count}개 / 전체: {data.get('total', len(prompts))}개")
