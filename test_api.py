import urllib.request, json

tests = [
    ('hello', 'Hello test'),
    ('what time is it', 'Time test'),
    ('tell me a joke', 'Joke test'),
    ('what is today date', 'Date test'),
]

print("\n=== JARVIS API TEST ===\n")
for query, label in tests:
    data = json.dumps({'query': query}).encode()
    req = urllib.request.Request(
        'http://localhost:8000/api/command',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        r = urllib.request.urlopen(req, timeout=8)
        result = json.loads(r.read().decode())
        resp = result.get('response', '')
        ok   = result.get('ok', False)
        print(f"[{'OK' if ok else 'FAIL'}] {label}: {resp[:70]}")
    except Exception as e:
        print(f"[ERR] {label}: {e}")

print("\n=== DONE ===")
