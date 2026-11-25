# Source Map: `notafiscal.py` (1306 lines)

Entity models for NF-e/NFC-e invoices and related objects (products, taxes, payments, transport, etc.).

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `NotaFiscal` | 12-595 | Main invoice entity |
| `NotaFiscalReferenciada` | 598-626 | Referenced invoice |
| `NotaFiscalProduto` | 629-1104 | Product/service item with all tax fields |
| `NotaFiscalDeclaracaoImportacao` | 1107-1152 | Import declaration |
| `NotaFiscalDeclaracaoImportacaoAdicao` | 1155-1166 | Import declaration addition |
| `NotaFiscalTransporteVolume` | 1169-1198 | Transport volume |
| `NotaFiscalTransporteVolumeLacre` | 1201-1203 | Volume seal |
| `NotaFiscalCobrancaDuplicata` | 1206-1214 | Billing duplicate |
| `NotaFiscalObservacaoContribuinte` | 1217-1222 | Taxpayer note |
| `NotaFiscalProcessoReferenciado` | 1225-1235 | Referenced process |
| `NotaFiscalEntregaRetirada` | 1238-1274 | Delivery/withdrawal address |
| `NotaFiscalResponsavelTecnico` | 1277-1283 | Technical responsible (NT2018/003) |
| `AutorizadosBaixarXML` | 1286-1287 | Authorized XML downloaders |
| `NotaFiscalPagamentos` | 1290-1306 | Payment details |

---

## `NotaFiscal` — Lines 12-595

### Field Groups
| Section | Lines | Fields |
|---------|-------|--------|
| Deprecated fields | 14-21 | `tipo_pagamento` deprecated |
| Invoice identity | 23-121 | status, codigo_numerico, modelo, serie, numero_nf, data_emissao, natureza_operacao, tipo_documento, processo_emissao, tipo_impressao_danfe, forma_emissao, finalidade_emissao, cliente_final, indicador_presencial, indicador_intermediador, indicador_destino, uf, municipio |
| Read-only fields | 122-138 | digest_value, valor_total_nota, valor_icms_nota, valor_icms_st_nota, protocolo, data |
| Relationships | 140-167 | notas_fiscais_referenciadas, emitente, destinatario_remetente, entrega, retirada, autorizados_baixar_xml, produtos_e_servicos |
| ICMS totals | 169-297 | totais_icms_base_calculo, totais_icms_total, totais_icms_desonerado, totais_icms_st_*, totais_icms_total_*, totais_fcp_*, totais_icms_inter_*, totais_icms_*_mono_* |
| **Reforma Tributaria totals** | 299-311 | totais_vbc_ibscbs, totais_ibs_uf, totais_ibs_mun, totais_ibs, totais_cbs, totais_is, totais_ibs_sn/totais_cbs_sn (None until an item has gTribSN), **municipio_fato_gerador_ibs** — IVA Dual totals + Group B field (EC 132/2023) |
| Transport | 311-366 | transporte_modalidade_frete, transporte_transportadora, transporte_retencao_icms_*, transporte_veiculo_*, transporte_reboque_*, transporte_volumes |
| Billing | 368-383 | fatura_numero, fatura_valor_original, fatura_valor_desconto, fatura_valor_liquido, duplicatas |
| Additional info | 385-402 | informacoes_adicionais_*, observacoes_contribuinte, processos_referenciados, pagamentos, valor_troco |

### Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__()` | 407-418 | Initialize all list fields |
| `adicionar_pagamento()` | 423-427 | Add payment |
| `adicionar_autorizados_baixar_xml()` | 429-432 | Add authorized XML downloader |
| `adicionar_nota_fiscal_referenciada()` | 434-438 | Add referenced invoice |
| `adicionar_produto_servico()` | 440-507 | **Add product** — accumulates all ICMS/tax totals + **IBSCBS/IS totals** (vNF excludes IBS/CBS/IS) |
| `adicionar_transporte_volume()` | 509-513 | Add transport volume |
| `adicionar_duplicata()` | 515-519 | Add billing duplicate |
| `adicionar_observacao_contribuinte()` | 521-525 | Add taxpayer note |
| `adicionar_processo_referenciado()` | 527-531 | Add referenced process |
| `adicionar_responsavel_tecnico()` | 533-537 | Add technical responsible |
| `_codigo_numerico_aleatorio()` | 539-542 | Generate random 8-digit code |
| `_dv_codigo_numerico()` | 544-569 | Calculate check digit (mod 11) |
| `identificador_unico` (property) | 558-586 | Build 44-char NF-e access key |

