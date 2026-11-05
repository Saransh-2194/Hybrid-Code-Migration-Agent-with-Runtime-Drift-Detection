
import ast
from pathlib import Path
from typing import Any


class ASTAnalyzer:
    """
    Analyzes Python source code using its Abstract Syntax Tree (AST).
    Does not execute the source code.
    """

    def analyze_file(self, file_path: str | Path) -> dict[str, Any]:
        file_path = Path(file_path)

        try:
            source_code = file_path.read_text(encoding="utf-8")

            return self.analyze_source(
                source_code=source_code,
                file_path=str(file_path)
            )

        except OSError as exc:
            return {
                "file": str(file_path),
                "status": "error",
                "error": str(exc)
            }

    def analyze_source(
        self,
        source_code: str,
        file_path: str = "<source>"
    ) -> dict[str, Any]:

        # Parse source code into AST
        try:
            tree = ast.parse(source_code, filename=file_path)

        except SyntaxError as exc:
            return {
                "file": file_path,
                "status": "syntax_error",
                "error": exc.msg,
                "line": exc.lineno,
                "column": exc.offset
            }

        # Initialize analysis result
        analysis = {
            "file": file_path,
            "status": "success",
            "functions": [],
            "classes": [],
            "imports": [],
            "calls": [],
            "conditions": [],
            "returns": [],
            "assignments": []
        }

        # Traverse AST nodes
        for node in ast.walk(tree):

            # Function definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                analysis["functions"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": node.end_lineno,
                    "arguments": [
                        arg.arg for arg in node.args.args
                    ],
                    "is_async": isinstance(
                        node, ast.AsyncFunctionDef
                    )
                })

            # Class definitions
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": node.end_lineno,
                    "bases": [
                        ast.unparse(base)
                        for base in node.bases
                    ]
                })

            # Import statements
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })

            # Import from statements
            elif isinstance(node, ast.ImportFrom):
                analysis["imports"].append({
                    "module": node.module,
                    "names": [
                        alias.name for alias in node.names
                    ],
                    "level": node.level,
                    "line": node.lineno
                })

            # Function and method calls
            elif isinstance(node, ast.Call):
                analysis["calls"].append({
                    "function": ast.unparse(node.func),
                    "line": node.lineno
                })

            # If conditions
            elif isinstance(node, ast.If):
                analysis["conditions"].append({
                    "type": "if",
                    "line": node.lineno,
                    "condition": ast.unparse(node.test)
                })

            # For loops
            elif isinstance(node, ast.For):
                analysis["conditions"].append({
                    "type": "for",
                    "line": node.lineno,
                    "condition": ast.unparse(node.iter)
                })

            # While loops
            elif isinstance(node, ast.While):
                analysis["conditions"].append({
                    "type": "while",
                    "line": node.lineno,
                    "condition": ast.unparse(node.test)
                })

            # Return statements
            elif isinstance(node, ast.Return):
                analysis["returns"].append({
                    "line": node.lineno,
                    "expression": (
                        ast.unparse(node.value)
                        if node.value else None
                    )
                })

            # Assignments
            elif isinstance(node, ast.Assign):
                analysis["assignments"].append({
                    "line": node.lineno,
                    "targets": [
                        ast.unparse(target)
                        for target in node.targets
                    ],
                    "value": ast.unparse(node.value)
                })

            # Annotated assignments
            elif isinstance(node, ast.AnnAssign):
                analysis["assignments"].append({
                    "line": node.lineno,
                    "targets": [
                        ast.unparse(node.target)
                    ],
                    "value": (
                        ast.unparse(node.value)
                        if node.value else None
                    )
                })

        return analysis
