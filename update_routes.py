import os

routes_file = r'c:\Users\sahil\Desktop\DevShield\backend\api\routes_arsenal.py'

append_content = '''
# --- Added by God Mode ---

@router.websocket("/dnsrecon/stream")
async def dnsrecon_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.dnsrecon_wrapper import dnsrecon_scanner
        async for line in dnsrecon_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] DNSRecon finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/gobuster/stream")
async def gobuster_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.gobuster_wrapper import gobuster_scanner
        async for line in gobuster_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Gobuster finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/harvester/stream")
async def harvester_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.harvester_wrapper import harvester_scanner
        async for line in harvester_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Harvester finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/hydra/stream")
async def hydra_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.hydra_wrapper import hydra_scanner
        async for line in hydra_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Hydra finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/nikto/stream")
async def nikto_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.nikto_wrapper import nikto_scanner
        async for line in nikto_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Nikto finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/shodan/stream")
async def shodan_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.shodan_wrapper import shodan_scanner
        async for line in shodan_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Shodan finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/sublister/stream")
async def sublister_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.sublister_wrapper import sublister_scanner
        async for line in sublister_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Sublister finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/whatweb/stream")
async def whatweb_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.whatweb_wrapper import whatweb_scanner
        async for line in whatweb_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] WhatWeb finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/zap/stream")
async def zap_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.zap_wrapper import zap_scanner
        async for line in zap_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] ZAP finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/hash/stream")
async def hash_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.hash_analyzer import hash_analyzer
        async for line in hash_analyzer.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Hash analysis finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")
'''

with open(routes_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert before Private helpers if possible
if '# ---------------------------------------------------------------------------' in content and '# Private helpers' in content:
    idx = content.rfind('# ---------------------------------------------------------------------------')
    content = content[:idx] + append_content + '\\n' + content[idx:]
else:
    content += append_content

with open(routes_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('Routes updated')
