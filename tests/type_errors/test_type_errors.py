import textwrap
import unittest
from mypy import api


class TestTypeErrors(unittest.TestCase):
    def _run_mypy(self, code: str) -> str:
        stdout, stderr, status = api.run(["-c", textwrap.dedent(code)])
        self.assertNotEqual(status, 0)
        return stdout + stderr

    def test_noargs_to_tuple_composition_error(self):
        output = self._run_mypy(
            """
            from gloe import transformer

            @transformer
            def randint() -> int:
                return 6

            @transformer
            def sum_tuple2(num: tuple[float, float]) -> float:
                return num[0] + num[1]

            randint >> sum_tuple2
            """
        )

        self.assertIn("Unsupported operand types for >>", output)

    def test_mapover_item_only_error(self):
        output = self._run_mypy(
            """
            from gloe import transformer
            from gloe.collection import MapOver

            @transformer
            def square(num: float) -> float:
                return num * num

            MapOver([1.0, 2.0], square)
            """
        )

        self.assertIn('Argument 2 to "MapOver" has incompatible type', output)

    def test_noargs_called_with_args_error(self):
        output = self._run_mypy(
            """
            from gloe import transformer

            @transformer
            def randint() -> int:
                return 6

            randint(1)
            """
        )

        self.assertIn(
            'Too many arguments for "__call__" of "Transformer"', output
        )
