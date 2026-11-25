import os
import ssl
import stat
import unittest
import warnings
from unittest import mock

import certifi
import requests

from pynotas.processamento.comunicacao import ComunicacaoSefaz
from pynotas.utils import etree
from pynotas.utils.tls import CAMINHO_CADEIA_ICP_BRASIL, cadeia_padrao, resolver_verificacao

CERTIFICADO = "./tests/certificado.pfx"
SENHA = "123456"


def contar_certificados(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read().count("BEGIN CERTIFICATE")


class CadeiaIcpBrasilTestCase(unittest.TestCase):
    def test_arquivo_icp_brasil_no_pacote(self):
        self.assertTrue(os.path.isfile(CAMINHO_CADEIA_ICP_BRASIL))
        conteudo = open(CAMINHO_CADEIA_ICP_BRASIL, encoding="utf-8").read()
        for versao in ("v5", "v10", "v11", "v12"):
            self.assertIn(f"Autoridade Certificadora Raiz Brasileira {versao}", conteudo)

    def test_arquivo_icp_brasil_carrega_no_ssl(self):
        contexto = ssl.create_default_context(cafile=CAMINHO_CADEIA_ICP_BRASIL)
        self.assertGreater(len(contexto.get_ca_certs()), 0)

    def test_cadeia_padrao_soma_certifi_e_icp_brasil(self):
        caminho = cadeia_padrao()
        self.assertEqual(
            contar_certificados(caminho),
            contar_certificados(certifi.where()) + contar_certificados(CAMINHO_CADEIA_ICP_BRASIL),
        )
        ssl.create_default_context(cafile=caminho)

    def test_cadeia_padrao_em_pasta_privada_e_reaproveitada(self):
        caminho = cadeia_padrao()
        modo = stat.S_IMODE(os.stat(os.path.dirname(caminho)).st_mode)
        self.assertEqual(modo, 0o700)
        self.assertEqual(cadeia_padrao(), caminho)


class ResolverVerificacaoTestCase(unittest.TestCase):
    def test_true_usa_cadeia_padrao(self):
        self.assertEqual(resolver_verificacao(True), cadeia_padrao())

    def test_caminho_proprio(self):
        self.assertEqual(resolver_verificacao("/tmp/minhas-cas.pem"), "/tmp/minhas-cas.pem")

    def test_false_desliga_com_aviso(self):
        with self.assertWarnsRegex(UserWarning, "Verificacao TLS desligada"):
            self.assertIs(resolver_verificacao(False), False)

    def test_tipo_invalido(self):
        with self.assertRaises(TypeError):
            resolver_verificacao(None)


class ComunicacaoVerificaTlsTestCase(unittest.TestCase):
    """As chamadas a SEFAZ passam a verificacao TLS para o requests."""

    def _post(self, **kwargs):
        con = ComunicacaoSefaz("sp", CERTIFICADO, SENHA, homologacao=True, **kwargs)
        with mock.patch("pynotas.processamento.comunicacao.requests.post") as post:
            con._post("https://exemplo.invalid/ws", etree.Element("teste"))
        return post.call_args.kwargs["verify"]

    def test_padrao_verifica_com_cadeia_padrao(self):
        self.assertEqual(self._post(), cadeia_padrao())

    def test_desligado_explicitamente(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.assertIs(self._post(verificar_ssl=False), False)


@unittest.skipUnless(
    os.environ.get("PYNOTAS_TESTES_REDE") == "1",
    "teste de rede: rode com PYNOTAS_TESTES_REDE=1",
)
class RedeSefazTestCase(unittest.TestCase):
    """SEFAZ-SP usa certificado da ICP-Brasil com cadeia incompleta."""

    URL = "https://homologacao.nfe.fazenda.sp.gov.br/ws/nfestatusservico4.asmx"

    def test_sefaz_sp_verifica_com_cadeia_padrao(self):
        try:
            requests.get(self.URL, verify=cadeia_padrao(), timeout=20)
        except requests.exceptions.SSLError as e:
            self.fail(f"verificacao TLS falhou: {e}")
        except requests.exceptions.ConnectionError:
            # Sem certificado de cliente a SEFAZ pode encerrar a conexao depois da
            # verificacao do servidor; o que importa aqui e nao haver SSLError.
            pass

    def test_sefaz_sp_falha_so_com_certifi(self):
        with self.assertRaises(requests.exceptions.SSLError):
            requests.get(self.URL, verify=certifi.where(), timeout=20)


if __name__ == "__main__":
    unittest.main()
