# Source Map: `notafiscal.py` (1307 lines)

Entity models for NF-e/NFC-e invoices and related objects (products, taxes, payments, transport, etc.).

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `NotaFiscal` | 13-596 | Main invoice entity |
| `NotaFiscalReferenciada` | 599-627 | Referenced invoice |
| `NotaFiscalProduto` | 630-1105 | Product/service item with all tax fields |
| `NotaFiscalDeclaracaoImportacao` | 1108-1153 | Import declaration |
| `NotaFiscalDeclaracaoImportacaoAdicao` | 1156-1167 | Import declaration addition |
| `NotaFiscalTransporteVolume` | 1170-1199 | Transport volume |
| `NotaFiscalTransporteVolumeLacre` | 1202-1204 | Volume seal |
| `NotaFiscalCobrancaDuplicata` | 1207-1215 | Billing duplicate |
| `NotaFiscalObservacaoContribuinte` | 1218-1223 | Taxpayer note |
| `NotaFiscalProcessoReferenciado` | 1226-1236 | Referenced process |
| `NotaFiscalEntregaRetirada` | 1239-1275 | Delivery/withdrawal address |
| `NotaFiscalResponsavelTecnico` | 1278-1284 | Technical responsible (NT2018/003) |
| `AutorizadosBaixarXML` | 1287-1288 | Authorized XML downloaders |
| `NotaFiscalPagamentos` | 1291-1307 | Payment details |

---

## `NotaFiscal` — Lines 13-596

### Field Groups
| Section | Lines | Fields |
|---------|-------|--------|
| Deprecated fields | 15-22 | `tipo_pagamento` deprecated |
| Invoice identity | 24-122 | status, codigo_numerico, modelo, serie, numero_nf, data_emissao, natureza_operacao, tipo_documento, processo_emissao, tipo_impressao_danfe, forma_emissao, finalidade_emissao, cliente_final, indicador_presencial, indicador_intermediador, indicador_destino, uf, municipio |
| Read-only fields | 123-139 | digest_value, valor_total_nota, valor_icms_nota, valor_icms_st_nota, protocolo, data |
| Relationships | 141-168 | notas_fiscais_referenciadas, emitente, destinatario_remetente, entrega, retirada, autorizados_baixar_xml, produtos_e_servicos |
| ICMS totals | 170-298 | totais_icms_base_calculo, totais_icms_total, totais_icms_desonerado, totais_icms_st_*, totais_icms_total_*, totais_fcp_*, totais_icms_inter_*, totais_icms_*_mono_* |
| **Reforma Tributaria totals** | 300-312 | totais_vbc_ibscbs, totais_ibs_uf, totais_ibs_mun, totais_ibs, totais_cbs, totais_is, totais_ibs_sn/totais_cbs_sn (None until an item has gTribSN), **municipio_fato_gerador_ibs** — IVA Dual totals + Group B field (EC 132/2023) |
| Transport | 312-367 | transporte_modalidade_frete, transporte_transportadora, transporte_retencao_icms_*, transporte_veiculo_*, transporte_reboque_*, transporte_volumes |
| Billing | 369-384 | fatura_numero, fatura_valor_original, fatura_valor_desconto, fatura_valor_liquido, duplicatas |
| Additional info | 386-403 | informacoes_adicionais_*, observacoes_contribuinte, processos_referenciados, pagamentos, valor_troco |

### Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__()` | 408-419 | Initialize all list fields |
| `adicionar_pagamento()` | 424-428 | Add payment |
| `adicionar_autorizados_baixar_xml()` | 430-433 | Add authorized XML downloader |
| `adicionar_nota_fiscal_referenciada()` | 435-439 | Add referenced invoice |
| `adicionar_produto_servico()` | 441-508 | **Add product** — accumulates all ICMS/tax totals + **IBSCBS/IS totals** (vNF excludes IBS/CBS/IS) |
| `adicionar_transporte_volume()` | 510-514 | Add transport volume |
| `adicionar_duplicata()` | 516-520 | Add billing duplicate |
| `adicionar_observacao_contribuinte()` | 522-526 | Add taxpayer note |
| `adicionar_processo_referenciado()` | 528-532 | Add referenced process |
| `adicionar_responsavel_tecnico()` | 534-538 | Add technical responsible |
| `_codigo_numerico_aleatorio()` | 540-543 | Generate random 8-digit code |
| `_dv_codigo_numerico()` | 545-570 | Calculate check digit (mod 11) |
| `identificador_unico` (property) | 559-587 | Build 44-char NF-e access key |

