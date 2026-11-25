"""Verificacao TLS dos servidores da SEFAZ.

Varios servidores da SEFAZ usam certificados emitidos por ACs da ICP-Brasil,
que nao estao no pacote de CAs padrao do Python (certifi), e alguns enviam a
cadeia incompleta. Por isso a verificacao usa o certifi somado as ACs da
ICP-Brasil (raizes e intermediarias), distribuidas em
pynotas/data/certificados/icp-brasil.pem.
"""

import atexit
import os
import shutil
import tempfile
import threading
import warnings

import certifi

CAMINHO_CADEIA_ICP_BRASIL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "certificados",
    "icp-brasil.pem",
)

_lock = threading.Lock()
_cadeia_padrao = None


def cadeia_padrao():
    """Caminho de um arquivo com as CAs do certifi e da ICP-Brasil.

    O arquivo e gerado uma vez por processo numa pasta temporaria privada
    (permissao 0700), para que outro usuario da maquina nao consiga trocar o
    conteudo, e e removido ao final do processo.
    """
    global _cadeia_padrao
    with _lock:
        if _cadeia_padrao is None or not os.path.isfile(_cadeia_padrao):
            pasta = tempfile.mkdtemp(prefix="pynotas-ca-")
            atexit.register(shutil.rmtree, pasta, True)
            destino = os.path.join(pasta, "cadeia.pem")
            with open(destino, "wb") as saida:
                for origem in (certifi.where(), CAMINHO_CADEIA_ICP_BRASIL):
                    with open(origem, "rb") as entrada:
                        saida.write(entrada.read().rstrip(b"\n") + b"\n")
            _cadeia_padrao = destino
        return _cadeia_padrao


def resolver_verificacao(verificar_ssl):
    """Converte o parametro verificar_ssl no valor de `verify` do requests.

    - True: cadeia padrao (certifi + ICP-Brasil)
    - str: caminho de um arquivo ou pasta de CAs informado pelo usuario
    - False: sem verificacao (inseguro; emite um aviso)
    """
    if verificar_ssl is True:
        return cadeia_padrao()
    if verificar_ssl is False:
        warnings.warn(
            "Verificacao TLS desligada (verificar_ssl=False): a conexao com a SEFAZ "
            "fica sujeita a interceptacao.",
            stacklevel=3,
        )
        return False
    if isinstance(verificar_ssl, (str, os.PathLike)):
        return os.fspath(verificar_ssl)
    raise TypeError("verificar_ssl deve ser True, False ou o caminho de um arquivo de CAs")
