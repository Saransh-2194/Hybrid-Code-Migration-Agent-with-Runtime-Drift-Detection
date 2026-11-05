
import ast
from typing import Any


class IssueDetector:
    """
    Detects potential Python migration issues using AST analysis
    and the requested target Python version.
    """

    # Module removals / API removals
    REMOVED_MODULES = {
        "distutils": (3, 12),
        "imp": (3, 12),
        "cgi": (3, 13),
        "asynchat": (3, 12),
        "asyncore": (3, 12),
        "smtpd": (3, 12),
        "lib2to3": (3, 13),
    }

    # Removed or deprecated APIs
    REMOVED_APIS = {
        "inspect.getargspec": (3, 11),
        "inspect.formatargspec": (3, 11),
        "asyncio.coroutine": (3, 11),
        "asyncio.coroutines.CoroWrapper": (3, 11),
    }

    # collections aliases removed in Python 3.10
    COLLECTIONS_ALIASES = {
        "Mapping",
        "MutableMapping",
        "Sequence",
        "MutableSequence",
        "Iterable",
        "MutableSet",
        "Callable",
    }

    def __init__(self, target_python: str):
        self.target_python = self._parse_version(target_python)

    @staticmethod
    def _parse_version(version: str) -> tuple[int, int]:
        """
        Convert version strings such as 3.12 or 3.12.1
        into a comparable tuple.
        """

        parts = version.strip().split(".")

        if len(parts) < 2:
            raise ValueError(
                f"Invalid Python version: {version}"
            )

        try:
            return int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError(
                f"Invalid Python version: {version}"
            ) from exc

    def _is_target_at_least(
        self,
        required_version: tuple[int, int]
    ) -> bool:
        return self.target_python >= required_version

    def _create_issue(
        self,
        file_path: str,
        line: int,
        issue_type: str,
        description: str,
        severity: str,
        recommendation: str
    ) -> dict[str, Any]:

        return {
            "file": file_path,
            "line": line,
            "issue_type": issue_type,
            "description": description,
            "severity": severity,
            "target_python": ".".join(
                map(str, self.target_python)
            ),
            "recommendation": recommendation,
        }

    def detect(self, source_code: str, file_path: str = "<source>") -> dict[str, Any]:
        """
        Analyze source code and detect migration issues.
        """

        issues = []

        try:
            tree = ast.parse(source_code, filename=file_path)

        except SyntaxError as exc:
            issues.append(
                self._create_issue(
                    file_path=file_path,
                    line=exc.lineno or 1,
                    issue_type="syntax_error",
                    description=exc.msg,
                    severity="high",
                    recommendation=(
                        "Fix the syntax error before migration analysis."
                    )
                )
            )

            return {
                "file": file_path,
                "status": "syntax_error",
                "issues": issues,
                "issue_count": len(issues),
            }

        for node in ast.walk(tree):

            # ------------------------------------------
            # 1. Removed modules
            # ------------------------------------------

            if isinstance(node, ast.Import):

                for alias in node.names:
                    module = alias.name.split(".")[0]

                    if module in self.REMOVED_MODULES:

                        removed_version = self.REMOVED_MODULES[module]

                        if self._is_target_at_least(removed_version):
                            issues.append(
                                self._create_issue(
                                    file_path,
                                    node.lineno,
                                    "removed_module",
                                    f"Module '{module}' is removed "
                                    f"in Python {removed_version[0]}."
                                    f"{removed_version[1]}",
                                    "high",
                                    "Replace the removed module "
                                    "with its supported alternative."
                                )
                            )

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""
                root_module = module.split(".")[0]

                # Removed modules
                if root_module in self.REMOVED_MODULES:

                    removed_version = self.REMOVED_MODULES[root_module]

                    if self._is_target_at_least(removed_version):
                        issues.append(
                            self._create_issue(
                                file_path,
                                node.lineno,
                                "removed_module",
                                f"Module '{root_module}' is removed "
                                f"in Python {removed_version[0]}."
                                f"{removed_version[1]}",
                                "high",
                                "Replace the removed module "
                                "with its supported alternative."
                            )
                        )

                # collections aliases
                if (
                    module == "collections"
                    and self._is_target_at_least((3, 10))
                ):

                    for alias in node.names:

                        if alias.name in self.COLLECTIONS_ALIASES:
                            issues.append(
                                self._create_issue(
                                    file_path,
                                    node.lineno,
                                    "removed_collections_alias",
                                    f"'{alias.name}' imported from "
                                    "collections is incompatible "
                                    "with Python 3.10+.",
                                    "high",
                                    "Import this name from "
                                    "collections.abc instead."
                                )
                            )

            # ------------------------------------------
            # 2. Removed APIs
            # ------------------------------------------

            elif isinstance(node, ast.Call):

                called_function = ast.unparse(node.func)

                if called_function in self.REMOVED_APIS:

                    removed_version = self.REMOVED_APIS[
                        called_function
                    ]

                    if self._is_target_at_least(removed_version):
                        issues.append(
                            self._create_issue(
                                file_path,
                                node.lineno,
                                "removed_api",
                                f"'{called_function}' was removed "
                                f"in Python {removed_version[0]}."
                                f"{removed_version[1]}.",
                                "high",
                                "Replace this API with its "
                                "supported alternative."
                            )
                        )

        return {
            "file": file_path,
            "status": "success",
            "issues": issues,
            "issue_count": len(issues),
        }