---

## `NotaFiscalProduto` — Lines 629-1104

### Field Groups
| Section | Lines | Fields |
|---------|-------|--------|
| Product data | 625-699 | codigo, descricao, ean, ncm, cfop, unidade_comercial, quantidade_comercial, valor_unitario_comercial, unidade_tributavel, cbenef, quantidade_tributavel, valor_unitario_tributavel, ean_tributavel, total_frete, total_seguro, desconto, outras_despesas_acessorias, valor_total_bruto, numero_pedido, numero_item |
| Fuel data | 701-746 | cProdANP, descANP, pGLP, pGNn, pGNi, vPart, UFCons, comb_codif, comb_q_temp, comb_n_bico, comb_n_bomba, comb_n_tanque, comb_v_enc_ini, comb_v_enc_fin, comb_p_bio |
| ICMS fields | 748-839 | icms_modalidade, icms_origem, icms_modalidade_determinacao_bc, icms_percentual_reducao_bc, icms_valor_base_calculo, icms_aliquota, icms_valor, icms_desonerado, icms_motivo_desoneracao, icms_st_*, fcp_*, icms_inter_*, icms_st_ret_*, icms_*_mono_* |
| IPI fields | 841-890 | ipi_situacao_tributaria, ipi_classe_enquadramento, ipi_codigo_enquadramento, ipi_valor_base_calculo, ipi_aliquota, ipi_valor_ipi, pdevol, ipi_valor_ipi_dev |
| PIS fields | 892-936 | pis_modalidade (via pis_situacao_tributaria), pis_valor_base_calculo, pis_aliquota_percentual, pis_aliquota_reais, pis_valor, pis_st_* |
| COFINS fields | 938-982 | cofins_modalidade, cofins_valor_base_calculo, cofins_aliquota_percentual, cofins_aliquota_reais, cofins_valor, cofins_st_* |
| ISSQN fields | 984-1003 | issqn_valor_base_calculo, issqn_aliquota, issqn_lista_servico, issqn_uf, issqn_municipio, issqn_valor |
| Import tax fields | 1005-1016 | imposto_importacao_valor_base_calculo, imposto_importacao_valor_despesas_aduaneiras, imposto_importacao_valor_iof, imposto_importacao_valor |
| **Reforma Tributaria fields** | 1029-1076 | **IBSCBS**: ibscbs_cst, ibscbs_c_class_trib, ibscbs_vbc, ibscbs_p_ibs_uf, ibscbs_v_ibs_uf, ibscbs_p_ibs_mun, ibscbs_v_ibs_mun, ibscbs_v_ibs, ibscbs_p_cbs, ibscbs_v_cbs; **gRed** (default None): ibscbs_p_red_aliq_{ibs_uf,ibs_mun,cbs}, ibscbs_p_aliq_efet_{ibs_uf,ibs_mun,cbs}; **gTribSN** (default None): ibscbs_p_ibs_sn, ibscbs_v_ibs_sn, ibscbs_p_cbs_sn, ibscbs_v_cbs_sn; `tem_trib_sn()` at 1090; **IS**: is_cst_selec, is_c_class_trib, is_vbc, is_aliquota, is_valor |
| Additional info | 1049-1064 | informacoes_adicionais, declaracoes_importacao |

---

## Supporting Entities (Lines 1107-1306)

Small entity classes for nested data — see class table above for line ranges. All extend `Entidade` base class and use kwargs initialization.
