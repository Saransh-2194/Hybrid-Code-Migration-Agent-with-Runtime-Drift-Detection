from pathlib import Path

from backend.analysis.repository.version_detector import (
    PythonVersionDetector
)


def create_repository(tmp_path: Path):

    repository = tmp_path / "legacy_project"

    repository.mkdir()

    return repository


def test_python_version_file(tmp_path):

    repository = create_repository(tmp_path)

    (repository / ".python-version").write_text(
        "3.8\n"
    )

    detector = PythonVersionDetector(str(repository))

    result = detector.detect()

    evidence = result["evidence"]

    assert {
        "source": ".python-version",
        "type": "explicit_version",
        "value": "3.8"
    } in evidence


def test_pyproject_requires_python(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "pyproject.toml").write_text(
        """
[project]
requires-python = ">=3.8,<3.12"
"""
    )

    detector = PythonVersionDetector(str(repository))

    result = detector.detect()

    evidence = result["evidence"]

    assert {
        "source": "pyproject.toml",
        "type": "requires_python",
        "value": ">=3.8,<3.12"
    } in evidence


def test_setup_python_requires(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "setup.py").write_text(
        """
from setuptools import setup

setup(
    name="legacy-project",
    python_requires=">=3.7,<3.11"
)
"""
    )

    detector = PythonVersionDetector(str(repository))

    result = detector.detect()

    evidence = result["evidence"]

    assert {
        "source": "setup.py",
        "type": "python_requires",
        "value": ">=3.7,<3.11"
    } in evidence


def test_tox_versions(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "tox.ini").write_text(
        """
[tox]
envlist = py38,py39,py310
"""
    )

    detector = PythonVersionDetector(str(repository))

    result = detector.detect()

    evidence = result["evidence"]

    tox_evidence = next(
        item
        for item in evidence
        if item["source"] == "tox.ini"
    )

    assert "3.8" in tox_evidence["value"]
    assert "3.9" in tox_evidence["value"]
    assert "3.10" in tox_evidence["value"]


def test_docker_python_version(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "Dockerfile").write_text(
        """
FROM python:3.8-slim

WORKDIR /app
"""
    )

    detector = PythonVersionDetector(str(repository))

    result = detector.detect()

    evidence = result["evidence"]

    assert {
        "source": "Dockerfile",
        "type": "docker_python_versions",
        "value": ["3.8"]
    } in evidence