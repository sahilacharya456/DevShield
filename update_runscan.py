import os
import re

frontend_file = r'c:\Users\sahil\Desktop\DevShield\frontend\src\app\arsenal\page.tsx'

with open(frontend_file, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''      } else {
        addLine(`[INFO] Opening WebSocket stream for ${selectedTool.name}...`, "info");
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        const wsHost = new URL(API_URL).host;
        const wsUrl = `${wsProto}://${wsHost}/api/v1/arsenal/${selectedTool.id}/stream`;
        const ws = new WebSocket(wsUrl);
        ws.onopen = () => ws.send(JSON.stringify({ target, scan_type: scanType }));
        ws.onmessage = (evt) => {
          const msg = JSON.parse(evt.data);
          addLine(msg.line, msg.type || "info");
          if (msg.type === "complete") { setIsScanning(false); ws.close(); }
        };
        ws.onerror = () => { addLine("[ERROR] WebSocket failed. Check backend connection.", "error"); setIsScanning(false); };
        ws.onclose = () => setIsScanning(false);
        return;
      }'''

# Replace the else block for Nmap
old_else_block = '''      } else {
        addLine(`[INFO] Opening WebSocket stream for Nmap...`, "info");
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        const wsHost = new URL(API_URL).host;
        const wsUrl = `${wsProto}://${wsHost}/api/v1/arsenal/nmap/stream`;
        const ws = new WebSocket(wsUrl);
        ws.onopen = () => ws.send(JSON.stringify({ target, scan_type: scanType }));
        ws.onmessage = (evt) => {
          const msg = JSON.parse(evt.data);
          addLine(msg.line, msg.type || "info");
          if (msg.type === "complete") { setIsScanning(false); ws.close(); }
        };
        ws.onerror = () => { addLine("[ERROR] WebSocket failed. Check backend connection.", "error"); setIsScanning(false); };
        ws.onclose = () => setIsScanning(false);
        return;
      }'''

# Since using string replacement might be fragile due to exact whitespace, let's use regex
content = re.sub(r'\} else \{\s*addLine\(`\[INFO\] Opening WebSocket stream for Nmap[^}]+return;\s*\}', replacement, content, flags=re.MULTILINE)

with open(frontend_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated runScan in frontend.")
