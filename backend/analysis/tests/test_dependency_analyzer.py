from pathlib import Path

from backend.analysis.repository.dependency_analyzer import (
    DependencyAnalyzer
)


def create_repository(tmp_path: Path):

    repository = tmp_path / "legacy_project"
    repository.mkdir()

    return repository


def test_requirements_file(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "requirements.txt").write_text(
        """
requests==2.20.0
flask>=1.1
numpy
# comment
"""
    )

    analyzer = DependencyAnalyzer(str(repository))

    result = analyzer.analyze()

    dependencies = result["dependencies"]

    assert {
        "package": "requests",
        "constraint": "==2.20.0",
        "source": "requirements.txt"
    } in dependencies

    assert {
        "package": "flask",
        "constraint": ">=1.1",
        "source": "requirements.txt"
    } in dependencies

    assert {
        "package": "numpy",
        "constraint": None,
        "source": "requirements.txt"
    } in dependencies


def test_pyproject_dependencies(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "pyproject.toml").write_text(
        """
[project]

dependencies = [
    "requests>=2.0",
    "flask==2.0.0"
]
"""
    )

    analyzer = DependencyAnalyzer(str(repository))

    result = analyzer.analyze()

    dependencies = result["dependencies"]

    assert {
        "package": "requests",
        "constraint": ">=2.0",
        "source": "pyproject.toml"
    } in dependencies

    assert {
        "package": "flask",
        "constraint": "==2.0.0",
        "source": "pyproject.toml"
    } in dependencies


def test_setup_py_dependencies(tmp_path):

    repository = create_repository(tmp_path)

    (repository / "setup.py").write_text(
        """
from setuptools import setup

setup(
    name="legacy-project",
    install_requires=[
        "requests>=2.0",
        "numpy==1.19.0"
    ]
)
"""
    )

    analyzer = DependencyAnalyzer(str(repository))

    result = analyzer.analyze()

    dependencies = result["dependencies"]

    assert {
        "package": "requests",
        "constraint": ">=2.0",
        "source": "setup.py"
    } in dependencies

    assert {
        "package": "numpy",
        "constraint": "==1.19.0",
        "source": "setup.py"
    } in dependencies


def test_no_dependency_files(tmp_path):

    repository = create_repository(tmp_path)

    analyzer = DependencyAnalyzer(str(repository))

    result = analyzer.analyze()

    assert result["files_found"] == []
    assert result["dependencies"] == []
    assert result["count"] == 0