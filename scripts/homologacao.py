"""Testes contra a SEFAZ em ambiente de HOMOLOGACAO (notas sem valor fiscal).

Configuracao local, fora do repositorio, em ~/.config/pynotas/homologacao.env:

    PFX_PATH=/caminho/do/certificado.pfx
    PFX_SENHA=senha-do-certificado
    UF=SP              # UF do emitente
    CRT=4              # opcional: forca o regime (1, 2, 3 ou 4)

Os dados do emitente vem do certificado (CNPJ e razao social) e da consulta de
cadastro da SEFAZ (IE, endereco, municipio e regime). Nenhum dado do emitente
fica no codigo. Os XMLs gerados vao para ~/.cache/pynotas/homologacao/.

Uso (na raiz do projeto):

    uv run python scripts/homologacao.py status
    uv run python scripts/homologacao.py emitir
    uv run python scripts/homologacao.py emitir --reforma

A ferramenta usa sempre o ambiente de homologacao; nao ha opcao de producao.
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
from decimal import Decimal
from zoneinfo import ZoneInfo

from cryptography.hazmat.primitives.serialization import pkcs12
from lxml import etree

from pynotas.entidades.cliente import Cliente
from pynotas.entidades.emitente import Emitente
from pynotas.entidades.fonte_dados import _fonte_dados
from pynotas.entidades.notafiscal import NotaFiscal
from pynotas.processamento.assinatura import AssinaturaA1
from pynotas.processamento.comunicacao import ComunicacaoSefaz
from pynotas.processamento.serializacao import SerializacaoXML
from pynotas.processamento.validacao import Validacao
from pynotas.utils import obter_codigo_por_municipio
from pynotas.utils.flags import CODIGO_BRASIL, XSD_FOLDER_NFE, XSD_NFE

HOMOLOGACAO = True  # fixo: esta ferramenta nunca acessa producao
NOME_DESTINATARIO = "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
CPF_TESTE = "12345678909"  # CPF ficticio com digitos verificadores validos
FUSO = ZoneInfo("America/Sao_Paulo")

CONFIG = os.path.expanduser("~/.config/pynotas/homologacao.env")
SAIDA = os.path.join(
    os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "pynotas", "homologacao"
)
REGISTRO = os.path.join(SAIDA, "notas.json")


# ---------------------------------------------------------------------------
# Configuracao e dados do emitente
# ---------------------------------------------------------------------------
def ler_config(caminho=CONFIG):
    """Le o arquivo KEY=VALOR. Nunca imprime a senha."""
    if not os.path.isfile(caminho):
        raise SystemExit(f"Configuracao nao encontrada: {caminho} (veja o topo deste script)")
    cfg = {}
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                chave, valor = linha.split("=", 1)
                cfg[chave.strip()] = valor.strip().strip('"').strip("'")
    for obrigatoria in ("PFX_PATH", "PFX_SENHA"):
        if not cfg.get(obrigatoria):
            raise SystemExit(f"{obrigatoria} nao definido em {caminho}")
    cfg["PFX_PATH"] = os.path.expanduser(cfg["PFX_PATH"])
    return cfg


def crt_do_regime(regime):
    """Deduz o CRT a partir do regime de apuracao devolvido pela consulta de cadastro."""
    regime = (regime or "").upper()
    if "MEI" in regime:
        return "4"
    if "SIMPLES" in regime:
        return "1"
    return "3"


def dados_certificado(pfx, senha):
    with open(pfx, "rb") as f:
        conteudo = f.read()
    try:
        _, cert, _ = pkcs12.load_key_and_certificates(conteudo, senha.encode())
    except ValueError:
        raise SystemExit(
            "Nao foi possivel abrir o certificado: senha incorreta ou arquivo invalido"
        )
    sujeito = cert.subject.rfc4514_string()
    nome = re.search(r"CN=([^,:]+)", sujeito).group(1).strip()
    cnpj = re.search(r"(\d{14})", sujeito).group(1)
    return {"nome": nome, "cnpj": cnpj, "validade": cert.not_valid_after_utc}


def texto(xml, tag):
    achados = xml.xpath(f"//*[local-name()='{tag}']")
    return achados[0].text if achados else None


def consultar_cadastro(con, cnpj):
    resposta = con.consulta_cadastro("nfe", cnpj)
    xml = etree.fromstring(resposta.content)
    if texto(xml, "cStat") != "111":
        raise SystemExit(f"Consulta de cadastro: {texto(xml, 'cStat')} - {texto(xml, 'xMotivo')}")
    campos = ("IE", "xNome", "cSit", "indCredNFe", "CNAE", "xRegApur", "xLgr", "nro", "xBairro")
    cadastro = {c: texto(xml, c) for c in campos + ("xMun", "cMun", "CEP", "UF")}
    return cadastro


def montar_contexto(cfg, uf_argumento=None):
    uf = (uf_argumento or cfg.get("UF") or "").upper()
    if not uf:
        raise SystemExit("Informe a UF do emitente: UF=XX no arquivo de configuracao ou --uf")
    cert = dados_certificado(cfg["PFX_PATH"], cfg["PFX_SENHA"])
    con = ComunicacaoSefaz(uf, cfg["PFX_PATH"], cfg["PFX_SENHA"], homologacao=HOMOLOGACAO)
    return {"cfg": cfg, "uf": uf, "cert": cert, "con": con}


# ---------------------------------------------------------------------------
# Registro local das notas emitidas (para consultas e eventos posteriores)
# ---------------------------------------------------------------------------
def preparar_saida():
    os.makedirs(SAIDA, mode=0o700, exist_ok=True)
    os.chmod(SAIDA, 0o700)


def salvar(nome, conteudo):
    preparar_saida()
    caminho = os.path.join(SAIDA, nome)
    with open(caminho, "wb") as f:
        f.write(conteudo)
    return caminho


def registrar(nota):
    notas = carregar_registro()
    notas.append(nota)
    salvar("notas.json", json.dumps(notas, indent=2, ensure_ascii=False).encode())


def carregar_registro():
    if not os.path.isfile(REGISTRO):
        return []
    with open(REGISTRO, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------
def cmd_status(ctx, args):
    cert = ctx["cert"]
    print(f"Certificado: {cert['nome']} | CNPJ {cert['cnpj']}")
    print(f"Valido ate: {cert['validade']:%d/%m/%Y}")

    resposta = ctx["con"].status_servico("nfe")
    xml = etree.fromstring(resposta.content)
    print(
        f"\nStatus NF-e {ctx['uf']} (homologacao): {texto(xml, 'cStat')} - {texto(xml, 'xMotivo')}"
    )

    cad = consultar_cadastro(ctx["con"], cert["cnpj"])
    crt = ctx["cfg"].get("CRT") or crt_do_regime(cad["xRegApur"])
    print("\nCadastro do emitente:")
    print(f"  IE {cad['IE']} | situacao {cad['cSit']} | credenciado NF-e {cad['indCredNFe']}")
    print(f"  regime {cad['xRegApur']} -> CRT {crt}")
    print(f"  {cad['xLgr']}, {cad['nro']} - {cad['xMun']}/{cad['UF']} - CEP {cad['CEP']}")
    return 0


def montar_emitente(ctx):
    cert, cfg = ctx["cert"], ctx["cfg"]
    cad = consultar_cadastro(ctx["con"], cert["cnpj"])
    municipio = cad["cMun"] or obter_codigo_por_municipio(cad["xMun"], ctx["uf"])
    emitente = Emitente(
        razao_social=cad["xNome"] or cert["nome"],
        nome_fantasia=cad["xNome"] or cert["nome"],
        cnpj=cert["cnpj"],
        codigo_de_regime_tributario=cfg.get("CRT") or crt_do_regime(cad["xRegApur"]),
        inscricao_estadual=cad["IE"],
        cnae_fiscal=cad["CNAE"] or "",
        endereco_logradouro=cad["xLgr"],
        endereco_numero=cad["nro"] or "SN",
        endereco_bairro=cad["xBairro"] or "CENTRO",
        endereco_municipio=cad["xMun"],
        endereco_uf=ctx["uf"],
        endereco_cep=cad["CEP"],
        endereco_pais=CODIGO_BRASIL,
    )
    return emitente, str(municipio), cad


def cmd_emitir(ctx, args):
    emitente, municipio, cad = montar_emitente(ctx)
    cliente = Cliente(
        razao_social=NOME_DESTINATARIO,
        tipo_documento="CPF",
        numero_documento=CPF_TESTE,
        indicador_ie=9,
        endereco_logradouro="RUA DE TESTE",
        endereco_numero="1",
        endereco_bairro="CENTRO",
        endereco_municipio=cad["xMun"],
        endereco_uf=ctx["uf"],
        endereco_cep=cad["CEP"],
        endereco_pais=CODIGO_BRASIL,
    )
    agora = datetime.datetime.now(FUSO).replace(microsecond=0) - datetime.timedelta(minutes=1)
    numero = str(args.numero or int(time.time()) % 900000 + 1)
    nf = NotaFiscal(
        emitente=emitente,
        cliente=cliente,
        uf=ctx["uf"],
        natureza_operacao="VENDA DE MERCADORIA",
        forma_pagamento=0,
        modelo=55,
        serie=args.serie,
        numero_nf=numero,
        data_emissao=agora,
        data_saida_entrada=agora,
        tipo_documento=1,
        municipio=municipio,
        tipo_impressao_danfe=1,
        forma_emissao="1",
        cliente_final=1,
        indicador_destino=1,
        indicador_presencial=1,
        finalidade_emissao="1",
        processo_emissao="0",
        transporte_modalidade_frete=9,
        informacoes_adicionais_interesse_fisco="Teste de homologacao pyNotas",
        totais_tributos_aproximado=Decimal("0"),
    )
    produto = dict(
        codigo="TESTE01",
        descricao="PRODUTO DE TESTE - HOMOLOGACAO",
        ncm=args.ncm,
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
    if args.reforma:
        # Aliquotas de teste de 2026; o teste e de estrutura, nao de calculo
        produto.update(
            ibscbs_cst="000",
            ibscbs_c_class_trib="000001",
            ibscbs_vbc=Decimal("10.00"),
            ibscbs_p_ibs_uf=Decimal("0.1000"),
            ibscbs_v_ibs_uf=Decimal("0.01"),
            ibscbs_p_ibs_mun=Decimal("0.0000"),
            ibscbs_v_ibs_mun=Decimal("0.00"),
            ibscbs_v_ibs=Decimal("0.01"),
            ibscbs_p_cbs=Decimal("0.9000"),
            ibscbs_v_cbs=Decimal("0.09"),
        )
        if emitente.codigo_de_regime_tributario in ("1", "2", "4"):
            produto.update(
                ibscbs_p_ibs_sn=Decimal("0.1000"),
                ibscbs_v_ibs_sn=Decimal("0.01"),
                ibscbs_p_cbs_sn=Decimal("0.9000"),
                ibscbs_v_cbs_sn=Decimal("0.09"),
            )
    nf.adicionar_produto_servico(**produto)
    nf.adicionar_pagamento(t_pag="01", v_pag=10.00, ind_pag=0)

    xml = SerializacaoXML(_fonte_dados, homologacao=HOMOLOGACAO).exportar()
    cfg = ctx["cfg"]
    assinado = AssinaturaA1(cfg["PFX_PATH"], cfg["PFX_SENHA"]).assinar(xml)
    chave = assinado.xpath("//*[local-name()='infNFe']")[0].get("Id")[3:]
    print(f"NF-e serie {args.serie} numero {numero} | chave {chave}")

    v = Validacao()
    v.validar_etree(xml_doc=assinado, xsd_file=v.get_xsd(XSD_NFE, XSD_FOLDER_NFE), use_assert=True)
    print("Schema local: OK")
    salvar(f"nfe_{chave}.xml", etree.tostring(assinado, encoding="utf-8", xml_declaration=True))

    retorno = ctx["con"].autorizacao(modelo="nfe", nota_fiscal=assinado, id_lote=numero, ind_sinc=1)
    if retorno[0] == 0:
        proc = retorno[1]
        protocolo = texto(proc, "nProt")
        print(
            f"AUTORIZADA: {texto(proc, 'cStat')} - {texto(proc, 'xMotivo')} | protocolo {protocolo}"
        )
        caminho = salvar(
            f"nfeProc_{chave}.xml", etree.tostring(proc, encoding="utf-8", xml_declaration=True)
        )
        registrar(
            {
                "chave": chave,
                "protocolo": protocolo,
                "serie": args.serie,
                "numero": numero,
                "reforma": args.reforma,
                "autorizada_em": texto(proc, "dhRecbto"),
            }
        )
        print(f"XML autorizado: {caminho}")
        return 0

    resposta = retorno[1]
    salvar(f"retorno_{chave}.xml", resposta.content)
    try:
        xml_resp = etree.fromstring(resposta.content)
        for c, m in zip(
            xml_resp.xpath("//*[local-name()='cStat']/text()"),
            xml_resp.xpath("//*[local-name()='xMotivo']/text()"),
        ):
            print(f"cStat {c} - {m}")
    except etree.XMLSyntaxError:
        print(f"HTTP {resposta.status_code}: {resposta.text[:300]}")
    return 1


def criar_parser():
    parser = argparse.ArgumentParser(description="Testes contra a SEFAZ em homologacao.")
    parser.add_argument("--uf", help="UF do emitente (padrao: UF do arquivo de configuracao)")
    sub = parser.add_subparsers(dest="comando", required=True)

    sub.add_parser("status", help="status da SEFAZ e cadastro do emitente")

    emitir = sub.add_parser("emitir", help="emite uma NF-e de teste")
    emitir.add_argument(
        "--reforma", action="store_true", help="inclui IBS/CBS (e gTribSN no Simples)"
    )
    emitir.add_argument("--serie", default="1")
    emitir.add_argument("--numero", type=int, help="numero da nota (padrao: gerado)")
    emitir.add_argument("--ncm", default="33049990", help="NCM do produto de teste")
    return parser


COMANDOS = {"status": cmd_status, "emitir": cmd_emitir}


def main(argv=None):
    args = criar_parser().parse_args(argv)
    ctx = montar_contexto(ler_config(), args.uf)
    return COMANDOS[args.comando](ctx, args)


if __name__ == "__main__":
    sys.exit(main())
