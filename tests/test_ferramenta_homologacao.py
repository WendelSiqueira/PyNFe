"""Testes da ferramenta scripts/homologacao.py que nao acessam a SEFAZ."""

import importlib.util
import os
import tempfile
import unittest

CAMINHO = os.path.join(os.path.dirname(__file__), "..", "scripts", "homologacao.py")
_spec = importlib.util.spec_from_file_location("homologacao", CAMINHO)
homologacao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(homologacao)


class FerramentaHomologacaoTestCase(unittest.TestCase):
    def test_sempre_homologacao(self):
        self.assertIs(homologacao.HOMOLOGACAO, True)

    def test_crt_do_regime(self):
        self.assertEqual(homologacao.crt_do_regime("SIMPLES NACIONAL - MEI"), "4")
        self.assertEqual(homologacao.crt_do_regime("SIMPLES NACIONAL"), "1")
        self.assertEqual(homologacao.crt_do_regime("NORMAL - REGIME PERIODICO DE APURACAO"), "3")
        self.assertEqual(homologacao.crt_do_regime(None), "3")

    def _config(self, conteudo):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False)
        tmp.write(conteudo)
        tmp.close()
        self.addCleanup(os.remove, tmp.name)
        return tmp.name

    def test_ler_config(self):
        caminho = self._config('# comentario\nPFX_PATH="~/cert.pfx"\nPFX_SENHA=abc=123\nUF=sp\n')
        cfg = homologacao.ler_config(caminho)
        self.assertEqual(cfg["PFX_PATH"], os.path.expanduser("~/cert.pfx"))
        self.assertEqual(cfg["PFX_SENHA"], "abc=123")  # '=' dentro da senha
        self.assertEqual(cfg["UF"], "sp")

    def test_ler_config_sem_senha(self):
        caminho = self._config("PFX_PATH=/tmp/cert.pfx\n")
        with self.assertRaisesRegex(SystemExit, "PFX_SENHA"):
            homologacao.ler_config(caminho)

    def test_parser_sem_opcao_de_producao(self):
        ajuda = homologacao.criar_parser().format_help().lower()
        self.assertNotIn("producao", ajuda)
        self.assertNotIn("--prod", ajuda)


if __name__ == "__main__":
    unittest.main()
