import structlog
import ast
from typing import List, Dict, Any
import tree_sitter
import tree_sitter_python as tspython

logger = structlog.get_logger("DevShield.SAST")

class ASTAnalyzer:
    """
    True AST-based SAST engine using tree-sitter.
    Replaces the naive regex and subprocess wrapper approach.
    """
    def __init__(self):
        # We use tree-sitter v0.21+ API
        self.language = tree_sitter.Language(tspython.language())
        self.parser = tree_sitter.Parser(self.language)

    def _matches(self, query: tree_sitter.Query, root_node: tree_sitter.Node):
        if hasattr(tree_sitter, "QueryCursor"):
            cursor = tree_sitter.QueryCursor(query)
            for _, captures in cursor.matches(root_node):
                yield captures
            return

        for match in query.matches(root_node):
            yield match[1]

    @staticmethod
    def _first_capture(captures: Dict[str, Any], name: str):
        node = captures.get(name)
        if isinstance(node, list):
            return node[0] if node else None
        return node

    @staticmethod
    def _is_dynamic_sql_expr(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mod, ast.Add))
            or isinstance(node, ast.JoinedStr)
            or (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "format"
            )
        )

    def _scan_sql_ast_fallback(self, code: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return findings

        dynamic_vars: Dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and self._is_dynamic_sql_expr(node.value):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        dynamic_vars[target.id] = node.lineno

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute) or node.func.attr != "execute":
                continue
            if not node.args:
                continue

            arg = node.args[0]
            line = None
            if self._is_dynamic_sql_expr(arg):
                line = getattr(arg, "lineno", node.lineno)
            elif isinstance(arg, ast.Name) and arg.id in dynamic_vars:
                line = dynamic_vars[arg.id]

            if line:
                findings.append({
                    "title": "SQL Injection Risk",
                    "severity": "CRITICAL",
                    "confidence": 90,
                    "line": line,
                    "description": "Dynamic string construction detected in SQL execution. Use parameterized queries instead.",
                    "cwe": "CWE-89",
                    "owasp": "A03:2021-Injection"
                })

        return findings

    def scan_python(self, code: str) -> List[Dict[str, Any]]:
        """
        Scans Python code for injection vulnerabilities and dangerous function calls.
        """
        tree = self.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        findings = []

        # We'll write tree-sitter queries to find specific dangerous patterns
        # 1. SQL Injection (concatenation in cursor.execute)
        sql_query_str = """
        (call
          function: (attribute attribute: (identifier) @method (#eq? @method "execute"))
          arguments: (argument_list
            (binary_operator
              operator: "%"
            ) @vulnerable_arg
          )
        )
        (call
          function: (attribute attribute: (identifier) @method (#eq? @method "execute"))
          arguments: (argument_list
            (call
              function: (attribute attribute: (identifier) @format_method (#eq? @format_method "format"))
            ) @vulnerable_arg
          )
        )
        (call
          function: (attribute attribute: (identifier) @method (#eq? @method "execute"))
          arguments: (argument_list
            (string
              (interpolation)
            ) @vulnerable_arg
          )
        )
        """
        
        try:
            sql_query = self.language.query(sql_query_str)
            for captures in self._matches(sql_query, root_node):
                node = self._first_capture(captures, "vulnerable_arg")
                if node:
                    findings.append({
                        "title": "SQL Injection Risk",
                        "severity": "CRITICAL",
                        "confidence": 95,
                        "line": node.start_point[0] + 1,
                        "description": "Dynamic string construction detected in SQL execution. Use parameterized queries instead.",
                        "cwe": "CWE-89",
                        "owasp": "A03:2021-Injection"
                    })
        except Exception as e:
            logger.error(f"Error in SQL injection query: {e}")

        if not any(f["title"] == "SQL Injection Risk" for f in findings):
            findings.extend(self._scan_sql_ast_fallback(code))

        # 2. Command Injection (os.system, subprocess with shell=True)
        cmd_query_str = """
        (call
          function: (attribute object: (identifier) @obj attribute: (identifier) @func)
          (#eq? @obj "os")
          (#eq? @func "system")
        ) @vuln
        
        (call
          function: (attribute object: (identifier) @obj attribute: (identifier) @func)
          (#eq? @obj "subprocess")
          arguments: (argument_list
            (keyword_argument
              name: (identifier) @kw
              value: (true)
              (#eq? @kw "shell")
            )
          )
        ) @vuln
        """
        try:
            cmd_query = self.language.query(cmd_query_str)
            for captures in self._matches(cmd_query, root_node):
                node = self._first_capture(captures, "vuln")
                if node:
                    findings.append({
                        "title": "Command Injection Risk",
                        "severity": "CRITICAL",
                        "confidence": 90,
                        "line": node.start_point[0] + 1,
                        "description": "Unsafe OS command execution detected. Avoid shell=True or os.system.",
                        "cwe": "CWE-78",
                        "owasp": "A03:2021-Injection"
                    })
        except Exception as e:
            logger.error(f"Error in Command injection query: {e}")

        # 3. Dangerous Deserialization (pickle)
        pickle_query_str = """
        (call
          function: (attribute object: (identifier) @obj attribute: (identifier) @func)
          (#eq? @obj "pickle")
          (#eq? @func "loads")
        ) @vuln
        """
        try:
            pickle_query = self.language.query(pickle_query_str)
            for captures in self._matches(pickle_query, root_node):
                node = self._first_capture(captures, "vuln")
                if node:
                    findings.append({
                        "title": "Insecure Deserialization",
                        "severity": "HIGH",
                        "confidence": 95,
                        "line": node.start_point[0] + 1,
                        "description": "Detected usage of pickle.loads which can lead to Remote Code Execution. Use json.loads.",
                        "cwe": "CWE-502",
                        "owasp": "A08:2021-Software and Data Integrity Failures"
                    })
        except Exception as e:
            logger.error(f"Error in Pickle query: {e}")

        return findings

analyzer = ASTAnalyzer()

def run_sast(code: str, language: str = "python") -> List[Dict[str, Any]]:
    if language.lower() == "python":
        return analyzer.scan_python(code)
    return []
