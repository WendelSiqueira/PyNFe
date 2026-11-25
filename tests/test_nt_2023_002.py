"""Avisos da NT 2023.002: fim da autorizacao assincrona e da inutilizacao em AC, BA e SP."""

import unittest
import warnings
from unittest import mock

from pynotas.processamento.comunicacao import UFS_SEM_INUTILIZACAO, ComunicacaoSefaz
from pynotas.utils import etree

CERTIFICADO = "./tests/certificado.pfx"
SENHA = "123456"


class NT2023002TestCase(unittest.TestCase):
    def _con(self, uf="pr"):
        con = ComunicacaoSefaz(uf, CERTIFICADO, SENHA, homologacao=True)
        resposta = mock.Mock(status_code=500, text="", content=b"")
        con._post = mock.Mock(return_value=resposta)
        return con

    def _avisos(self, funcao):
        with warnings.catch_warnings(record=True) as avisos:
            warnings.simplefilter("always")
            funcao()
        return [str(a.message) for a in avisos if issubclass(a.category, FutureWarning)]

    def test_autorizacao_assincrona_avisa(self):
        con = self._con()
        avisos = self._avisos(lambda: con.autorizacao("nfe", etree.Element("NFe"), ind_sinc=0))
        self.assertTrue(any("assincrona" in a for a in avisos), avisos)

    def test_autorizacao_sincrona_nao_avisa(self):
        con = self._con()
        avisos = self._avisos(lambda: con.autorizacao("nfe", etree.Element("NFe"), ind_sinc=1))
        self.assertEqual(avisos, [])

    def test_consulta_recibo_avisa(self):
        con = self._con()
        avisos = self._avisos(lambda: con.consulta_recibo("nfe", "123"))
        self.assertTrue(any("assincrona" in a for a in avisos), avisos)

    def test_inutilizacao_avisa_nas_ufs_afetadas(self):
        self.assertEqual(UFS_SEM_INUTILIZACAO, ("AC", "BA", "SP"))
        for uf in ("sp", "BA", "ac"):
            con = self._con(uf)
            avisos = self._avisos(
                lambda: con.inutilizacao("nfe", "99999999000199", 1, 2, "Teste de inutilizacao")
            )
            with self.subTest(uf=uf):
                self.assertTrue(any("Inutilizacao desativada" in a for a in avisos), avisos)

    def test_inutilizacao_sem_aviso_nas_demais_ufs(self):
        con = self._con("pr")
        avisos = self._avisos(
            lambda: con.inutilizacao("nfe", "99999999000199", 1, 2, "Teste de inutilizacao")
        )
        self.assertEqual(avisos, [])


if __name__ == "__main__":
    unittest.main()
