import ast

class DocumentationGenerator:
    @staticmethod
    async def generate(code: str) -> str:
        """
        Parses code via AST to extract docstrings and semantic structure,
        then synthesizes Markdown.
        """
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except Exception:
            return "Failed to parse AST. Code may be malformed or non-Python.\n\n```text\n" + code + "\n```"

        markdown = "# Generated Code Documentation\n\n## Classes\n"
        for c in classes:
            doc = ast.get_docstring(c) or "No description provided."
            markdown += f"### `class {c.name}`\n{doc}\n\n"

        markdown += "## Functions\n"
        for f in functions:
            doc = ast.get_docstring(f) or "No description provided."
            args = [a.arg for a in f.args.args]
            arg_str = ", ".join(args)
            markdown += f"### `def {f.name}({arg_str})`\n{doc}\n\n"

        return markdown
