import unittest
from importlib.metadata import version

import pynotas


class VersaoTestCase(unittest.TestCase):
    """A versao do pacote instalado e a usada no verProc da nota sao a mesma."""

    def test_versao_do_pacote_igual_a_do_codigo(self):
        self.assertEqual(version("pynotas-br"), pynotas.__version__)

    def test_get_version(self):
        self.assertEqual(pynotas.get_version(), pynotas.__version__)


if __name__ == "__main__":
    unittest.main()
