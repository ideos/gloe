import unittest
from unittest.mock import MagicMock, patch

from tests.lib.transformers import plus1, square_root


class TestTransformerExport(unittest.TestCase):

    @patch("builtins.__import__", side_effect=ImportError)
    def test_import_error(self, mock_import: MagicMock):

        foo = square_root >> plus1

        self.assertRaises(ImportError, lambda: foo.export("foo.dot"))


if __name__ == "__main__":
    unittest.main()
