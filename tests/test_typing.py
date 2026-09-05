"""Run the checked-in typing contract against the pinned mypy release."""

from __future__ import annotations

import os
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINNED_MYPY_PYTHON = Path(os.environ.get("GLOE_MYPY_PYTHON", sys.executable))
ERROR_LINE = re.compile(
    r"(?P<file>[^:\n]+):(?P<line>[0-9]+): error: (?P<message>[^\n]+)"
)


class TypingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PINNED_MYPY_PYTHON.exists():
            raise AssertionError(
                f"mypy interpreter is unavailable: {PINNED_MYPY_PYTHON}; "
                "install the project's .[types] extra"
            )
        version = subprocess.run(
            [str(PINNED_MYPY_PYTHON), "-m", "mypy", "--version"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if version.returncode != 0 or version.stdout.split()[1:2] != ["2.3.1"]:
            raise AssertionError(
                "typing contract requires released mypy 2.3.1; "
                f"got {version.stdout.strip()} {version.stderr.strip()}"
            )

    def _run_mypy(
        self,
        paths: list[Path],
        *,
        config: Path,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="gloe-mypy-") as cache_dir:
            return subprocess.run(
                [
                    str(PINNED_MYPY_PYTHON),
                    "-m",
                    "mypy",
                    "--config-file",
                    str(config),
                    "--cache-dir",
                    cache_dir,
                    "--no-incremental",
                    *[str(path) for path in paths],
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    @staticmethod
    def _errors(output: str, filename: Path) -> dict[int, list[str]]:
        expected_names = {
            str(filename),
            str(filename.relative_to(ROOT)),
            filename.name,
        }
        matches = list(ERROR_LINE.finditer(output))
        unexpected = [
            match.group(0)
            for match in matches
            if match.group("file") not in expected_names
        ]
        if unexpected:
            raise AssertionError(
                f"Unexpected diagnostics outside fixture: {unexpected}"
            )
        errors: dict[int, list[str]] = {}
        for match in matches:
            errors.setdefault(int(match.group("line")), []).append(
                match.group("message")
            )
        return {line: sorted(messages) for line, messages in errors.items()}

    @staticmethod
    def _expected_errors(filename: Path) -> dict[int, list[str]]:
        manifest = json.loads((ROOT / "tests/typing/diagnostics.json").read_text())
        cases = manifest[filename.name]
        expected = {}
        seen = set()
        for number, line in enumerate(filename.read_text().splitlines(), 1):
            if "# reject:" in line:
                case = line.split("# reject:", 1)[1].strip()
                if not case or case in seen or case not in cases:
                    raise AssertionError(f"Missing/duplicate diagnostic case: {case}")
                seen.add(case)
                if not cases[case]:
                    raise AssertionError(f"No expected diagnostic for {case}")
                expected[number] = sorted(cases[case])
        if seen != cases.keys():
            raise AssertionError(f"Stale diagnostic cases: {cases.keys() - seen}")
        return expected

    def test_positive_contract_and_consumer_scenarios(self) -> None:
        paths = [
            *sorted((ROOT / "tests/typing").glob("positive*.py")),
            ROOT / "tests/typing/workflows.py",
            ROOT / "tests/scenarios.py",
            ROOT / "docs/source/examples/pipelines.py",
        ]
        result = self._run_mypy(paths, config=ROOT / "mypy.ini")
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr,
        )

    def test_negative_contract_reports_intended_diagnostics(self) -> None:
        negatives = sorted((ROOT / "tests/typing").glob("negative*.py"))
        self.assertTrue(negatives)
        for negative in negatives:
            with self.subTest(negative=negative.name):
                result = self._run_mypy([negative], config=ROOT / "mypy.ini")
                actual = self._errors(result.stdout + result.stderr, negative)
                expected = self._expected_errors(negative)
                self.assertEqual(
                    actual,
                    expected,
                    msg=(
                        f"{negative.name}: expected diagnostics at {sorted(expected)}, "
                        f"got {sorted(actual)}\n{result.stdout}{result.stderr}"
                    ),
                )
                self.assertEqual(result.returncode, 1)

    def test_composition_fails_closed_without_plugin(self) -> None:
        missing = ROOT / "tests/typing/plugin_missing.py"
        with tempfile.TemporaryDirectory(prefix="gloe-mypy-config-") as directory:
            config = Path(directory) / "mypy.ini"
            config.write_text(
                "[mypy]\n"
                "strict = True\n"
                "python_version = 3.12\n"
                "ignore_missing_imports = True\n"
            )
            result = self._run_mypy([missing], config=config)
        actual = self._errors(result.stdout + result.stderr, missing)
        expected = self._expected_errors(missing)
        self.assertEqual(
            actual,
            expected,
            msg=f"{result.stdout}{result.stderr}",
        )
        self.assertEqual(result.returncode, 1)

    def test_incremental_cache_preserves_types_and_rechecks_changed_dependencies(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="gloe-incremental-") as directory:
            project = Path(directory)
            stage = project / "application_stage.py"
            application = project / "application.py"
            stage.write_text("def parse(value: str) -> int:\n    return int(value)\n")
            application.write_text(
                "import gloe\n"
                "from application_stage import parse\n"
                "def increment(value: int) -> int:\n    return value + 1\n"
                "pipe = gloe.input() >> parse >> increment\n"
            )
            command = [
                str(PINNED_MYPY_PYTHON),
                "-m",
                "mypy",
                "--config-file",
                str(ROOT / "mypy.ini"),
                "--cache-dir",
                str(project / "cache"),
                str(application),
                *map(str, sorted((ROOT / "tests/typing").glob("positive*.py"))),
            ]
            for state in ("cold", "warm"):
                with self.subTest(state=state):
                    result = subprocess.run(
                        command, cwd=ROOT, capture_output=True, text=True
                    )
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )
            stage.write_text(
                "def parse(value: str) -> str:\n    return value.strip()\n"
            )
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(
                'application.py:5: error: Argument 1 to "increment" has incompatible '
                'type "str"; expected "int"  [arg-type]',
                result.stdout,
            )
