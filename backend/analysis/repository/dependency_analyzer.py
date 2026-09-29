from pathlib import Path
import re


class DependencyAnalyzer:
    """
    Extracts dependency information from common Python
    dependency/configuration files.

    This component currently focuses on extraction.
    Compatibility checking will be added later.
    """

    DEPENDENCY_FILES = {
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-test.txt",
        "requirements-prod.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "Pipfile",
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

    def _read_file(self, filename: str) -> str | None:
        """Read a repository file if it exists."""

        path = self.repository_path / filename

        if not path.exists() or not path.is_file():
            return None

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    def _parse_requirement_line(self, line: str):
        """
        Parse a basic requirements.txt dependency line.

        Examples:
            requests==2.20.0
            flask>=2.0
            numpy
        """

        line = line.strip()

        # Ignore empty lines and comments
        if not line or line.startswith("#"):
            return None

        # Ignore pip options such as:
        # -r requirements-dev.txt
        # --index-url ...
        if line.startswith("-"):
            return None

        pattern = (
            r"^([A-Za-z0-9_.-]+)"
            r"\s*"
            r"((?:==|>=|<=|>|<|~=|!=).*)?$"
        )

        match = re.match(pattern, line)

        if not match:
            return None

        package = match.group(1)
        constraint = match.group(2)

        return {
            "package": package,
            "constraint": constraint.strip()
            if constraint
            else None,
            "source": "requirements.txt",
        }

    def _parse_requirements_file(
        self,
        filename: str,
        content: str
    ) -> list[dict]:

        dependencies = []

        for line in content.splitlines():

            dependency = self._parse_requirement_line(line)

            if dependency:
                dependency["source"] = filename
                dependencies.append(dependency)

        return dependencies

    def _parse_pyproject_dependencies(
        self,
        content: str
    ) -> list[dict]:

        dependencies = []

        # Basic extraction from:
        #
        # dependencies = [
        #     "requests>=2.0",
        #     "flask==2.0.0"
        # ]

        dependency_block = re.search(
            r"dependencies\s*=\s*\[(.*?)\]",
            content,
            re.DOTALL
        )

        if not dependency_block:
            return dependencies

        block = dependency_block.group(1)

        pattern = (
            r'["\']'
            r'([A-Za-z0-9_.-]+)'
            r'\s*'
            r'((?:==|>=|<=|>|<|~=|!=).*?)?'
            r'["\']'
        )

        matches = re.findall(pattern, block)

        for package, constraint in matches:

            dependencies.append(
                {
                    "package": package,
                    "constraint": constraint or None,
                    "source": "pyproject.toml",
                }
            )

        return dependencies

    def _parse_setup_python_dependencies(
        self,
        content: str
    ) -> list[dict]:

        dependencies = []

        # Basic extraction of:
        #
        # install_requires=[
        #     "requests>=2.0",
        #     "flask==2.0.0"
        # ]

        block_match = re.search(
            r"install_requires\s*=\s*\[(.*?)\]",
            content,
            re.DOTALL
        )

        if not block_match:
            return dependencies

        block = block_match.group(1)

        pattern = (
            r'["\']'
            r'([A-Za-z0-9_.-]+)'
            r'\s*'
            r'((?:==|>=|<=|>|<|~=|!=).*?)?'
            r'["\']'
        )

        matches = re.findall(pattern, block)

        for package, constraint in matches:

            dependencies.append(
                {
                    "package": package,
                    "constraint": constraint or None,
                    "source": "setup.py",
                }
            )

        return dependencies

    def _parse_setup_cfg(
        self,
        content: str
    ) -> list[dict]:

        dependencies = []

        # Example:
        #
        # [options]
        # install_requires =
        #     requests>=2.0
        #     flask==2.0.0

        block_match = re.search(
            r"\[options\].*?"
            r"install_requires\s*=\s*(.*?)(?=\n\[|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not block_match:
            return dependencies

        block = block_match.group(1)

        for line in block.splitlines():

            line = line.strip()

            if not line:
                continue

            dependency = self._parse_requirement_line(line)

            if dependency:
                dependency["source"] = "setup.cfg"
                dependencies.append(dependency)

        return dependencies

    def analyze(self) -> dict:
        """
        Analyze dependency declarations in the repository.
        """

        dependencies = []
        files_found = []

        # requirements files
        for filename in self.DEPENDENCY_FILES:

            content = self._read_file(filename)

            if content is None:
                continue

            files_found.append(filename)

            if filename.endswith(".txt"):
                dependencies.extend(
                    self._parse_requirements_file(
                        filename,
                        content
                    )
                )

            elif filename == "pyproject.toml":
                dependencies.extend(
                    self._parse_pyproject_dependencies(
                        content
                    )
                )

            elif filename == "setup.py":
                dependencies.extend(
                    self._parse_setup_python_dependencies(
                        content
                    )
                )

            elif filename == "setup.cfg":
                dependencies.extend(
                    self._parse_setup_cfg(
                        content
                    )
                )

        # Remove duplicate entries while preserving information.
        unique_dependencies = []

        seen = set()

        for dependency in dependencies:

            key = (
                dependency["package"].lower(),
                dependency["constraint"],
                dependency["source"],
            )

            if key in seen:
                continue

            seen.add(key)
            unique_dependencies.append(dependency)

        return {
            "files_found": sorted(files_found),
            "dependencies": unique_dependencies,
            "count": len(unique_dependencies),
        }