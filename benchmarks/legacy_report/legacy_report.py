import inspect
import time
from collections import Mapping


class Report(Mapping):

    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


def generate_report(records, include_errors=True):

    start = time.clock()

    result = {
        "total": len(records),
        "errors": 0
    }

    if include_errors:
        result["errors"] = sum(
            1
            for record in records
            if record["status"] == "error"
        )

    elapsed = time.clock() - start

    result["execution_time"] = elapsed

    return Report(result)


def get_report_signature():

    spec = inspect.getargspec(
        generate_report
    )

    return {
        "arguments": spec.args,
        "defaults": spec.defaults
    }