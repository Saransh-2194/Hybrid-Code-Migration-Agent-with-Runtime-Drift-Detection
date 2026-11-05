
from analysis.static.issue_detector import IssueDetector


def test_detect_distutils_python312():
    detector = IssueDetector("3.12")

    source = """
import distutils
"""

    result = detector.detect(source, "legacy.py")

    assert result["issue_count"] == 1
    assert result["issues"][0]["issue_type"] == "removed_module"
    assert result["issues"][0]["line"] == 2


def test_detect_imp_python312():
    detector = IssueDetector("3.12")

    source = """
import imp
"""

    result = detector.detect(source)

    assert result["issue_count"] == 1


def test_detect_collections_mapping_python310():
    detector = IssueDetector("3.10")

    source = """
from collections import Mapping
"""

    result = detector.detect(source)

    assert result["issue_count"] == 1
    assert result["issues"][0]["issue_type"] == "removed_collections_alias"


def test_no_distutils_issue_python311():
    detector = IssueDetector("3.11")

    source = """
import distutils
"""

    result = detector.detect(source)

    assert result["issue_count"] == 0


def test_detect_inspect_getargspec():
    detector = IssueDetector("3.11")

    source = """
import inspect
inspect.getargspec(my_function)
"""

    result = detector.detect(source)

    assert result["issue_count"] == 1
    assert result["issues"][0]["issue_type"] == "removed_api"


def test_syntax_error_detection():
    detector = IssueDetector("3.12")

    source = """
def broken(
"""

    result = detector.detect(source)

    assert result["status"] == "syntax_error"
    assert result["issue_count"] == 1