---

## `NotaFiscalProduto` — Lines 630-1105

### Field Groups
| Section | Lines | Fields |
|---------|-------|--------|
| Product data | 626-700 | codigo, descricao, ean, ncm, cfop, unidade_comercial, quantidade_comercial, valor_unitario_comercial, unidade_tributavel, cbenef, quantidade_tributavel, valor_unitario_tributavel, ean_tributavel, total_frete, total_seguro, desconto, outras_despesas_acessorias, valor_total_bruto, numero_pedido, numero_item |
| Fuel data | 702-747 | cProdANP, descANP, pGLP, pGNn, pGNi, vPart, UFCons, comb_codif, comb_q_temp, comb_n_bico, comb_n_bomba, comb_n_tanque, comb_v_enc_ini, comb_v_enc_fin, comb_p_bio |
| ICMS fields | 749-840 | icms_modalidade, icms_origem, icms_modalidade_determinacao_bc, icms_percentual_reducao_bc, icms_valor_base_calculo, icms_aliquota, icms_valor, icms_desonerado, icms_motivo_desoneracao, icms_st_*, fcp_*, icms_inter_*, icms_st_ret_*, icms_*_mono_* |
| IPI fields | 842-891 | ipi_situacao_tributaria, ipi_classe_enquadramento, ipi_codigo_enquadramento, ipi_valor_base_calculo, ipi_aliquota, ipi_valor_ipi, pdevol, ipi_valor_ipi_dev |
| PIS fields | 893-937 | pis_modalidade (via pis_situacao_tributaria), pis_valor_base_calculo, pis_aliquota_percentual, pis_aliquota_reais, pis_valor, pis_st_* |
| COFINS fields | 939-983 | cofins_modalidade, cofins_valor_base_calculo, cofins_aliquota_percentual, cofins_aliquota_reais, cofins_valor, cofins_st_* |
| ISSQN fields | 985-1004 | issqn_valor_base_calculo, issqn_aliquota, issqn_lista_servico, issqn_uf, issqn_municipio, issqn_valor |
| Import tax fields | 1006-1017 | imposto_importacao_valor_base_calculo, imposto_importacao_valor_despesas_aduaneiras, imposto_importacao_valor_iof, imposto_importacao_valor |
| **Reforma Tributaria fields** | 1030-1077 | **IBSCBS**: ibscbs_cst, ibscbs_c_class_trib, ibscbs_vbc, ibscbs_p_ibs_uf, ibscbs_v_ibs_uf, ibscbs_p_ibs_mun, ibscbs_v_ibs_mun, ibscbs_v_ibs, ibscbs_p_cbs, ibscbs_v_cbs; **gRed** (default None): ibscbs_p_red_aliq_{ibs_uf,ibs_mun,cbs}, ibscbs_p_aliq_efet_{ibs_uf,ibs_mun,cbs}; **gTribSN** (default None): ibscbs_p_ibs_sn, ibscbs_v_ibs_sn, ibscbs_p_cbs_sn, ibscbs_v_cbs_sn; `tem_trib_sn()` at 1097; **IS**: is_cst_selec, is_c_class_trib, is_vbc, is_aliquota, is_valor |
| Additional info | 1050-1065 | informacoes_adicionais, declaracoes_importacao |

---

## Supporting Entities (Lines 1108-1307)

Small entity classes for nested data — see class table above for line ranges. All extend `Entidade` base class and use kwargs initialization.
