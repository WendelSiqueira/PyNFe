"""Impressao do DANFE com a brazilfiscalreport (extra "impressao")."""

import os
import sys
import tempfile
import unittest
from unittest import mock

from lxml import etree

from pynotas.processamento import gerar_danfe
from tests import test_nfe_pedido_marketplace as pedido

try:
    import brazilfiscalreport  # noqa: F401

    TEM_IMPRESSAO = True
except ImportError:
    TEM_IMPRESSAO = False


def xml_pedido():
    caso = pedido.PedidoMarketplaceTestCase("test_totais_e_rateio")
    caso._pedido()
    return caso._xml()


@unittest.skipUnless(TEM_IMPRESSAO, "brazilfiscalreport nao instalada (Python 3.10+)")
class DanfeTestCase(unittest.TestCase):
    def setUp(self):
        self.xml = xml_pedido()

    def test_gera_pdf_do_elemento(self):
        pdf = gerar_danfe(self.xml)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_aceita_bytes_texto_e_caminho_e_grava(self):
        texto = etree.tostring(self.xml, encoding="unicode")
        with tempfile.TemporaryDirectory() as pasta:
            origem = os.path.join(pasta, "nfe.xml")
            with open(origem, "w", encoding="utf-8") as f:
                f.write(texto)
            destino = os.path.join(pasta, "danfe.pdf")
            for entrada in (texto.encode("utf-8"), texto, origem):
                pdf = gerar_danfe(entrada, caminho=destino)
                with open(destino, "rb") as f:
                    self.assertEqual(f.read(), pdf)

    def test_nfce_usa_danfce(self):
        nfce = etree.tostring(self.xml, encoding="unicode").replace(
            "<mod>55</mod>", "<mod>65</mod>"
        )
        with mock.patch("brazilfiscalreport.danfce.Danfce") as danfce:
            danfce.return_value.output.return_value = bytearray(b"%PDF-nfce")
            self.assertEqual(gerar_danfe(nfce), b"%PDF-nfce")
        danfce.assert_called_once_with(xml=nfce, config=None)


class DanfeSemDependenciaTestCase(unittest.TestCase):
    def test_xml_sem_modelo(self):
        with self.assertRaisesRegex(ValueError, "ide/mod"):
            gerar_danfe("<nada/>")

    def test_sem_brazilfiscalreport_explica_o_extra(self):
        with mock.patch.dict(sys.modules, {"brazilfiscalreport.danfe": None}):
            with self.assertRaisesRegex(ImportError, r"pynotas-br\[impressao\]"):
                gerar_danfe("<NFe><infNFe><ide><mod>55</mod></ide></infNFe></NFe>")


if __name__ == "__main__":
    unittest.main()
