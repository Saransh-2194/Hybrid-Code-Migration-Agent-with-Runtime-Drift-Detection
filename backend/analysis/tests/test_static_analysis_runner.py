
from pathlib import Path

from analysis.static.static_analysis_runner import StaticAnalysisRunner


def test_static_analysis_runner(tmp_path):

    # Create a sample legacy repository
    repository = tmp_path / "legacy_project"
    repository.mkdir()

    source_file = repository / "legacy.py"

    source_file.write_text(
        """
import distutils

def calculate(a, b):
    return a + b
""",
        encoding="utf-8"
    )

    # Run static analysis
    runner = StaticAnalysisRunner(
        repository_path=str(repository),
        target_python="3.12"
    )

    result = runner.analyze()

    # Validate summary
    assert result["summary"]["total_python_files"] == 1

    assert result["summary"]["successfully_analyzed"] == 1

    assert result["summary"]["total_migration_issues"] == 1

    # Validate AST analysis
    file_result = result["file_results"][0]

    assert file_result["status"] == "success"

    assert len(
        file_result["ast_analysis"]["functions"]
    ) == 1

    # Validate migration issue
    issue = result["migration_issues"][0]

    assert issue["issue_type"] == "removed_module"

    assert issue["file"] == "legacy.py"

    assert issue["line"] == 2
