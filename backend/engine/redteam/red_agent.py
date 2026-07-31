import asyncio
import ipaddress
import shutil
import socket
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.parse import urlparse

import structlog

from backend.config import settings

logger = structlog.get_logger("DevShield.RedAgent")

COMMON_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 5900, 6379, 8000, 8080, 8443]
MAX_OUTPUT_CHARS = 12000


@dataclass
class ToolStep:
    name: str
    command: List[str]
    purpose: str


class RedAgentEngine:
    """
    Authorized red-team reconnaissance orchestrator.

    This engine performs non-exploit reconnaissance only after the caller confirms
    authorization. It never invokes a shell and returns structured evidence for
    every attempted step.
    """

    def _normalize_target(self, target: str) -> str:
        raw = target.strip()
        if not raw:
            raise ValueError("No target provided")

        parsed = urlparse(raw if "://" in raw else f"//{raw}")
        host = parsed.hostname or raw.split("/")[0]
        if not host:
            raise ValueError("Invalid target")
        return host

    def _resolve_target(self, host: str) -> Dict[str, Any]:
        try:
            ip = socket.gethostbyname(host)
            ip_obj = ipaddress.ip_address(ip)
            return {
                "host": host,
                "ip": ip,
                "is_private": ip_obj.is_private,
                "is_loopback": ip_obj.is_loopback,
            }
        except Exception as exc:
            raise ValueError(f"Could not resolve target: {host}") from exc

    def _is_allowed_target(self, host: str, resolved: Dict[str, Any]) -> bool:
        allowed = [item.strip().lower() for item in settings.allowed_scan_targets.split(",") if item.strip()]
        if allowed and not any(host.lower() == item or host.lower().endswith(f".{item}") for item in allowed):
            return False
        if not settings.allow_private_scan_targets and (resolved.get("is_private") or resolved.get("is_loopback")):
            return False
        return True

    async def _socket_port_scan(self, host: str, ports: List[int] | None = None) -> List[int]:
        ports = ports or COMMON_PORTS

        async def check(port: int) -> int | None:
            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1.0)
                writer.close()
                await writer.wait_closed()
                return port
            except Exception:
                return None

        results = await asyncio.gather(*(check(port) for port in ports))
        return [port for port in results if port is not None]

    def _build_steps(self, host: str, options: Dict[str, Any]) -> List[ToolStep]:
        intensity = str(options.get("intensity", "safe")).lower()
        top_ports = "100" if intensity == "safe" else "1000"
        url = host if host.startswith(("http://", "https://")) else f"http://{host}"

        steps = [
            ToolStep("nmap", ["nmap", "-T3", "-Pn", "--top-ports", top_ports, host], "TCP service discovery"),
            ToolStep("nikto", ["nikto", "-host", url, "-nointeractive", "-Tuning", "b"], "Web server misconfiguration check"),
        ]

        wordlist = options.get("wordlist") or "/usr/share/wordlists/dirb/common.txt"
        steps.append(ToolStep("gobuster", ["gobuster", "dir", "-q", "-u", url, "-w", str(wordlist), "-t", "10"], "Content discovery"))
        return steps

    async def _run_tool(self, step: ToolStep, timeout: int) -> Dict[str, Any]:
        executable = shutil.which(step.command[0])
        if not executable:
            return {
                "tool": step.name,
                "purpose": step.purpose,
                "status": "not_installed",
                "command": step.command,
                "stdout": "",
                "stderr": f"{step.command[0]} is not installed in this runtime",
            }

        command = [executable, *step.command[1:]]
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "tool": step.name,
                "purpose": step.purpose,
                "status": "completed" if proc.returncode == 0 else "failed",
                "exit_code": proc.returncode,
                "command": step.command,
                "stdout": stdout.decode(errors="replace")[:MAX_OUTPUT_CHARS],
                "stderr": stderr.decode(errors="replace")[:MAX_OUTPUT_CHARS],
            }
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return {
                "tool": step.name,
                "purpose": step.purpose,
                "status": "timeout",
                "command": step.command,
                "stdout": "",
                "stderr": f"Timed out after {timeout} seconds",
            }

    async def _plan(self, host: str, scan_data: str) -> str:
        from backend.ai.ai_router import AIRouter
        from backend.ai.prompt_engineer import build_redteam_prompt
        
        router = AIRouter()
        prompt = build_redteam_prompt(host, scan_data)
        text, _, _ = await router.route_request(prompt)
        return text

    def _build_attack_graph(self, target: str, open_ports: List[int]) -> dict:
        import networkx as nx
        from networkx.readwrite import json_graph
        G = nx.DiGraph()
        G.add_node("Internet", type="EntryPoint")
        G.add_node(target, type="TargetAsset")
        
        for port in open_ports:
            node_name = f"{target}:{port}"
            G.add_node(node_name, type="ExposedService", port=port)
            G.add_edge("Internet", node_name, relation="can_reach")
            G.add_edge(node_name, target, relation="hosts")
            
        # Calculate Centrality to find bottlenecks
        if len(G.nodes) > 1:
            centrality = nx.betweenness_centrality(G)
            nx.set_node_attributes(G, centrality, 'centrality')
            
        return json_graph.node_link_data(G)

    async def run(self, data: dict) -> Dict[str, Any]:
        try:
            target = self._normalize_target(data.get("target", ""))
            options = data.get("options") or {}
            resolved = self._resolve_target(target)
            if not self._is_allowed_target(target, resolved):
                raise ValueError("Target is not allowed by scan policy")
        except ValueError as exc:
            return {"status": "error", "module": "RedAgent", "message": str(exc)}

        authorized = bool(options.get("authorization_confirmed"))
        execute_tools = bool(options.get("execute_tools"))
        timeout = int(options.get("timeout_seconds", 60))

        result: Dict[str, Any] = {
            "status": "success",
            "module": "RedAgent",
            "target": target,
            "resolved_target": resolved,
            "authorization_required": True,
            "authorization_confirmed": authorized,
            "executed_steps": [],
            "open_ports": [],
        }

        if not authorized:
            result["status_detail"] = "Planning-only mode. Set options.authorization_confirmed=true for authorized reconnaissance."
            return result

        result["open_ports"] = await self._socket_port_scan(target)

        if execute_tools:
            steps = self._build_steps(target, options)
            result["executed_steps"] = [await self._run_tool(step, timeout) for step in steps]
            
            # 1. Graph Modeling using NetworkX
            result["attack_graph"] = self._build_attack_graph(target, result["open_ports"])

            # 2. Structured Output & Risk Triaging
            import json
            raw_data = json.dumps({
                "open_ports": result["open_ports"],
                "tool_results": result["executed_steps"]
            }, indent=2)
            
            ai_text = await self._plan(target, raw_data)
            try:
                # Strip markdown code blocks to ensure clean JSON parsing
                cleaned_text = ai_text.strip()
                if cleaned_text.startswith("```json"): cleaned_text = cleaned_text[7:]
                elif cleaned_text.startswith("```"): cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"): cleaned_text = cleaned_text[:-3]
                
                result["ai_analysis_structured"] = json.loads(cleaned_text.strip())
            except Exception as e:
                result["ai_analysis_structured"] = {"error": "Failed to parse structured JSON", "raw": ai_text}
        else:
            result["status_detail"] = "Authorization confirmed; completed built-in bounded port scan. Set options.execute_tools=true to run installed recon tools."

        return result
