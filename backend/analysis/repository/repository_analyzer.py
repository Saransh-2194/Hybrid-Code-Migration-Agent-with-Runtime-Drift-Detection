from pathlib import Path
from typing import Any


class RepositoryAnalyzer:
    """
    Analyzes the structure of a Python repository.

    This module does not modify the repository.
    It only collects information that will later be
    supplied to the static analysis and LLM pipeline.
    """

    DEPENDENCY_FILES = {
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "Pipfile.lock",
        "poetry.lock",
    }

    VERSION_FILES = {
        ".python-version",
        "runtime.txt",
    }

    CONFIG_FILES = {
        "tox.ini",
        "pytest.ini",
        "setup.cfg",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
    }

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()

        if not self.repository_path.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repository_path}"
            )

    def get_all_files(self) -> list[dict[str, Any]]:
        """Return all files in the repository."""

        files = []

        for path in self.repository_path.rglob("*"):

            if not path.is_file():
                continue

            # Ignore common generated/version-control directories.
            if any(
                part in {
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    "node_modules",
                    ".pytest_cache",
                }
                for part in path.parts
            ):
                continue

            relative_path = path.relative_to(self.repository_path)

            files.append(
                {
                    "path": str(relative_path),
                    "extension": path.suffix,
                    "name": path.name,
                }
            )

        return files

    def get_python_files(self) -> list[str]:
        """Return Python source files."""

        python_files = []

        for path in self.repository_path.rglob("*.py"):

            if any(
                part in {
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    "node_modules",
                }
                for part in path.parts
            ):
                continue

            python_files.append(
                str(path.relative_to(self.repository_path))
            )

        return sorted(python_files)

    def get_test_files(self) -> list[str]:
        """
        Identify likely test files.

        This is intentionally heuristic for now.
        We will improve test discovery when we build
        the dynamic execution module.
        """

        test_files = []

        for path in self.repository_path.rglob("*.py"):

            if any(
                part in {
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    "node_modules",
                }
                for part in path.parts
            ):
                continue

            filename = path.name.lower()

            if (
                filename.startswith("test_")
                or filename.endswith("_test.py")
                or "tests" in path.parts
            ):
                test_files.append(
                    str(path.relative_to(self.repository_path))
                )

        return sorted(set(test_files))

    def get_dependency_files(self) -> list[str]:
        """Find files that may contain dependency information."""

        found = []

        for filename in self.DEPENDENCY_FILES:

            path = self.repository_path / filename

            if path.exists() and path.is_file():
                found.append(filename)

        return sorted(found)

    def get_version_files(self) -> list[str]:
        """Find files that may specify the Python version."""

        found = []

        for filename in self.VERSION_FILES:

            path = self.repository_path / filename

            if path.exists() and path.is_file():
                found.append(filename)

        return sorted(found)

    def get_config_files(self) -> list[str]:
        """Find relevant Python/project configuration files."""

        found = []

        for filename in self.CONFIG_FILES:

            path = self.repository_path / filename

            if path.exists() and path.is_file():
                found.append(filename)

        return sorted(found)

    def analyze(self) -> dict[str, Any]:
        """
        Run the complete repository structure analysis.
        """

        all_files = self.get_all_files()
        python_files = self.get_python_files()
        test_files = self.get_test_files()
        dependency_files = self.get_dependency_files()
        version_files = self.get_version_files()
        config_files = self.get_config_files()

        return {
            "repository_path": str(self.repository_path),
            "statistics": {
                "total_files": len(all_files),
                "python_files": len(python_files),
                "test_files": len(test_files),
            },
            "files": all_files,
            "python_files": python_files,
            "test_files": test_files,
            "dependency_files": dependency_files,
            "version_files": version_files,
            "config_files": config_files,
        }