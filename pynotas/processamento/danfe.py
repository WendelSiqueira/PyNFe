"""Impressao do DANFE (NF-e, modelo 55) e do DANFCE (NFC-e, modelo 65).

Gera o PDF a partir do XML da nota com a brazilfiscalreport, instalada pelo
extra "impressao" (Python 3.10 ou mais novo):

    pip install "pynotas-br[impressao]"

Use o XML autorizado (nfeProc, com o protocolo): so assim o DANFE sai com o
numero e a data da autorizacao.
"""

import os

from lxml import etree

INSTALAR = 'Instale o extra de impressao: pip install "pynotas-br[impressao]" (Python 3.10+)'


def _xml_texto(xml):
    """Aceita elemento lxml, bytes, texto do XML ou caminho do arquivo."""
    if isinstance(xml, etree._Element):
        return etree.tostring(xml, encoding="unicode")
    if isinstance(xml, bytes):
        return xml.decode("utf-8")
    if isinstance(xml, os.PathLike) or not str(xml).lstrip().startswith("<"):
        with open(xml, encoding="utf-8") as f:
            return f.read()
    return xml


def _modelo(texto):
    raiz = etree.fromstring(texto.encode("utf-8"))
    achados = raiz.xpath("//*[local-name()='ide']/*[local-name()='mod']")
    if not achados:
        raise ValueError("XML sem ide/mod: nao parece uma NF-e ou NFC-e")
    return achados[0].text


def gerar_danfe(xml, caminho=None, config=None):
    """Gera o DANFE (modelo 55) ou o DANFCE (modelo 65) em PDF.

    :param xml: nfeProc ou NFe, como elemento lxml, bytes, texto ou caminho do arquivo
    :param caminho: onde gravar o PDF (opcional)
    :param config: DanfeConfig ou DanfceConfig da brazilfiscalreport (opcional).
        Sem config, o DANFE usa o layout vigente na data de emissao da nota
        (o da NT 2026.010, com IBS/CBS, para notas emitidas a partir de 01/12/2026).
    :return: o PDF em bytes
    """
    texto = _xml_texto(xml)
    modelo = _modelo(texto)
    try:
        if modelo == "65":
            from brazilfiscalreport.danfce import Danfce as Documento
        else:
            from brazilfiscalreport.danfe import Danfe as Documento
    except ImportError as erro:
        raise ImportError(INSTALAR) from erro

    pdf = bytes(Documento(xml=texto, config=config).output())
    if caminho:
        with open(caminho, "wb") as f:
            f.write(pdf)
    return pdf
