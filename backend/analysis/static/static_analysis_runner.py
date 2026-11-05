
from pathlib import Path
from typing import Any

from analysis.repository.repository_analyzer import RepositoryAnalyzer
from analysis.static.ast_analyzer import ASTAnalyzer
from analysis.static.issue_detector import IssueDetector


class StaticAnalysisRunner:
    """
    Integrates repository analysis, AST analysis,
    and static migration issue detection.
    """

    def __init__(
        self,
        repository_path: str,
        target_python: str
    ):
        self.repository_path = Path(repository_path).resolve()
        self.target_python = target_python

        self.repository_analyzer = RepositoryAnalyzer(
            str(self.repository_path)
        )

        self.ast_analyzer = ASTAnalyzer()

        self.issue_detector = IssueDetector(
            target_python=target_python
        )

    def analyze(self) -> dict[str, Any]:
        """
        Run static analysis across the entire repository.
        """

        repository_report = self.repository_analyzer.analyze()

        python_files = repository_report["python_files"]

        file_results = []
        all_issues = []
        successful_files = 0
        syntax_error_files = 0
        failed_files = 0

        for relative_path in python_files:

            absolute_path = self.repository_path / relative_path

            try:
                source_code = absolute_path.read_text(
                    encoding="utf-8"
                )

            except (OSError, UnicodeDecodeError) as exc:
                failed_files += 1

                file_results.append({
                    "file": relative_path,
                    "status": "error",
                    "error": str(exc),
                    "ast_analysis": None,
                    "issues": [],
                    "issue_count": 0
                })

                continue

            # AST analysis
            ast_result = self.ast_analyzer.analyze_source(
                source_code=source_code,
                file_path=relative_path
            )

            # Static migration issue detection
            issue_result = self.issue_detector.detect(
                source_code=source_code,
                file_path=relative_path
            )

            if ast_result["status"] == "success":
                successful_files += 1

            elif ast_result["status"] == "syntax_error":
                syntax_error_files += 1

            elif ast_result["status"] == "error":
                failed_files += 1

            issues = issue_result["issues"]

            all_issues.extend(issues)

            file_results.append({
                "file": relative_path,
                "status": ast_result["status"],
                "ast_analysis": ast_result,
                "issues": issues,
                "issue_count": len(issues)
            })

        return {
            "repository_path": str(self.repository_path),
            "target_python": self.target_python,

            "summary": {
                "total_python_files": len(python_files),
                "successfully_analyzed": successful_files,
                "syntax_error_files": syntax_error_files,
                "failed_files": failed_files,
                "total_migration_issues": len(all_issues)
            },

            "repository_analysis": repository_report,

            "file_results": file_results,

            "migration_issues": all_issues
        }
