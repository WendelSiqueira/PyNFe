"""Intermediador da transacao (NT 2020.006): indIntermed e infIntermed."""

import datetime
import unittest
from decimal import Decimal

from pynotas.entidades.cliente import Cliente
from pynotas.entidades.emitente import Emitente
from pynotas.entidades.fonte_dados import _fonte_dados
from pynotas.entidades.notafiscal import NotaFiscal
from pynotas.processamento.assinatura import AssinaturaA1
from pynotas.processamento.serializacao import SerializacaoXML
from pynotas.processamento.validacao import Validacao
from pynotas.utils.flags import CODIGO_BRASIL, NAMESPACE_NFE, XSD_FOLDER_NFE, XSD_NFE

NS = {"ns": NAMESPACE_NFE}
SHOPEE = "35.635.824/0001-12"


class IntermediadorTestCase(unittest.TestCase):
    def _nota(self, presenca, **nota):
        emitente = Emitente(
            razao_social="NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL",
            nome_fantasia="Empresa Teste",
            cnpj="99999999000199",
            codigo_de_regime_tributario="1",
            inscricao_estadual="9999999999",
            cnae_fiscal="9999999",
            endereco_logradouro="Rua da Paz",
            endereco_numero="666",
            endereco_bairro="Sossego",
            endereco_municipio="Paranavaí",
            endereco_uf="PR",
            endereco_cep="87704000",
            endereco_pais=CODIGO_BRASIL,
        )
        cliente = Cliente(
            razao_social="JOSE DA SILVA",
            tipo_documento="CPF",
            numero_documento="12345678900",
            indicador_ie=9,
            endereco_logradouro="Rua dos Bobos",
            endereco_numero="Zero",
            endereco_bairro="Aquele Mesmo",
            endereco_municipio="Brasilia",
            endereco_uf="DF",
            endereco_cep="12345123",
            endereco_pais=CODIGO_BRASIL,
        )
        utc = datetime.timezone.utc
        nf = NotaFiscal(
            emitente=emitente,
            cliente=cliente,
            uf="PR",
            natureza_operacao="VENDA",
            forma_pagamento=0,
            modelo=55,
            serie="1",
            numero_nf="1",
            data_emissao=datetime.datetime(2026, 11, 25, 12, tzinfo=utc),
            data_saida_entrada=datetime.datetime(2026, 11, 25, 13, tzinfo=utc),
            tipo_documento=1,
            municipio="4118402",
            tipo_impressao_danfe=1,
            forma_emissao="1",
            cliente_final=1,
            indicador_destino=2,
            indicador_presencial=presenca,
            finalidade_emissao="1",
            processo_emissao="0",
            transporte_modalidade_frete=9,
            totais_tributos_aproximado=Decimal("0"),
            **nota,
        )
        nf.adicionar_produto_servico(
            codigo="001",
            descricao="Produto",
            ncm="33049990",
            ean="SEM GTIN",
            cfop="6102",
            unidade_comercial="UN",
            quantidade_comercial=Decimal("1"),
            valor_unitario_comercial=Decimal("10.00"),
            valor_total_bruto=Decimal("10.00"),
            unidade_tributavel="UN",
            quantidade_tributavel=Decimal("1"),
            valor_unitario_tributavel=Decimal("10.00"),
            ean_tributavel="SEM GTIN",
            ind_total=1,
            icms_modalidade="102",
            icms_origem=0,
            icms_csosn="102",
            pis_modalidade="99",
            cofins_modalidade="99",
            valor_tributos_aprox="0",
        )
        nf.adicionar_pagamento(t_pag="01", v_pag=10.00, ind_pag=0)

    def _xml(self):
        xml = SerializacaoXML(_fonte_dados, homologacao=True).exportar()
        assinado = AssinaturaA1("./tests/certificado.pfx", b"123456").assinar(xml)
        v = Validacao()
        v.validar_etree(assinado, v.get_xsd(XSD_NFE, XSD_FOLDER_NFE), use_assert=True)
        return assinado

    def _filhos_infnfe(self, xml):
        return [c.tag.split("}")[-1] for c in xml.xpath("//ns:infNFe", namespaces=NS)[0]]

    def test_internet_com_marketplace(self):
        self._nota(
            2,
            indicador_intermediador=1,
            intermediador_cnpj=SHOPEE,
            intermediador_id_cadastro="minhaloja",
        )
        xml = self._xml()
        self.assertEqual(xml.xpath("//ns:ide/ns:indIntermed", namespaces=NS)[0].text, "1")
        self.assertEqual(
            xml.xpath("//ns:infIntermed/ns:CNPJ", namespaces=NS)[0].text, "35635824000112"
        )
        self.assertEqual(
            xml.xpath("//ns:infIntermed/ns:idCadIntTran", namespaces=NS)[0].text, "minhaloja"
        )
        filhos = self._filhos_infnfe(xml)
        self.assertEqual(filhos[filhos.index("pag") + 1], "infIntermed")

    def test_internet_sem_intermediador(self):
        self._nota(2)
        xml = self._xml()
        self.assertEqual(xml.xpath("//ns:ide/ns:indIntermed", namespaces=NS)[0].text, "0")
        self.assertEqual(len(xml.xpath("//ns:infIntermed", namespaces=NS)), 0)

    def test_presencial_sem_intermediador_omite_indicador(self):
        self._nota(1)
        xml = self._xml()
        self.assertEqual(len(xml.xpath("//ns:ide/ns:indIntermed", namespaces=NS)), 0)

    def test_presencial_com_intermediador(self):
        self._nota(
            1,
            indicador_intermediador=1,
            intermediador_cnpj=SHOPEE,
            intermediador_id_cadastro="minhaloja",
        )
        xml = self._xml()
        self.assertEqual(xml.xpath("//ns:ide/ns:indIntermed", namespaces=NS)[0].text, "1")
        self.assertEqual(len(xml.xpath("//ns:infIntermed", namespaces=NS)), 1)

    def test_grupo_incompleto_levanta_erro(self):
        self._nota(2, indicador_intermediador=1, intermediador_cnpj=SHOPEE)
        with self.assertRaisesRegex(ValueError, "infIntermed"):
            self._xml()


if __name__ == "__main__":
    unittest.main()
