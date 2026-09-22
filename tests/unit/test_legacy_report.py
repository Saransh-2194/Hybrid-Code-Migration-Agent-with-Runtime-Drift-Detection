from benchmarks.legacy_report.legacy_report import generate_report 
 


test_cases = [
    (
        [
            {"status": "success"},
            {"status": "error"},
            {"status": "success"},
        ],
        {
            "total": 3,
            "errors": 1,
        },
    ),
    (
        [
            {"status": "success"},
            {"status": "success"},
            {"status": "success"},
        ],
        {
            "total": 3,
            "errors": 0,
        },
    ),
    (
        [
            {"status": "error"},
            {"status": "error"},
        ],
        {
            "total": 2,
            "errors": 2,
        },
    ),
    (
        [],
        {
            "total": 0,
            "errors": 0,
        },
    ),
]


for records, expected in test_cases:
    result = dict(generate_report(records))

    if result["total"] != expected["total"]:
        raise AssertionError(
            f"Expected total={expected['total']}, got {result['total']}"
        )

    if result["errors"] != expected["errors"]:
        raise AssertionError(
            f"Expected errors={expected['errors']}, got {result['errors']}"
        )

print("All test cases produced the required output.")