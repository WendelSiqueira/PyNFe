"""Pedido realista de marketplace: varios itens, frete e desconto rateados,
volume, cartao, intermediador, interestadual e IBS/CBS com gTribSN.

O mesmo pedido foi autorizado em homologacao na SEFAZ-SP (cStat 100)."""

import datetime
import unittest
from decimal import ROUND_HALF_UP, Decimal

from pynotas.entidades.cliente import Cliente
from pynotas.entidades.emitente import Emitente
from pynotas.entidades.fonte_dados import _fonte_dados
from pynotas.entidades.notafiscal import NotaFiscal
from pynotas.processamento.assinatura import AssinaturaA1
from pynotas.processamento.serializacao import SerializacaoXML
from pynotas.processamento.validacao import Validacao
from pynotas.utils.flags import CODIGO_BRASIL, NAMESPACE_NFE, XSD_FOLDER_NFE, XSD_NFE

NS = {"ns": NAMESPACE_NFE}
C = Decimal("0.01")
ITENS = [
    ("SER30", "SERUM FACIAL 30ML", "33049990", 3, Decimal("12.90"), "2003800"),
    ("BAT01", "BATOM MATTE", "33041000", 2, Decimal("19.99"), ""),
    ("MASC250", "MASCARA CAPILAR 250G", "33059000", 1, Decimal("34.50"), ""),
]
FRETE = Decimal("18.47")
DESCONTO = Decimal("10.00")


def ratear(valor, bases):
    total = sum(bases)
    partes = [(valor * b / total).quantize(C, ROUND_HALF_UP) for b in bases[:-1]]
    partes.append(valor - sum(partes))
    return partes


