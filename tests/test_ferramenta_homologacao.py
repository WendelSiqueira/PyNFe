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

    def test_comandos_disponiveis(self):
        self.assertEqual(
            set(homologacao.COMANDOS),
            {"status", "emitir", "notas", "consultar", "cce", "cancelar", "inutilizar", "danfe"},
        )


class RegistroNotasTestCase(unittest.TestCase):
    """Registro local das notas emitidas, usado por consultar/cce/cancelar."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._saida, self._registro = homologacao.SAIDA, homologacao.REGISTRO
        homologacao.SAIDA = self._tmp.name
        homologacao.REGISTRO = os.path.join(self._tmp.name, "notas.json")

    def tearDown(self):
        homologacao.SAIDA, homologacao.REGISTRO = self._saida, self._registro

    def test_sem_notas(self):
        with self.assertRaisesRegex(SystemExit, "Nenhuma nota"):
            homologacao.nota_do_registro()

    def test_ultima_nota_e_busca_por_chave(self):
        homologacao.registrar({"chave": "A", "protocolo": "1"})
        homologacao.registrar({"chave": "B", "protocolo": "2"})
        self.assertEqual(homologacao.nota_do_registro()["chave"], "B")
        self.assertEqual(homologacao.nota_do_registro("A")["protocolo"], "1")
        with self.assertRaisesRegex(SystemExit, "nao esta no registro"):
            homologacao.nota_do_registro("C")

    def test_atualizar_registro(self):
        homologacao.registrar({"chave": "A", "protocolo": "1"})
        homologacao.atualizar_registro("A", situacao="cancelada", cce=2)
        nota = homologacao.nota_do_registro("A")
        self.assertEqual((nota["situacao"], nota["cce"]), ("cancelada", 2))

    def test_proximo_numero_segue_o_registro_por_serie(self):
        homologacao.registrar({"chave": "A", "protocolo": "1", "serie": "1", "numero": "41"})
        homologacao.registrar({"chave": "B", "protocolo": "2", "serie": "1", "numero": "42"})
        homologacao.registrar({"chave": "C", "protocolo": "3", "serie": "2", "numero": "7"})
        self.assertEqual(homologacao.proximo_numero("1"), 43)
        self.assertEqual(homologacao.proximo_numero("2"), 8)

    def test_proximo_numero_sem_registro(self):
        numero = homologacao.proximo_numero("1")
        self.assertTrue(1 <= numero <= 900000)

    def test_pasta_de_saida_privada(self):
        homologacao.registrar({"chave": "A", "protocolo": "1"})
        self.assertEqual(os.stat(self._tmp.name).st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
