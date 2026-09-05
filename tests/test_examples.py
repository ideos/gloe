"""Keep the documented input/call/result examples executable."""

from pathlib import Path
import subprocess
import sys
from unittest import TestCase


class DocumentationExamples(TestCase):
    def test_published_pipeline_calls_and_results(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "docs.source.examples.pipelines"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
