import ast
from pathlib import Path
from typing import Dict, List, Any


class ASTParser:
    """
    Parses Python files using Python's built-in AST module
    and extracts structural information about the codebase.
    """

    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Python file and return its AST metadata.
        """

        path = Path(file_path)

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            metadata = {
                "file": str(path),
                "imports": [],
                "classes": [],
                "functions": [],
                "globals": []
            }

            for node in tree.body:

                # ------------------------
                # Imports
                # ------------------------
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata["imports"].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        metadata["imports"].append(
                            f"{module}.{alias.name}"
                        )

                # ------------------------
                # Global Variables
                # ------------------------
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            metadata["globals"].append(target.id)

                # ------------------------
                # Functions
                # ------------------------
                elif isinstance(node, ast.FunctionDef):
                    metadata["functions"].append(
                        self.extract_function(node)
                    )

                # ------------------------
                # Classes
                # ------------------------
                elif isinstance(node, ast.ClassDef):
                    metadata["classes"].append(
                        self.extract_class(node)
                    )

            return metadata

        except Exception as e:
            return {
                "file": str(path),
                "error": str(e)
            }

    def extract_function(self, node: ast.FunctionDef) -> Dict[str, Any]:

        return {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "decorators": [
                ast.unparse(d)
                for d in node.decorator_list
            ],
            "docstring": ast.get_docstring(node),
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno)
        }

    def extract_class(self, node: ast.ClassDef) -> Dict[str, Any]:

        methods = []

        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                methods.append(
                    self.extract_function(child)
                )

        return {
            "name": node.name,
            "bases": [
                ast.unparse(base)
                for base in node.bases
            ],
            "docstring": ast.get_docstring(node),
            "methods": methods,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno)
        }

    def parse_repository(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Parse every Python file inside a repository.
        """

        repo = Path(repo_path)

        results = []

        for py_file in repo.rglob("*.py"):
            results.append(
                self.parse_file(py_file)
            )

        return results