class PedidoMarketplaceTestCase(unittest.TestCase):
    def _pedido(self, peso_l=Decimal("0.850"), peso_b=Decimal("1.020"), t_band=None):
        emitente = Emitente(
            razao_social="NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL",
            nome_fantasia="Loja Teste",
            cnpj="99999999000199",
            codigo_de_regime_tributario="4",
            inscricao_estadual="9999999999",
            cnae_fiscal="4772500",
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
            numero_documento="12345678909",
            indicador_ie=9,
            endereco_logradouro="Rua de Teste",
            endereco_numero="1",
            endereco_bairro="Centro",
            endereco_municipio="Rio de Janeiro",
            endereco_uf="RJ",
            endereco_cep="20010000",
            endereco_pais=CODIGO_BRASIL,
        )
        utc = datetime.timezone.utc
        nf = NotaFiscal(
            emitente=emitente,
            cliente=cliente,
            uf="PR",
            natureza_operacao="VENDA DE MERCADORIA",
            forma_pagamento=0,
            modelo=55,
            serie="1",
            numero_nf="10",
            data_emissao=datetime.datetime(2026, 11, 25, 12, tzinfo=utc),
            data_saida_entrada=datetime.datetime(2026, 11, 25, 13, tzinfo=utc),
            tipo_documento=1,
            municipio="4118402",
            tipo_impressao_danfe=1,
            forma_emissao="1",
            cliente_final=1,
            indicador_destino=2,
            indicador_presencial=2,
            indicador_intermediador=1,
            intermediador_cnpj="35635824000112",
            intermediador_id_cadastro="lojateste",
            finalidade_emissao="1",
            processo_emissao="0",
            transporte_modalidade_frete=0,
            totais_tributos_aproximado=Decimal("0"),
        )
        totais = [(Decimal(q) * v).quantize(C) for _, _, _, q, v, _ in ITENS]
        self.bases = []
        for (cod, desc, ncm, qtd, unit, cest), total, frete, descv in zip(
            ITENS, totais, ratear(FRETE, totais), ratear(DESCONTO, totais)
        ):
            base = total + frete - descv
            self.bases.append(base)
            v_ibs = (base * Decimal("0.001")).quantize(C, ROUND_HALF_UP)
            v_cbs = (base * Decimal("0.009")).quantize(C, ROUND_HALF_UP)
            nf.adicionar_produto_servico(
                codigo=cod,
                descricao=desc,
                ncm=ncm,
                cest=cest,
                ean="SEM GTIN",
                cfop="6102",
                unidade_comercial="UN",
                quantidade_comercial=Decimal(qtd),
                valor_unitario_comercial=unit,
                valor_total_bruto=total,
                unidade_tributavel="UN",
                quantidade_tributavel=Decimal(qtd),
                valor_unitario_tributavel=unit,
                ean_tributavel="SEM GTIN",
                ind_total=1,
                total_frete=frete,
                desconto=descv,
                icms_modalidade="102",
                icms_origem=0,
                icms_csosn="102",
                pis_modalidade="99",
                cofins_modalidade="99",
                valor_tributos_aprox="0",
                ibscbs_cst="000",
                ibscbs_c_class_trib="000001",
                ibscbs_vbc=base,
                ibscbs_p_ibs_uf=Decimal("0.1000"),
                ibscbs_v_ibs_uf=v_ibs,
                ibscbs_v_ibs=v_ibs,
                ibscbs_p_cbs=Decimal("0.9000"),
                ibscbs_v_cbs=v_cbs,
                ibscbs_p_ibs_sn=Decimal("0.1000"),
                ibscbs_v_ibs_sn=v_ibs,
                ibscbs_p_cbs_sn=Decimal("0.9000"),
                ibscbs_v_cbs_sn=v_cbs,
            )
        nf.adicionar_transporte_volume(
            quantidade=1, especie="CAIXA", peso_liquido=peso_l, peso_bruto=peso_b
        )
        pagamento = dict(t_pag="03", v_pag=float(sum(totais) + FRETE - DESCONTO), ind_pag=0)
        pagamento["tp_integra"] = "2"
        if t_band is not None:
            pagamento["t_band"] = t_band
        nf.adicionar_pagamento(**pagamento)

    def _xml(self):
        xml = SerializacaoXML(_fonte_dados, homologacao=True).exportar()
        assinado = AssinaturaA1("./tests/certificado.pfx", b"123456").assinar(xml)
        v = Validacao()
        v.validar_etree(assinado, v.get_xsd(XSD_NFE, XSD_FOLDER_NFE), use_assert=True)
        return assinado

    def _txt(self, xml, caminho):
        return [e.text for e in xml.xpath(caminho, namespaces=NS)]

    def test_totais_e_rateio(self):
        self._pedido()
        xml = self._xml()
        tot = "//ns:total/ns:ICMSTot/ns:"
        self.assertEqual(self._txt(xml, tot + "vProd"), ["113.18"])
        self.assertEqual(self._txt(xml, tot + "vFrete"), ["18.47"])
        self.assertEqual(self._txt(xml, tot + "vDesc"), ["10.00"])
        self.assertEqual(self._txt(xml, tot + "vNF"), ["121.65"])
        # Soma do frete e do desconto dos itens igual aos totais (rateio fecha no centavo)
        self.assertEqual(
            sum(Decimal(v) for v in self._txt(xml, "//ns:det/ns:prod/ns:vFrete")), FRETE
        )
        self.assertEqual(
            sum(Decimal(v) for v in self._txt(xml, "//ns:det/ns:prod/ns:vDesc")), DESCONTO
        )
        self.assertEqual(self._txt(xml, "//ns:pag/ns:detPag/ns:vPag"), ["121.65"])
        self.assertEqual(self._txt(xml, "//ns:IBSCBSTot/ns:vBCIBSCBS"), [str(sum(self.bases))])

    def test_cest_so_no_item_que_tem(self):
        self._pedido()
        xml = self._xml()
        self.assertEqual(self._txt(xml, "//ns:det/ns:prod/ns:CEST"), ["2003800"])

    def test_pesos_com_tres_casas(self):
        self._pedido(peso_l=Decimal("0.85"), peso_b=1)
        xml = self._xml()
        self.assertEqual(self._txt(xml, "//ns:transp/ns:vol/ns:pesoL"), ["0.850"])
        self.assertEqual(self._txt(xml, "//ns:transp/ns:vol/ns:pesoB"), ["1.000"])

    def test_cartao_sem_bandeira(self):
        self._pedido()
        xml = self._xml()
        self.assertEqual(self._txt(xml, "//ns:detPag/ns:card/ns:tpIntegra"), ["2"])
        self.assertEqual(self._txt(xml, "//ns:detPag/ns:card/ns:tBand"), [])

    def test_cartao_com_bandeira_dois_digitos(self):
        self._pedido(t_band=2)
        xml = self._xml()
        self.assertEqual(self._txt(xml, "//ns:detPag/ns:card/ns:tBand"), ["02"])


if __name__ == "__main__":
    unittest.main()
