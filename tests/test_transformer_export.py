import unittest
from unittest.mock import MagicMock, patch

from gloe.collection import Map
from tests.lib.transformers import plus1, square_root, repeat_list


class TestTransformerExport(unittest.TestCase):

    foo = repeat_list(10) >> Map(plus1)

    def test_import_error(self):
        # instead of foo.dot store it on a temporary file
        # calling the real function, not mocking

        import tempfile

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".dot", delete=False) as temp:
            # Use the name of the temporary file instead of 'foo.dot'
            self.foo.to_dot(temp.name)


if __name__ == "__main__":
    unittest.main()
