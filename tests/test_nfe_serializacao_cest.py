"""CEST, indEscala e CNPJFab no grupo prod da NF-e."""

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


class CestTestCase(unittest.TestCase):
    def _nota(self, **produto):
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
            indicador_destino=1,
            indicador_presencial=1,
            finalidade_emissao="1",
            processo_emissao="0",
            transporte_modalidade_frete=9,
            totais_tributos_aproximado=Decimal("0"),
        )
        kwargs = dict(
            codigo="001",
            descricao="Produto",
            ncm="33049990",
            ean="SEM GTIN",
            cfop="5102",
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
        kwargs.update(produto)
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", v_pag=10.00, ind_pag=0)
        return nf

    def _xml(self):
        xml = SerializacaoXML(_fonte_dados, homologacao=True).exportar()
        assinado = AssinaturaA1("./tests/certificado.pfx", b"123456").assinar(xml)
        v = Validacao()
        v.validar_etree(assinado, v.get_xsd(XSD_NFE, XSD_FOLDER_NFE), use_assert=True)
        return assinado

    def _filhos_prod(self, xml):
        return [c.tag.split("}")[-1] for c in xml.xpath("//ns:det/ns:prod", namespaces=NS)[0]]

    def test_sem_cest(self):
        self._nota()
        xml = self._xml()
        self.assertNotIn("CEST", self._filhos_prod(xml))

    def test_cest_logo_apos_o_ncm(self):
        self._nota(cest="2003800")
        xml = self._xml()
        filhos = self._filhos_prod(xml)
        self.assertEqual(filhos[filhos.index("NCM") + 1], "CEST")
        self.assertEqual(xml.xpath("//ns:prod/ns:CEST", namespaces=NS)[0].text, "2003800")

    def test_cest_com_pontuacao(self):
        self._nota(cest="20.038.00")
        xml = self._xml()
        self.assertEqual(xml.xpath("//ns:prod/ns:CEST", namespaces=NS)[0].text, "2003800")

    def test_cest_com_escala_e_fabricante(self):
        self._nota(cest="2003800", ind_escala="N", cnpj_fabricante="11.222.333/0001-81")
        xml = self._xml()
        filhos = self._filhos_prod(xml)
        i = filhos.index("CEST")
        self.assertEqual(filhos[i : i + 3], ["CEST", "indEscala", "CNPJFab"])
        self.assertEqual(xml.xpath("//ns:prod/ns:indEscala", namespaces=NS)[0].text, "N")
        self.assertEqual(xml.xpath("//ns:prod/ns:CNPJFab", namespaces=NS)[0].text, "11222333000181")

    def test_escala_sem_cest_levanta_erro(self):
        self._nota(ind_escala="S")
        with self.assertRaisesRegex(ValueError, "junto com o CEST"):
            self._xml()


if __name__ == "__main__":
    unittest.main()
