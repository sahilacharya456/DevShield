import urllib.request
import json

try:
    req = urllib.request.Request(
        'http://localhost:8000/api/v1/soc/chat', 
        data=b'{"message": "hello"}', 
        headers={'Content-Type': 'application/json'}, 
        method='POST'
    )
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except Exception as e:
    print(e.read().decode())
