import unittest
import tempfile

from unittest.mock import MagicMock, patch

from gloe.collection import Map
from tests.lib.transformers import plus1, repeat_list


class TestTransformerExport(unittest.TestCase):

    foo = repeat_list(10) >> Map(plus1 >> repeat_list(10) >> Map(plus1))

    @patch("builtins.__import__", side_effect=ImportError)
    def test_no_graphviz_installed(self, mock_import: MagicMock):
        with self.assertRaises(ImportError):
            with tempfile.NamedTemporaryFile(suffix=".dot", delete=False) as temp:
                self.foo.to_dot(temp.name)

    def test_export_no_errors(self):
        with tempfile.NamedTemporaryFile(suffix=".dot", delete=False) as temp:
            self.foo.to_dot(temp.name, with_edge_labels=False)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            self.foo.to_image(temp.name)

    def test_export_deprecated(self):
        with self.assertWarns(DeprecationWarning):
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".dot", delete=False) as temp:
                self.foo.export(temp.name)


if __name__ == "__main__":
    unittest.main()
