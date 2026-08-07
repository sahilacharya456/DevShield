import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect('ws://127.0.0.1:8000/api/v1/arsenal/nmap/stream') as ws:
            await ws.send(json.dumps({"target": "127.0.0.1", "scan_type": "quick"}))
            res = await ws.recv()
            print("Received:", res)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
