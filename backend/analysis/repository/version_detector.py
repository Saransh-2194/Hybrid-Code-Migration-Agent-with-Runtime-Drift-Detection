from pathlib import Path
import re
from typing import Optional


class PythonVersionDetector:
    """
    Detects Python version requirements declared by a repository.

    The detector collects evidence from common project configuration
    files. It does not execute repository code.
    """

    VERSION_FILES = {
        ".python-version",
        "runtime.txt",
    }

    CONFIG_FILES = {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "tox.ini",
        "Dockerfile",
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

    def _read_file(self, filename: str) -> Optional[str]:
        """
        Read a repository file if it exists.
        """

        path = self.repository_path / filename

        if not path.exists() or not path.is_file():
            return None

        try:
            return path.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except OSError:
            return None

    def _extract_version_from_python_version_file(
        self,
        filename: str
    ) -> Optional[str]:

        content = self._read_file(filename)

        if not content:
            return None

        version = content.strip().splitlines()[0].strip()

        if version:
            return version

        return None

    def _extract_requires_python(
        self,
        content: str
    ) -> Optional[str]:

        # Example:
        # requires-python = ">=3.8,<3.12"
        pattern = r'requires-python\s*=\s*["\']([^"\']+)["\']'

        match = re.search(
            pattern,
            content,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        return None

    def _extract_python_requires(
        self,
        content: str
    ) -> Optional[str]:

        # Examples:
        #
        # python_requires=">=3.8"
        # python_requires='>=3.7,<3.11'

        pattern = (
            r'python_requires\s*=\s*'
            r'["\']([^"\']+)["\']'
        )

        match = re.search(
            pattern,
            content,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        return None

    def _extract_tox_python_versions(
        self,
        content: str
    ) -> list[str]:

        versions = []

        # Example:
        #
        # envlist = py38,py39,py310
        #
        pattern = r'envlist\s*=\s*([^\n]+)'

        match = re.search(
            pattern,
            content,
            re.IGNORECASE
        )

        if not match:
            return versions

        envlist = match.group(1)

        for environment in envlist.split(","):

            environment = environment.strip()

            version_match = re.fullmatch(
                r'py(\d{2,3})',
                environment
            )

            if not version_match:
                continue

            value = version_match.group(1)

            if len(value) == 2:
                # py38 → Python 3.8
                versions.append(
                    f"3.{value[1]}"
                )

            elif len(value) == 3:
                # py310 → Python 3.10
                versions.append(
                    f"3.{value[1:]}"
                )

        return versions

    def _extract_docker_python_versions(
        self,
        content: str
    ) -> list[str]:

        versions = []

        # Examples:
        #
        # FROM python:3.8
        # FROM python:3.8-slim
        # FROM python:3.10-alpine

        pattern = r'FROM\s+python:(\d+\.\d+(?:\.\d+)?)'

        matches = re.findall(
            pattern,
            content,
            re.IGNORECASE
        )

        versions.extend(matches)

        return versions

    def detect(self) -> dict:
        """
        Detect Python version information from the repository.

        Returns structured evidence rather than assuming that one
        source is always correct.
        """

        evidence = []

        # ---------------------------------------------------------
        # .python-version / runtime.txt
        # ---------------------------------------------------------

        for filename in self.VERSION_FILES:

            version = self._extract_version_from_python_version_file(
                filename
            )

            if version:
                evidence.append(
                    {
                        "source": filename,
                        "type": "explicit_version",
                        "value": version,
                    }
                )

        # ---------------------------------------------------------
        # pyproject.toml
        # ---------------------------------------------------------

        pyproject = self._read_file("pyproject.toml")

        if pyproject:

            requires_python = self._extract_requires_python(
                pyproject
            )

            if requires_python:
                evidence.append(
                    {
                        "source": "pyproject.toml",
                        "type": "requires_python",
                        "value": requires_python,
                    }
                )

        # ---------------------------------------------------------
        # setup.py / setup.cfg
        # ---------------------------------------------------------

        for filename in ["setup.py", "setup.cfg"]:

            content = self._read_file(filename)

            if not content:
                continue

            python_requires = self._extract_python_requires(
                content
            )

            if python_requires:
                evidence.append(
                    {
                        "source": filename,
                        "type": "python_requires",
                        "value": python_requires,
                    }
                )

        # ---------------------------------------------------------
        # tox.ini
        # ---------------------------------------------------------

        tox_content = self._read_file("tox.ini")

        if tox_content:

            versions = self._extract_tox_python_versions(
                tox_content
            )

            if versions:
                evidence.append(
                    {
                        "source": "tox.ini",
                        "type": "tox_versions",
                        "value": versions,
                    }
                )

        # ---------------------------------------------------------
        # Dockerfile
        # ---------------------------------------------------------

        docker_content = self._read_file("Dockerfile")

        if docker_content:

            versions = self._extract_docker_python_versions(
                docker_content
            )

            if versions:
                evidence.append(
                    {
                        "source": "Dockerfile",
                        "type": "docker_python_versions",
                        "value": versions,
                    }
                )

        return {
            "evidence": evidence,
            "sources_checked": [
                ".python-version",
                "runtime.txt",
                "pyproject.toml",
                "setup.py",
                "setup.cfg",
                "tox.ini",
                "Dockerfile",
            ],
        }