import os
import re
import inspect
import unittest
from pathlib import Path

from mypy import api


class MypyTestSuite(unittest.TestCase):
    mypy_result: str

    @classmethod
    def setUpClass(cls):
        class_file_path = Path(inspect.getfile(cls))
        file_path = Path(os.path.abspath(__file__))
        config_path = (file_path.parent.parent.parent / "mypy.ini").absolute()
        result = api.run(
            [
                str(class_file_path),
                f"--config-file={config_path}",
            ]
        )
        cls.mypy_result = result[0]

    def setUp(self):
        if "Success" in self.mypy_result:
            return

        test_case = self._testMethodName
        lines, start_line = inspect.getsourcelines(getattr(self.__class__, test_case))
        end_line = start_line + len(lines) - 1

        errors = self.mypy_result.split("\n")[:-2]
        for error in errors:
            matches = re.findall(r"^[a-z/_]+\.py:(\d+): error: (.+)", error)
            line_number, error = matches[0]
            if start_line <= int(line_number) <= end_line:
                mypy_error = re.sub(r" \[assert-type\]$", "", error)
                raise AssertionError(mypy_error)
