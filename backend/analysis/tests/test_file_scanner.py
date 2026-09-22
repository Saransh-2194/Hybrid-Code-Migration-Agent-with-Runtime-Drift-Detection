from pathlib import Path

from backend.analysis.repository.file_scanner import FileScanner


def create_sample_repository(tmp_path: Path):

    repository = tmp_path / "sample_repo"
    repository.mkdir()

    # Python source
    (repository / "main.py").write_text(
        "print('hello')"
    )

    (repository / "utils.py").write_text(
        "def add(a, b):\n"
        "    return a + b\n"
    )

    # Tests
    tests = repository / "tests"
    tests.mkdir()

    (tests / "test_utils.py").write_text(
        "def test_add():\n"
        "    assert add(1, 2) == 3\n"
    )

    # Dependency information
    (repository / "requirements.txt").write_text(
        "requests==2.20.0\n"
    )

    # Python version
    (repository / ".python-version").write_text(
        "3.8\n"
    )

    # Ignored directory
    git_directory = repository / ".git"
    git_directory.mkdir()

    (git_directory / "ignored.py").write_text(
        "this_should_not_be_detected = True"
    )

    return repository


def test_scan_repository(tmp_path):

    repository = create_sample_repository(tmp_path)

    scanner = FileScanner(str(repository))

    files = scanner.scan()

    paths = [file["path"] for file in files]

    assert "main.py" in paths
    assert "utils.py" in paths
    assert "tests/test_utils.py" in paths

    assert ".git/ignored.py" not in paths


def test_python_files(tmp_path):

    repository = create_sample_repository(tmp_path)

    scanner = FileScanner(str(repository))

    python_files = scanner.python_files()

    assert "main.py" in python_files
    assert "utils.py" in python_files
    assert "tests/test_utils.py" in python_files


def test_test_files(tmp_path):

    repository = create_sample_repository(tmp_path)

    scanner = FileScanner(str(repository))

    test_files = scanner.test_files()

    assert "tests/test_utils.py" in test_files


def test_dependency_files(tmp_path):

    repository = create_sample_repository(tmp_path)

    scanner = FileScanner(str(repository))

    dependencies = scanner.dependency_files()

    assert "requirements.txt" in dependencies


def test_version_files(tmp_path):

    repository = create_sample_repository(tmp_path)

    scanner = FileScanner(str(repository))

    versions = scanner.version_files()

    assert ".python-version" in versions


def test_summary(tmp_path):

    repository = create_sample_repository(tmp_path)

    scanner = FileScanner(str(repository))

    summary = scanner.summary()

    assert summary["python_files"] == 3
    assert summary["test_files"] == 1
    assert "requirements.txt" in summary["dependency_files"]