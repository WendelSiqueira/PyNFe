import os
import tempfile
import unittest

from lxml import etree

from pynotas.processamento.validacao import Validacao
from pynotas.utils.flags import (
    XSD_FOLDER_MDFE,
    XSD_FOLDER_NFE,
    XSD_MDFE,
    XSD_NFE,
    XSD_NFE_PROCESSADA,
)


class CaminhoXsdTestCase(unittest.TestCase):
    """Os XSDs sao encontrados a partir do pacote, qualquer que seja o diretorio
    de trabalho (caso da lib instalada como dependencia de outro projeto)."""

    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_pastas_sao_absolutas(self):
        self.assertTrue(os.path.isabs(XSD_FOLDER_NFE))
        self.assertTrue(os.path.isabs(XSD_FOLDER_MDFE))

    def test_schemas_carregam_fora_da_raiz_do_projeto(self):
        validacao = Validacao()
        for pasta, arquivo in (
            (XSD_FOLDER_NFE, XSD_NFE),
            (XSD_FOLDER_NFE, XSD_NFE_PROCESSADA),
            (XSD_FOLDER_MDFE, XSD_MDFE),
        ):
            caminho = validacao.get_xsd(xsd_file=arquivo, xsd_folder=pasta)
            with self.subTest(arquivo=arquivo):
                self.assertTrue(os.path.isfile(caminho), caminho)
                # Carrega o schema completo, incluindo os XSDs importados
                etree.XMLSchema(etree.parse(caminho))


if __name__ == "__main__":
    unittest.main()
