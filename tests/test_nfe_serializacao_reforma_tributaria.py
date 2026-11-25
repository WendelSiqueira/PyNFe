"""Tests for Reforma Tributaria IBS/CBS serialization (NT 2025.002-RTC).

Note: IS (Imposto Seletivo) is not yet in the SEFAZ schema (starts 2027).
IS entity fields are preserved for future use but not serialized to XML.
"""

import datetime
import unittest
from decimal import Decimal

from pynotas.entidades.cliente import Cliente
from pynotas.entidades.emitente import Emitente
from pynotas.entidades.notafiscal import NotaFiscal
from pynotas.entidades.fonte_dados import _fonte_dados
from pynotas.processamento.assinatura import AssinaturaA1
from pynotas.processamento.serializacao import SerializacaoXML
from pynotas.processamento.validacao import Validacao
from pynotas.utils.flags import CODIGO_BRASIL, NAMESPACE_NFE, XSD_FOLDER_NFE, XSD_NFE


class ReformaTributariaSerializacaoTestCase(unittest.TestCase):
    """Tests for IBSCBS (Reforma Tributaria) XML serialization per NT 2025.002-RTC."""

    def setUp(self):
        self.certificado = "./tests/certificado.pfx"
        self.senha = bytes("123456", "utf-8")
        self.uf = "pr"
        self.homologacao = True
        self.ns = {"ns": NAMESPACE_NFE}

    def _emitente(self):
        return Emitente(
            razao_social="NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL",
            nome_fantasia="Empresa Teste",
            cnpj="99999999000199",
            codigo_de_regime_tributario="3",
            inscricao_estadual="9999999999",
            inscricao_municipal="12345",
            cnae_fiscal="9999999",
            endereco_logradouro="Rua da Paz",
            endereco_numero="666",
            endereco_bairro="Sossego",
            endereco_municipio="Paranavaí",
            endereco_uf="PR",
            endereco_cep="87704000",
            endereco_pais=CODIGO_BRASIL,
        )

    def _cliente(self):
        return Cliente(
            razao_social="JOSE DA SILVA",
            tipo_documento="CPF",
            email="email@email.com",
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

    def _nota_fiscal(self, emitente, cliente):
        utc = datetime.timezone.utc
        return NotaFiscal(
            emitente=emitente,
            cliente=cliente,
            uf="PR",
            natureza_operacao="VENDA",
            forma_pagamento=0,
            modelo=55,
            serie="1",
            numero_nf="111",
            data_emissao=datetime.datetime(2026, 1, 15, 12, 0, 0, tzinfo=utc),
            data_saida_entrada=datetime.datetime(2026, 1, 15, 13, 0, 0, tzinfo=utc),
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
            informacoes_adicionais_interesse_fisco="Reforma Tributaria teste",
            totais_tributos_aproximado=Decimal("0.00"),
        )

    def _base_product_kwargs(self):
        """Common product kwargs without reforma tributaria fields."""
        return dict(
            codigo="001",
            descricao="Produto teste reforma tributaria",
            ncm="99999999",
            ean="SEM GTIN",
            cfop="5102",
            unidade_comercial="UN",
            quantidade_comercial=Decimal("10"),
            valor_unitario_comercial=Decimal("100.00"),
            valor_total_bruto=Decimal("1000.00"),
            unidade_tributavel="UN",
            quantidade_tributavel=Decimal("10"),
            valor_unitario_tributavel=Decimal("100.00"),
            ean_tributavel="SEM GTIN",
            ind_total=1,
            icms_modalidade="00",
            icms_origem=0,
            icms_csosn="",
            pis_modalidade="99",
            cofins_modalidade="99",
            pis_valor_base_calculo=Decimal("0.00"),
            pis_aliquota_percentual=Decimal("0.00"),
            pis_valor=Decimal("0.00"),
            cofins_valor_base_calculo=Decimal("0.00"),
            cofins_aliquota_percentual=Decimal("0.00"),
            cofins_valor=Decimal("0.00"),
            valor_tributos_aprox="0",
        )

    def _serializar_e_assinar(self):
        serializador = SerializacaoXML(_fonte_dados, homologacao=self.homologacao)
        xml = serializador.exportar()
        a1 = AssinaturaA1(self.certificado, self.senha)
        assinado = a1.assinar(xml)
        # Todo XML gerado com IBS/CBS precisa validar contra o schema oficial (PL_010h)
        validacao = Validacao()
        validacao.validar_etree(
            xml_doc=assinado,
            xsd_file=validacao.get_xsd(xsd_file=XSD_NFE, xsd_folder=XSD_FOLDER_NFE),
            use_assert=True,
        )
        return assinado

    # ------------------------------------------------------------------
    # Test 1: CST 000 — full regular taxation with IBS UF/Mun split
    # ------------------------------------------------------------------
    def test_cst000_ibscbs_tributacao_integral(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        kwargs = self._base_product_kwargs()
        kwargs.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("1.00"),
            ibscbs_p_ibs_mun=Decimal("0.0000"),
            ibscbs_v_ibs_mun=Decimal("0.00"),
            ibscbs_v_ibs=Decimal("1.00"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("9.00"),
        )
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # <IBSCBS> is direct child of <imposto> (no impostoMisto wrapper)
        ibscbs = xml.xpath("//ns:det/ns:imposto/ns:IBSCBS", namespaces=self.ns)
        self.assertEqual(len(ibscbs), 1)

        # No impostoMisto wrapper
        imposto_misto = xml.xpath("//ns:det/ns:imposto/ns:impostoMisto", namespaces=self.ns)
        self.assertEqual(len(imposto_misto), 0)

        # CST is 3-digit
        cst = xml.xpath("//ns:IBSCBS/ns:CST", namespaces=self.ns)[0].text
        self.assertEqual(cst, "000")

        # cClassTrib present
        cclass = xml.xpath("//ns:IBSCBS/ns:cClassTrib", namespaces=self.ns)[0].text
        self.assertEqual(cclass, "000001")

        # Shared vBC at gIBSCBS level
        vbc = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:vBC", namespaces=self.ns)[0].text
        self.assertEqual(vbc, "1000.00")

        # gIBSUF
        p_ibs_uf = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:gIBSUF/ns:pIBSUF", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(p_ibs_uf, "0.1000")
        v_ibs_uf = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:gIBSUF/ns:vIBSUF", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(v_ibs_uf, "1.00")

        # gIBSMun
        p_ibs_mun = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:gIBSMun/ns:pIBSMun", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(p_ibs_mun, "0.0000")
        v_ibs_mun = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:gIBSMun/ns:vIBSMun", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(v_ibs_mun, "0.00")

        # vIBS total
        v_ibs = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:vIBS", namespaces=self.ns)[0].text
        self.assertEqual(v_ibs, "1.00")

        # gCBS
        p_cbs = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:gCBS/ns:pCBS", namespaces=self.ns)[0].text
        self.assertEqual(p_cbs, "0.9000")
        v_cbs = xml.xpath("//ns:IBSCBS/ns:gIBSCBS/ns:gCBS/ns:vCBS", namespaces=self.ns)[0].text
        self.assertEqual(v_cbs, "9.00")

        # IS NOT emitted in XML (schema not ready until 2027)
        is_tag = xml.xpath("//ns:det/ns:imposto/ns:IS", namespaces=self.ns)
        self.assertEqual(len(is_tag), 0)

    # ------------------------------------------------------------------
    # Test 2: CST 222 — isenção (no vBC, values zero)
    # ------------------------------------------------------------------
    def test_cst222_isencao_sem_valores(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        kwargs = self._base_product_kwargs()
        kwargs.update(
            codigo="002",
            descricao="Produto isento reforma tributaria",
            quantidade_comercial=Decimal("1"),
            valor_unitario_comercial=Decimal("50.00"),
            valor_total_bruto=Decimal("50.00"),
            quantidade_tributavel=Decimal("1"),
            valor_unitario_tributavel=Decimal("50.00"),
            ibscbs_cst="222",
            ibscbs_c_class_trib="000002",
        )
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=50.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # IBSCBS present even if exempt
        ibscbs = xml.xpath("//ns:det/ns:imposto/ns:IBSCBS", namespaces=self.ns)
        self.assertEqual(len(ibscbs), 1)

        # CST present
        cst = xml.xpath("//ns:IBSCBS/ns:CST", namespaces=self.ns)[0].text
        self.assertEqual(cst, "222")

        # cClassTrib present
        cclass = xml.xpath("//ns:IBSCBS/ns:cClassTrib", namespaces=self.ns)[0].text
        self.assertEqual(cclass, "000002")

        # No gIBSCBS group (CST 222 is not in taxable CSTs)
        gibscbs = xml.xpath("//ns:IBSCBS/ns:gIBSCBS", namespaces=self.ns)
        self.assertEqual(len(gibscbs), 0)

        # No IS group
        is_group = xml.xpath("//ns:det/ns:imposto/ns:IS", namespaces=self.ns)
        self.assertEqual(len(is_group), 0)

    # ------------------------------------------------------------------
    # Test 3: No reforma data — IBSCBS not emitted
    # ------------------------------------------------------------------
    def test_sem_reforma_tributaria_sem_ibscbs(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        nf.adicionar_produto_servico(
            codigo="003",
            descricao="Produto sem reforma",
            ncm="99999999",
            ean="SEM GTIN",
            cfop="5102",
            unidade_comercial="UN",
            quantidade_comercial=Decimal("1"),
            valor_unitario_comercial=Decimal("100.00"),
            valor_total_bruto=Decimal("100.00"),
            unidade_tributavel="UN",
            quantidade_tributavel=Decimal("1"),
            valor_unitario_tributavel=Decimal("100.00"),
            ean_tributavel="SEM GTIN",
            ind_total=1,
            icms_modalidade="00",
            icms_origem=0,
            icms_csosn="",
            pis_modalidade="51",
            cofins_modalidade="51",
            pis_valor_base_calculo=Decimal("100.00"),
            pis_aliquota_percentual=Decimal("0.65"),
            pis_valor=Decimal("0.65"),
            cofins_valor_base_calculo=Decimal("100.00"),
            cofins_aliquota_percentual=Decimal("3.00"),
            cofins_valor=Decimal("3.00"),
            valor_tributos_aprox="0",
        )

        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=100.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # IBSCBS should NOT exist
        ibscbs = xml.xpath("//ns:det/ns:imposto/ns:IBSCBS", namespaces=self.ns)
        self.assertEqual(len(ibscbs), 0)

        # No impostoMisto either
        imposto_misto = xml.xpath("//ns:det/ns:imposto/ns:impostoMisto", namespaces=self.ns)
        self.assertEqual(len(imposto_misto), 0)

        # No IBSCBSTot
        ibscbs_tot = xml.xpath("//ns:total/ns:IBSCBSTot", namespaces=self.ns)
        self.assertEqual(len(ibscbs_tot), 0)

    # ------------------------------------------------------------------
    # Test 4: Multiple products — totals accumulation with split IBS
    # ------------------------------------------------------------------
    def test_totais_acumulacao_multiplos_produtos(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        base = self._base_product_kwargs()

        # Product 1: vBC=1000, IBS UF=1.00, IBS Mun=0.50, IBS=1.50, CBS=9.00
        p1 = dict(base)
        p1.update(
            codigo="004",
            descricao="Produto 1 reforma",
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("1.00"),
            ibscbs_p_ibs_mun=Decimal("0.0500"),
            ibscbs_v_ibs_mun=Decimal("0.50"),
            ibscbs_v_ibs=Decimal("1.50"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("9.00"),
        )
        nf.adicionar_produto_servico(**p1)

        # Product 2: vBC=500, IBS UF=0.50, IBS Mun=0.25, IBS=0.75, CBS=4.50
        p2 = dict(base)
        p2.update(
            codigo="005",
            descricao="Produto 2 reforma",
            quantidade_comercial=Decimal("5"),
            valor_unitario_comercial=Decimal("100.00"),
            valor_total_bruto=Decimal("500.00"),
            quantidade_tributavel=Decimal("5"),
            valor_unitario_tributavel=Decimal("100.00"),
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("500.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("0.50"),
            ibscbs_p_ibs_mun=Decimal("0.0500"),
            ibscbs_v_ibs_mun=Decimal("0.25"),
            ibscbs_v_ibs=Decimal("0.75"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("4.50"),
        )
        nf.adicionar_produto_servico(**p2)

        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1500.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # Totals in IBSCBSTot (NOT ICMSTot)
        ibscbs_tot = xml.xpath("//ns:total/ns:IBSCBSTot", namespaces=self.ns)
        self.assertEqual(len(ibscbs_tot), 1)

        # vBCIBSCBS = sum of all ibscbs_vbc = 1000 + 500 = 1500
        v_bc = xml.xpath("//ns:IBSCBSTot/ns:vBCIBSCBS", namespaces=self.ns)[0].text
        self.assertEqual(v_bc, "1500.00")

        # Accumulated: IBS UF=1.50, IBS Mun=0.75, IBS=2.25, CBS=13.50
        v_ibs_uf = xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:gIBSUF/ns:vIBSUF", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(v_ibs_uf, "1.50")

        v_ibs_mun = xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:gIBSMun/ns:vIBSMun", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(v_ibs_mun, "0.75")

        v_ibs = xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:vIBS", namespaces=self.ns)[0].text
        self.assertEqual(v_ibs, "2.25")

        v_cbs = xml.xpath("//ns:IBSCBSTot/ns:gCBS/ns:vCBS", namespaces=self.ns)[0].text
        self.assertEqual(v_cbs, "13.50")

    # ------------------------------------------------------------------
    # Test 5: Mixed legacy (ICMS/PIS/COFINS) + reform (IBSCBS) coexistence
    # ------------------------------------------------------------------
    def test_misto_legacy_icms_pis_cofins_com_ibscbs(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        nf.adicionar_produto_servico(
            codigo="006",
            descricao="Produto misto legado e reforma",
            ncm="99999999",
            ean="SEM GTIN",
            cfop="5102",
            unidade_comercial="UN",
            quantidade_comercial=Decimal("1"),
            valor_unitario_comercial=Decimal("200.00"),
            valor_total_bruto=Decimal("200.00"),
            unidade_tributavel="UN",
            quantidade_tributavel=Decimal("1"),
            valor_unitario_tributavel=Decimal("200.00"),
            ean_tributavel="SEM GTIN",
            ind_total=1,
            # Legacy ICMS
            icms_modalidade="00",
            icms_origem=0,
            icms_csosn="",
            icms_valor_base_calculo=Decimal("200.00"),
            icms_aliquota=Decimal("18.00"),
            icms_valor=Decimal("36.00"),
            # Legacy PIS
            pis_modalidade="01",
            pis_valor_base_calculo=Decimal("200.00"),
            pis_aliquota_percentual=Decimal("1.65"),
            pis_valor=Decimal("3.30"),
            # Legacy COFINS
            cofins_modalidade="01",
            cofins_valor_base_calculo=Decimal("200.00"),
            cofins_aliquota_percentual=Decimal("7.60"),
            cofins_valor=Decimal("15.20"),
            valor_tributos_aprox="0",
            # Reform IBSCBS (coexisting during transition)
            ibscbs_cst="010",
            ibscbs_c_class_trib="000003",
            ibscbs_vbc=Decimal("200.00"),
            ibscbs_p_ibs_uf=Decimal("4.4250"),
            ibscbs_v_ibs_uf=Decimal("8.85"),
            ibscbs_p_ibs_mun=Decimal("4.4250"),
            ibscbs_v_ibs_mun=Decimal("8.85"),
            ibscbs_v_ibs=Decimal("17.70"),
            ibscbs_p_cbs=Decimal("4.4000"),
            ibscbs_v_cbs=Decimal("8.80"),
        )

        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=200.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # Legacy ICMS still present
        icms_cst = xml.xpath("//ns:det/ns:imposto/ns:ICMS/ns:ICMS00/ns:CST", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(icms_cst, "00")

        # Legacy PIS still present
        pis_cst = xml.xpath("//ns:det/ns:imposto/ns:PIS/ns:PISAliq/ns:CST", namespaces=self.ns)[
            0
        ].text
        self.assertEqual(pis_cst, "01")

        # Legacy COFINS still present
        cofins_cst = xml.xpath(
            "//ns:det/ns:imposto/ns:COFINS/ns:COFINSAliq/ns:CST", namespaces=self.ns
        )[0].text
        self.assertEqual(cofins_cst, "01")

        # Reform IBSCBS also present (as direct child of imposto)
        ibscbs = xml.xpath("//ns:det/ns:imposto/ns:IBSCBS", namespaces=self.ns)
        self.assertEqual(len(ibscbs), 1)

        cst = xml.xpath("//ns:IBSCBS/ns:CST", namespaces=self.ns)[0].text
        self.assertEqual(cst, "010")

        # No IS in XML
        is_group = xml.xpath("//ns:det/ns:imposto/ns:IS", namespaces=self.ns)
        self.assertEqual(len(is_group), 0)

    # ------------------------------------------------------------------
    # Test 6: vNF does NOT include IBS/CBS (prohibited in 2025-2026)
    # ------------------------------------------------------------------
    def test_vnf_nao_inclui_ibs_cbs(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        kwargs = self._base_product_kwargs()
        kwargs.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("1.00"),
            ibscbs_p_ibs_mun=Decimal("0.0000"),
            ibscbs_v_ibs_mun=Decimal("0.00"),
            ibscbs_v_ibs=Decimal("1.00"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("9.00"),
        )
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # vNF should be 1000.00 (product value only, NO IBS/CBS)
        vnf = xml.xpath("//ns:total/ns:ICMSTot/ns:vNF", namespaces=self.ns)[0].text
        self.assertEqual(vnf, "1000.00")

        # IBS/CBS totals should NOT be inside ICMSTot
        vcbs_in_icmstot = xml.xpath("//ns:ICMSTot/ns:vCBS", namespaces=self.ns)
        self.assertEqual(len(vcbs_in_icmstot), 0)
        vibs_in_icmstot = xml.xpath("//ns:ICMSTot/ns:vIBS", namespaces=self.ns)
        self.assertEqual(len(vibs_in_icmstot), 0)

    # ------------------------------------------------------------------
    # Test 7: Totals in IBSCBSTot, NOT in ICMSTot
    # ------------------------------------------------------------------
    def test_totais_em_ibscbstot_nao_icmstot(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        kwargs = self._base_product_kwargs()
        kwargs.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("5.0000"),
            ibscbs_v_ibs_uf=Decimal("50.00"),
            ibscbs_p_ibs_mun=Decimal("3.0000"),
            ibscbs_v_ibs_mun=Decimal("30.00"),
            ibscbs_v_ibs=Decimal("80.00"),
            ibscbs_p_cbs=Decimal("8.8000"),
            ibscbs_v_cbs=Decimal("88.00"),
        )
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # IBSCBSTot is a sibling of ICMSTot under <total>
        ibscbs_tot = xml.xpath("//ns:total/ns:IBSCBSTot", namespaces=self.ns)
        self.assertEqual(len(ibscbs_tot), 1)

        # Verify vBCIBSCBS (required first child)
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:vBCIBSCBS", namespaces=self.ns)[0].text,
            "1000.00",
        )

        # Verify nested gIBS structure
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:gIBSUF/ns:vIBSUF", namespaces=self.ns)[0].text,
            "50.00",
        )
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:gIBSMun/ns:vIBSMun", namespaces=self.ns)[0].text,
            "30.00",
        )
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:vIBS", namespaces=self.ns)[0].text,
            "80.00",
        )

        # Verify nested gCBS structure
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gCBS/ns:vCBS", namespaces=self.ns)[0].text,
            "88.00",
        )

        # Verify vDif and vDevTrib are present (required, zero for now)
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gIBS/ns:gIBSUF/ns:vDif", namespaces=self.ns)[0].text,
            "0.00",
        )
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gCBS/ns:vDif", namespaces=self.ns)[0].text,
            "0.00",
        )

    # ------------------------------------------------------------------
    # Test 8: IS entity fields stored but NOT serialized to XML
    # ------------------------------------------------------------------
    def test_is_entity_stored_but_not_in_xml(self):
        """IS (Imposto Seletivo) starts in 2027. Entity fields are stored
        but _serializar_is is not called until schema supports it."""
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)

        kwargs = self._base_product_kwargs()
        kwargs.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("1.00"),
            ibscbs_p_ibs_mun=Decimal("0.0000"),
            ibscbs_v_ibs_mun=Decimal("0.00"),
            ibscbs_v_ibs=Decimal("1.00"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("9.00"),
            # IS fields stored in entity
            is_cst_selec="01",
            is_c_class_trib="010001",
            is_vbc=Decimal("1000.00"),
            is_aliquota=Decimal("1.0000"),
            is_valor=Decimal("10.00"),
        )
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        # Verify entity fields are stored
        produto = nf.produtos_e_servicos[0]
        self.assertEqual(produto.is_cst_selec, "01")
        self.assertEqual(produto.is_c_class_trib, "010001")
        self.assertEqual(produto.is_vbc, Decimal("1000.00"))
        self.assertEqual(produto.is_aliquota, Decimal("1.0000"))
        self.assertEqual(produto.is_valor, Decimal("10.00"))

        # IS totals accumulated internally
        self.assertEqual(nf.totais_is, Decimal("10.00"))

        xml = self._serializar_e_assinar()

        # But IS is NOT in the XML output
        is_tag = xml.xpath("//ns:det/ns:imposto/ns:IS", namespaces=self.ns)
        self.assertEqual(len(is_tag), 0)

        # ISTot not emitted (IS not in schema yet)
        is_tot = xml.xpath("//ns:total/ns:ISTot", namespaces=self.ns)
        self.assertEqual(len(is_tot), 0)

    # ------------------------------------------------------------------
    # Test 9: cMunFGIBS emitted in <ide> header
    # ------------------------------------------------------------------
    def test_cmunfgibs_emitido_no_ide(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)
        nf.municipio_fato_gerador_ibs = "4118402"

        kwargs = self._base_product_kwargs()
        kwargs.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("1.00"),
            ibscbs_p_ibs_mun=Decimal("0.0000"),
            ibscbs_v_ibs_mun=Decimal("0.00"),
            ibscbs_v_ibs=Decimal("1.00"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("9.00"),
        )
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # cMunFGIBS should be present in <ide>
        cmunfgibs = xml.xpath("//ns:ide/ns:cMunFGIBS", namespaces=self.ns)
        self.assertEqual(len(cmunfgibs), 1)
        self.assertEqual(cmunfgibs[0].text, "4118402")

        # cMunFGIBS should come after cMunFG
        ide = xml.xpath("//ns:ide", namespaces=self.ns)[0]
        tags = [child.tag.split("}")[-1] for child in ide]
        cmunfg_idx = tags.index("cMunFG")
        cmunfgibs_idx = tags.index("cMunFGIBS")
        self.assertGreater(cmunfgibs_idx, cmunfg_idx)

    # ------------------------------------------------------------------
    # Test 10: cMunFGIBS NOT emitted when not set
    # ------------------------------------------------------------------
    def test_cmunfgibs_nao_emitido_quando_vazio(self):
        emitente = self._emitente()
        cliente = self._cliente()
        nf = self._nota_fiscal(emitente, cliente)
        # municipio_fato_gerador_ibs not set (empty string default)

        kwargs = self._base_product_kwargs()
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        # cMunFGIBS should NOT be present
        cmunfgibs = xml.xpath("//ns:ide/ns:cMunFGIBS", namespaces=self.ns)
        self.assertEqual(len(cmunfgibs), 0)

    # ------------------------------------------------------------------
    # gRed — reducao de aliquota (TRed) em gIBSUF, gIBSMun e gCBS
    # ------------------------------------------------------------------
    def _kwargs_gred_60(self):
        """Reducao de 60%, valores do exemplo oficial da calculadora RTC
        da Receita Federal (item 3, cClassTrib 200028)."""
        kwargs = self._base_product_kwargs()
        kwargs.update(
            valor_unitario_comercial=Decimal("120.00"),
            valor_total_bruto=Decimal("1200.00"),
            valor_unitario_tributavel=Decimal("120.00"),
            ibscbs_cst="200",
            ibscbs_c_class_trib="200028",
            ibscbs_vbc=Decimal("1200.00"),
            ibscbs_p_ibs_uf=Decimal("0.05"),
            ibscbs_p_red_aliq_ibs_uf=Decimal("60.00"),
            ibscbs_p_aliq_efet_ibs_uf=Decimal("0.02"),
            ibscbs_v_ibs_uf=Decimal("0.24"),
            ibscbs_p_ibs_mun=Decimal("0.05"),
            ibscbs_p_red_aliq_ibs_mun=Decimal("60.00"),
            ibscbs_p_aliq_efet_ibs_mun=Decimal("0.02"),
            ibscbs_v_ibs_mun=Decimal("0.24"),
            ibscbs_v_ibs=Decimal("0.48"),
            ibscbs_p_cbs=Decimal("8.80"),
            ibscbs_p_red_aliq_cbs=Decimal("60.00"),
            ibscbs_p_aliq_efet_cbs=Decimal("3.52"),
            ibscbs_v_cbs=Decimal("42.24"),
        )
        return kwargs

    def test_gred_reducao_60_nos_tres_tributos(self):
        nf = self._nota_fiscal(self._emitente(), self._cliente())
        nf.adicionar_produto_servico(**self._kwargs_gred_60())
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1200.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        base = "//ns:IBSCBS/ns:gIBSCBS"
        for grupo, aliq, efet in (
            ("gIBSUF", "0.0500", "0.0200"),
            ("gIBSMun", "0.0500", "0.0200"),
            ("gCBS", "8.8000", "3.5200"),
        ):
            g = "%s/ns:%s" % (base, grupo)
            # Aliquota nominal (pIBSUF, pIBSMun, pCBS) segue no grupo, antes do gRed
            nominal = xml.xpath(g, namespaces=self.ns)[0][0].text
            self.assertEqual(nominal, aliq, grupo)
            red = xml.xpath(g + "/ns:gRed/ns:pRedAliq", namespaces=self.ns)[0].text
            ef = xml.xpath(g + "/ns:gRed/ns:pAliqEfet", namespaces=self.ns)[0].text
            self.assertEqual(red, "60.0000", grupo)
            self.assertEqual(ef, efet, grupo)

            # Ordem exigida pelo schema: pXXX, gRed, vXXX
            filhos = [c.tag.split("}")[-1] for c in xml.xpath(g, namespaces=self.ns)[0]]
            self.assertEqual(filhos[1], "gRed", grupo)
            self.assertTrue(filhos[0].startswith("p") and filhos[-1].startswith("v"), grupo)

        v_cbs = xml.xpath(base + "/ns:gCBS/ns:vCBS", namespaces=self.ns)[0].text
        self.assertEqual(v_cbs, "42.24")

    def test_gred_reducao_100_aliquota_efetiva_zero(self):
        """Reducao de 100% (ex.: cesta basica): aliquota efetiva zero ainda
        emite gRed, pois o campo foi informado (None != 0)."""
        kwargs = self._kwargs_gred_60()
        kwargs.update(
            ibscbs_c_class_trib="200003",
            ibscbs_p_red_aliq_ibs_uf=Decimal("100"),
            ibscbs_p_aliq_efet_ibs_uf=Decimal("0"),
            ibscbs_v_ibs_uf=Decimal("0"),
            ibscbs_p_red_aliq_ibs_mun=Decimal("100"),
            ibscbs_p_aliq_efet_ibs_mun=Decimal("0"),
            ibscbs_v_ibs_mun=Decimal("0"),
            ibscbs_v_ibs=Decimal("0"),
            ibscbs_p_red_aliq_cbs=Decimal("100"),
            ibscbs_p_aliq_efet_cbs=Decimal("0"),
            ibscbs_v_cbs=Decimal("0"),
        )
        nf = self._nota_fiscal(self._emitente(), self._cliente())
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1200.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        efets = xml.xpath("//ns:gRed/ns:pAliqEfet", namespaces=self.ns)
        self.assertEqual([e.text for e in efets], ["0.0000"] * 3)

    def test_gred_so_na_cbs(self):
        kwargs = self._kwargs_gred_60()
        for campo in (
            "ibscbs_p_red_aliq_ibs_uf",
            "ibscbs_p_aliq_efet_ibs_uf",
            "ibscbs_p_red_aliq_ibs_mun",
            "ibscbs_p_aliq_efet_ibs_mun",
        ):
            kwargs.pop(campo)
        nf = self._nota_fiscal(self._emitente(), self._cliente())
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1200.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        self.assertEqual(len(xml.xpath("//ns:gIBSUF/ns:gRed", namespaces=self.ns)), 0)
        self.assertEqual(len(xml.xpath("//ns:gIBSMun/ns:gRed", namespaces=self.ns)), 0)
        self.assertEqual(len(xml.xpath("//ns:gCBS/ns:gRed", namespaces=self.ns)), 1)

    def test_sem_gred_quando_nao_informado(self):
        """CST 000 sem campos de reducao: XML identico ao anterior, sem gRed."""
        kwargs = self._base_product_kwargs()
        kwargs.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("1000.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("1.00"),
            ibscbs_v_ibs=Decimal("1.00"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("9.00"),
        )
        nf = self._nota_fiscal(self._emitente(), self._cliente())
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        self.assertEqual(len(xml.xpath("//ns:gRed", namespaces=self.ns)), 0)

    def test_gred_sem_aliquota_efetiva_levanta_erro(self):
        kwargs = self._kwargs_gred_60()
        kwargs.pop("ibscbs_p_aliq_efet_cbs")
        nf = self._nota_fiscal(self._emitente(), self._cliente())
        nf.adicionar_produto_servico(**kwargs)
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1200.00, ind_pag=0)

        with self.assertRaisesRegex(ValueError, "gCBS.*pAliqEfet"):
            self._serializar_e_assinar()

    # ------------------------------------------------------------------
    # gTribSN — IBS e CBS do Simples Nacional (valores ficticios)
    # ------------------------------------------------------------------
    def _nota_simples(self):
        emitente = self._emitente()
        emitente.codigo_de_regime_tributario = "1"
        return self._nota_fiscal(emitente, self._cliente())

    def _kwargs_simples(self, **extra):
        kwargs = self._base_product_kwargs()
        kwargs.update(
            icms_modalidade="102",
            icms_csosn="102",
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
        )
        kwargs.update(extra)
        return kwargs

    def _filhos(self, el):
        return [c.tag.split("}")[-1] for c in el]

    def test_gtribsn_ibs_e_cbs_sem_gibscbs(self):
        nf = self._nota_simples()
        nf.adicionar_produto_servico(
            **self._kwargs_simples(
                ibscbs_p_ibs_sn=Decimal("0.1500"),
                ibscbs_v_ibs_sn=Decimal("1.50"),
                ibscbs_p_cbs_sn=Decimal("0.6000"),
                ibscbs_v_cbs_sn=Decimal("6.00"),
            )
        )
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        ibscbs = xml.xpath("//ns:det/ns:imposto/ns:IBSCBS", namespaces=self.ns)[0]
        # Sem base do regime regular: nao emite gIBSCBS zerado
        self.assertEqual(self._filhos(ibscbs), ["CST", "cClassTrib", "gTribSN"])

        sn = "//ns:IBSCBS/ns:gTribSN"
        self.assertEqual(
            xml.xpath(sn + "/ns:gIBSSN/ns:pIBSSN", namespaces=self.ns)[0].text, "0.1500"
        )
        self.assertEqual(xml.xpath(sn + "/ns:gIBSSN/ns:vIBSSN", namespaces=self.ns)[0].text, "1.50")
        self.assertEqual(
            xml.xpath(sn + "/ns:gCBSSN/ns:pCBSSN", namespaces=self.ns)[0].text, "0.6000"
        )
        self.assertEqual(xml.xpath(sn + "/ns:gCBSSN/ns:vCBSSN", namespaces=self.ns)[0].text, "6.00")

        tot = xml.xpath("//ns:total/ns:IBSCBSTot", namespaces=self.ns)[0]
        self.assertEqual(self._filhos(tot), ["vBCIBSCBS", "gTribSN"])
        self.assertEqual(tot[0].text, "0.00")
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gTribSN/ns:vIBSSN", namespaces=self.ns)[0].text, "1.50"
        )
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gTribSN/ns:vCBSSN", namespaces=self.ns)[0].text, "6.00"
        )

    def test_gtribsn_so_cbs_crt2(self):
        """Sem IBS (CRT=2): omite gIBSSN no item; no total vIBSSN e obrigatorio (0.00)."""
        nf = self._nota_simples()
        nf.adicionar_produto_servico(
            **self._kwargs_simples(
                ibscbs_p_cbs_sn=Decimal("0.6000"),
                ibscbs_v_cbs_sn=Decimal("6.00"),
            )
        )
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        sn = xml.xpath("//ns:IBSCBS/ns:gTribSN", namespaces=self.ns)[0]
        self.assertEqual(self._filhos(sn), ["gCBSSN"])
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gTribSN/ns:vIBSSN", namespaces=self.ns)[0].text, "0.00"
        )

    def test_gtribsn_totais_varios_itens(self):
        nf = self._nota_simples()
        for v_ibs, v_cbs in (("1.50", "6.00"), ("0.75", "3.00")):
            nf.adicionar_produto_servico(
                **self._kwargs_simples(
                    ibscbs_p_ibs_sn=Decimal("0.1500"),
                    ibscbs_v_ibs_sn=Decimal(v_ibs),
                    ibscbs_p_cbs_sn=Decimal("0.6000"),
                    ibscbs_v_cbs_sn=Decimal(v_cbs),
                )
            )
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=2000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gTribSN/ns:vIBSSN", namespaces=self.ns)[0].text, "2.25"
        )
        self.assertEqual(
            xml.xpath("//ns:IBSCBSTot/ns:gTribSN/ns:vCBSSN", namespaces=self.ns)[0].text, "9.00"
        )

    def test_gtribsn_com_base_regular_emite_os_dois_grupos(self):
        """Com vBC informado, gIBSCBS continua sendo emitido, antes do gTribSN."""
        nf = self._nota_simples()
        nf.adicionar_produto_servico(
            **self._kwargs_simples(
                ibscbs_vbc=Decimal("1000.00"),
                ibscbs_p_ibs_uf=Decimal("0.1000"),
                ibscbs_v_ibs_uf=Decimal("1.00"),
                ibscbs_v_ibs=Decimal("1.00"),
                ibscbs_p_cbs=Decimal("0.9000"),
                ibscbs_v_cbs=Decimal("9.00"),
                ibscbs_p_cbs_sn=Decimal("0.6000"),
                ibscbs_v_cbs_sn=Decimal("6.00"),
            )
        )
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        xml = self._serializar_e_assinar()

        ibscbs = xml.xpath("//ns:det/ns:imposto/ns:IBSCBS", namespaces=self.ns)[0]
        self.assertEqual(self._filhos(ibscbs), ["CST", "cClassTrib", "gIBSCBS", "gTribSN"])
        tot = xml.xpath("//ns:total/ns:IBSCBSTot", namespaces=self.ns)[0]
        self.assertEqual(self._filhos(tot), ["vBCIBSCBS", "gIBS", "gCBS", "gTribSN"])

    def test_gtribsn_sem_gcbssn_levanta_erro(self):
        nf = self._nota_simples()
        nf.adicionar_produto_servico(
            **self._kwargs_simples(
                ibscbs_p_ibs_sn=Decimal("0.1500"),
                ibscbs_v_ibs_sn=Decimal("1.50"),
            )
        )
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        with self.assertRaisesRegex(ValueError, "gCBSSN e obrigatorio"):
            self._serializar_e_assinar()

    def test_gtribsn_aliquota_sem_valor_levanta_erro(self):
        nf = self._nota_simples()
        nf.adicionar_produto_servico(
            **self._kwargs_simples(
                ibscbs_p_cbs_sn=Decimal("0.6000"),
            )
        )
        nf.adicionar_pagamento(t_pag="01", x_pag="Dinheiro", v_pag=1000.00, ind_pag=0)

        with self.assertRaisesRegex(ValueError, "gCBSSN: informe aliquota e valor"):
            self._serializar_e_assinar()


if __name__ == "__main__":
    unittest.main()
