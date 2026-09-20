from pathlib import Path
from typing import List, Dict


class FileScanner:
    """
    Scans a repository and categorizes its files.

    This component does not modify or execute repository code.
    """

    DEFAULT_IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "dist",
        "build",
        ".idea",
        ".vscode",
    }

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
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "tox.ini",
        "pytest.ini",
        "Dockerfile",
        "docker-compose.yml",
        ".flake8",
        "mypy.ini",
    }

    def __init__(
        self,
        repository_path: str,
        ignored_directories: set[str] | None = None,
    ):
        self.repository_path = Path(repository_path).resolve()

        if not self.repository_path.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repository_path}"
            )

        self.ignored_directories = (
            ignored_directories
            if ignored_directories is not None
            else self.DEFAULT_IGNORED_DIRECTORIES
        )

    def _should_ignore(self, path: Path) -> bool:
        """
        Determine whether a path belongs to an ignored directory.
        """

        return any(
            directory in self.ignored_directories
            for directory in path.parts
        )

    def scan(self) -> List[Dict]:
        """
        Scan all relevant files in the repository.

        Returns a list containing metadata for each file.
        """

        files = []

        for path in self.repository_path.rglob("*"):

            if not path.is_file():
                continue

            if self._should_ignore(path):
                continue

            relative_path = path.relative_to(self.repository_path)

            files.append(
                {
                    "path": str(relative_path),
                    "name": path.name,
                    "extension": path.suffix,
                }
            )

        return sorted(files, key=lambda item: item["path"])

    def python_files(self) -> List[str]:
        """
        Return all Python source files.
        """

        return [
            file["path"]
            for file in self.scan()
            if file["extension"] == ".py"
        ]

    def test_files(self) -> List[str]:
        """
        Identify likely Python test files.

        This is intentionally a simple discovery mechanism.
        The actual test runner will later use pytest/unittest
        discovery rather than relying only on this method.
        """

        test_files = []

        for file in self.scan():

            if file["extension"] != ".py":
                continue

            path = Path(file["path"])
            name = path.name.lower()

            if (
                name.startswith("test_")
                or name.endswith("_test.py")
                or "tests" in path.parts
            ):
                test_files.append(file["path"])

        return sorted(set(test_files))

    def dependency_files(self) -> List[str]:
        """
        Find files containing dependency information.
        """

        return [
            file["path"]
            for file in self.scan()
            if file["name"] in self.DEPENDENCY_FILES
        ]

    def version_files(self) -> List[str]:
        """
        Find files that may specify the Python version.
        """

        return [
            file["path"]
            for file in self.scan()
            if file["name"] in self.VERSION_FILES
        ]

    def config_files(self) -> List[str]:
        """
        Find relevant project/configuration files.
        """

        return [
            file["path"]
            for file in self.scan()
            if file["name"] in self.CONFIG_FILES
        ]

    def summary(self) -> Dict:
        """
        Return a compact summary of the repository.
        """

        files = self.scan()

        python_files = self.python_files()
        test_files = self.test_files()

        return {
            "repository_path": str(self.repository_path),
            "total_files": len(files),
            "python_files": len(python_files),
            "test_files": len(test_files),
            "dependency_files": self.dependency_files(),
            "version_files": self.version_files(),
            "config_files": self.config_files(),
        }