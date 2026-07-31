import os

base_dir = "c:/Users/sahil/Desktop/DevShield"

modules = [
    {
        "name": "phantom",
        "title": "PhantomScan",
        "desc": "Sandboxed malware execution & dynamic analysis",
        "engine_path": "backend/engine/sandbox/phantom_executor.py",
        "route_path": "backend/api/routes_phantom.py",
        "page_path": "frontend/src/app/phantom/page.tsx"
    },
    {
        "name": "supplychain",
        "title": "ChainBreaker",
        "desc": "Deep dependency tree vulnerability mapping",
        "engine_path": "backend/engine/supplychain/chain_breaker.py",
        "route_path": "backend/api/routes_supplychain.py",
        "page_path": "frontend/src/app/supply-chain/page.tsx"
    },
    {
        "name": "osint",
        "title": "OsintRadar",
        "desc": "Global attack surface mapping & dark web intel",
        "engine_path": "backend/engine/osint/attack_surface_mapper.py",
        "route_path": "backend/api/routes_osint.py",
        "page_path": "frontend/src/app/osint/page.tsx"
    },
    {
        "name": "deobfuscator",
        "title": "MalwareForge",
        "desc": "Neural AST-based code deobfuscation",
        "engine_path": "backend/engine/deobfuscator/neural_deobfuscator.py",
        "route_path": "backend/api/routes_deobfuscator.py",
        "page_path": "frontend/src/app/deobfuscator/page.tsx"
    },
    {
        "name": "redteam",
        "title": "RedAgent",
        "desc": "Autonomous Red Team AI orchestrator",
        "engine_path": "backend/engine/redteam/red_agent.py",
        "route_path": "backend/api/routes_redteam.py",
        "page_path": "frontend/src/app/red-team/page.tsx"
    }
]

for mod in modules:
    # Ensure dirs exist
    os.makedirs(os.path.dirname(os.path.join(base_dir, mod["engine_path"])), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(base_dir, mod["route_path"])), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(base_dir, mod["page_path"])), exist_ok=True)
    
    # Engine file
    with open(os.path.join(base_dir, mod["engine_path"]), "w") as f:
        f.write(f'''import asyncio\nimport structlog\n\nlogger = structlog.get_logger("{mod['title']}")\n\nclass {mod['title']}Engine:\n    async def run(self, data: dict):\n        await asyncio.sleep(1)\n        return {{"status": "success", "module": "{mod['title']}", "data": data, "findings": []}}\n''')
        
    # Route file
    with open(os.path.join(base_dir, mod["route_path"]), "w") as f:
        f.write(f'''from fastapi import APIRouter, Depends\nfrom pydantic import BaseModel\nfrom backend.engine.{os.path.basename(os.path.dirname(mod['engine_path']))}.{os.path.basename(mod['engine_path']).replace(".py","")} import {mod['title']}Engine\n\nrouter = APIRouter()\nengine = {mod['title']}Engine()\n\nclass {mod['title'].capitalize()}Request(BaseModel):\n    target: str\n    options: dict = {{}}\n\n@router.post("/run")\nasync def run_module(req: {mod['title'].capitalize()}Request):\n    return await engine.run(req.model_dump())\n''')

    # Next.js Page
    with open(os.path.join(base_dir, mod["page_path"]), "w") as f:
        f.write(f'''"use client";
import {{ useState }} from "react";
import {{ motion }} from "framer-motion";

export default function {mod['title']}Page() {{
  const [target, setTarget] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runTest = async () => {{
    setLoading(true);
    try {{
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/v1/{mod['name']}/run", {{
        method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify({{target}})
      }});
      setResult(await res.json());
    }} catch (e) {{
      console.error(e);
    }} finally {{
      setLoading(false);
    }}
  }};

  return (
    <div className="min-h-screen p-6">
      <h1 className="text-2xl font-bold text-white mb-2">{mod['title']}</h1>
      <p className="text-gray-400 mb-6">{mod['desc']}</p>
      
      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5 mb-6">
        <input value={{target}} onChange={{e => setTarget(e.target.value)}} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white mb-4 focus:outline-none" placeholder="Target..." />
        <button onClick={{runTest}} disabled={{loading}} className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors">
          {{loading ? "Running..." : "Execute"}}
        </button>
      </div>
      
      {{result && (
        <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <pre className="text-xs text-green-400 font-mono">{{JSON.stringify(result, null, 2)}}</pre>
        </div>
      )}}
    </div>
  );
}}
''')

print("Generated boilerplate for 5 AI modules.")
