# -*- coding: utf-8 -*-
import re
from pynotas.utils import etree


class RetornoSoap(object):
    def __init__(self, webservice, retorno, resposta):
        self.webservice = webservice
        self.resposta = resposta
        self.retorno = retorno


def analisar_retorno(webservice, retorno, classe_resposta):
    match = re.search("<soap:Body>(.*?)</soap:Body>", retorno.text)

    if match:
        resultado = etree.tostring(etree.fromstring(match.group(1))[0])
        resposta = resultado

    return RetornoSoap(webservice, retorno, resposta)
