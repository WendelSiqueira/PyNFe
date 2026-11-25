"""Atualiza pynotas/data/certificados/icp-brasil.pem a partir do pacote oficial
de certificados das ACs da ICP-Brasil, publicado pelo ITI.

Uso (na raiz do projeto):
    uv run python scripts/atualizar_cadeia_icp_brasil.py

O script baixa o ACcompactado.zip e o hashsha512.txt, confere o SHA-512 do zip,
e grava no .pem os certificados de AC (raizes e intermediarias) dentro da
validade. As intermediarias sao necessarias porque varios servidores da SEFAZ
enviam a cadeia incompleta no TLS.
"""

import datetime
import hashlib
import io
import os
import sys
import urllib.request
import zipfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding

BASE = "https://acraiz.icpbrasil.gov.br/credenciadas/CertificadosAC-ICP-Brasil/"
ZIP = "ACcompactado.zip"
HASH = "hashsha512.txt"
DESTINO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "pynotas",
    "data",
    "certificados",
    "icp-brasil.pem",
)


def baixar(nome):
    with urllib.request.urlopen(BASE + nome, timeout=60) as resposta:
        return resposta.read()


def carregar(raw):
    if b"BEGIN CERTIFICATE" in raw:
        return x509.load_pem_x509_certificate(raw)
    return x509.load_der_x509_certificate(raw)


def eh_ca(cert):
    try:
        return cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    except x509.ExtensionNotFound:
        return False


def main():
    conteudo = baixar(ZIP)
    esperado = baixar(HASH).decode().split()[0].lower()
    obtido = hashlib.sha512(conteudo).hexdigest()
    if obtido != esperado:
        print(f"erro: SHA-512 do {ZIP} nao confere com o {HASH}", file=sys.stderr)
        return 1

    agora = datetime.datetime.now(datetime.timezone.utc)
    certificados, vistos = [], set()
    with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
        for nome in sorted(z.namelist()):
            if not nome.lower().endswith((".crt", ".cer", ".pem")):
                continue
            cert = carregar(z.read(nome))
            impressao = cert.fingerprint(hashes.SHA256())
            if not eh_ca(cert) or cert.not_valid_after_utc < agora or impressao in vistos:
                continue
            vistos.add(impressao)
            certificados.append(cert)

    certificados.sort(key=lambda c: c.subject.rfc4514_string())
    raizes = sum(1 for c in certificados if c.subject == c.issuer)
    linhas = [
        "# Cadeia de certificados das ACs da ICP-Brasil (raizes e intermediarias).",
        f"# Origem: {BASE}{ZIP}",
        f"# SHA-512 do zip: {obtido}",
        f"# Gerado em {agora:%Y-%m-%d} por scripts/atualizar_cadeia_icp_brasil.py",
        f"# {len(certificados)} certificados, {raizes} raizes.",
        "",
    ]
    for cert in certificados:
        linhas.append(f"# {cert.subject.rfc4514_string()}")
        linhas.append(f"# valido ate {cert.not_valid_after_utc:%Y-%m-%d}")
        linhas.append(cert.public_bytes(Encoding.PEM).decode().rstrip("\n"))
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")
    print(
        f"{len(certificados)} certificados ({raizes} raizes) gravados em {os.path.relpath(DESTINO)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
