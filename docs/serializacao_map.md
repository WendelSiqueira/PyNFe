# Source Map: `serializacao.py` (2747 lines)

XML serialization of NF-e, NFC-e and MDF-e documents into SEFAZ-compliant XML format.

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Serializacao` | 30-63 | Abstract base class (not instantiable directly) |
| `SerializacaoXML` | 66-2148 | Main NF-e/NFC-e XML serialization |
| `SerializacaoQrcode` | 2151-2251 | NFC-e QR Code generation |
| `SerializacaoQrcodeMDFe` | 2254-2277 | MDF-e QR Code generation |
| `SerializacaoMDFe` | 2280-2747 | MDF-e XML serialization |

---

## `Serializacao` (base class) — Lines 30-63

Abstract base for all serializers. Stores `_fonte_dados`, `_ambiente` (1=prod, 2=homolog), `_contingencia`, `_so_cpf`.

## `SerializacaoXML` — Lines 66-2148

### Exported Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `exportar()` | 71-97 | Main entry: exports NF-e XML from data source |
| `serializar_evento()` | ~1862 | Serializes NF-e events (cancellation, correction letter) |
| `serializar_evento_mdfe()` | ~1896 | Serializes MDF-e events (cancel, close, add driver, add DF-e, payment) |

### Internal Serializers (NF-e)
| Method | Lines | Purpose |
|--------|-------|---------|
| `_serializar_emitente()` | 105-146 | Issuer data (CNPJ/CPF, address, IE, CRT) |
| `_serializar_cliente()` | 148-200 | Customer/destination data (document, address, IE indicator) |
| `_serializar_transportadora()` | 202-228 | Carrier data |
| `_serializar_entrega_retirada()` | 230-255 | Delivery/withdrawal address |
| `_serializar_autorizados_baixar_xml()` | 257-270 | Authorized XML downloaders |
| `_serializar_produto_servico()` | 279-466 | **Product/service item** (prod data, fuel, taxes dispatch incl. IBSCBS) |
| `_serializar_responsavel_tecnico()` | 1488-1500 | Technical responsible (NT2018/003) |
| `_serializar_nota_fiscal()` | 1554-2020 | **Main NF-e assembly** (ide w/ cMunFGIBS, emit, dest, items, totals incl. IBSCBSTot, transport, billing, payment, additional info) |

### Tax Serializers (within `SerializacaoXML`)
| Method | Lines | Purpose |
|--------|-------|---------|
| `_serializar_imposto_icms()` | 468-1085 | **ICMS tax** — all CST/CSOSN modalities |
| `_serializar_imposto_ipi()` | 1087-1125 | IPI tax |
| `_serializar_imposto_pis()` | 1127-1190 | PIS tax |
| `_serializar_imposto_cofins()` | 1192-1255 | COFINS tax |
| `_serializar_imposto_importacao()` | 1257-1286 | Import tax (II) |
| `_serializar_imposto_ibscbs()` | 1288-1306 | **Reforma Tributaria** — dispatches IBSCBS + IS serialization |
| `_serializar_ibscbs()` | 1308-1370 | IBSCBS (IBS + CBS) — `<IBSCBS>` as direct child of `<imposto>` |
| `_serializar_gtribsn()` | 1372-1399 | gTribSN (TTribSN) — IBS/CBS do Simples Nacional (gIBSSN opcional, gCBSSN obrigatorio); raises ValueError if incomplete |
| `_serializar_gred()` | 1401-1417 | gRed (TRed) — reducao de aliquota inside gIBSUF/gIBSMun/gCBS; raises ValueError if pAliqEfet missing |
| `_serializar_is()` | 1419-1434 | IS (Imposto Seletivo) — ready but not called until 2027 |
| `_serializar_declaracao_importacao()` | 1436-1486 | Import declaration (DI) |

### ICMS Modalities Detail (within `_serializar_imposto_icms`)
| CST/CSOSN | Lines | Description |
|-----------|-------|-------------|
| 00 | 460-484 | Fully taxed |
| 02 | 486-499 | Monophasic on fuels |
| 10 | 502-563 | Taxed + ICMS ST |
| 15 | 566-595 | Monophasic + retention on fuels |
| 20 | 598-637 | Reduced base |
| 30 | 640-680 | Exempt + ICMS ST |
| 40/41/50 | 683-694 | Exempt / Not taxed / Suspended |
| 51 | 697-714 | Deferral |
| 53 | 717-739 | Monophasic deferred on fuels |
| 60/ST | 742-765 | Previously charged by ST |
| 61 | 768-780 | Monophasic previously charged on fuels |
| 70 | 783-850 | Reduced base + ICMS ST |
| 90 | 853-925 | Other |
| 101 | 930-939 | Simples Nacional with credit |
| 102/103/300/400 | 946-949 | Simples Nacional without credit |
| 201/202/203 | 954-999 | Simples Nacional + ICMS ST |
| 500 | 1002-1005 | SN previously charged by ST |
| 900 | 1008-1070 | SN Other |

### Payment Serializers
| Method | Lines | Purpose |
|--------|-------|---------|
| `_serializar_pagamentos_antigo_deprecado()` | 1502-1521 | Legacy payment (deprecated) |
| `_serializar_pagamentos()` | 1523-1552 | Current payment serialization |

### NF-e Assembly Detail (`_serializar_nota_fiscal`)
| Section | Lines | XML tags |
|---------|-------|----------|
| IDE (identification) | 1495-1550 | `<ide>` cUF, cNF, natOp, mod, serie, nNF, dhEmi, tpNF, cMunFG, **cMunFGIBS**, etc. |
| Referenced NF-e | 1552-1588 | `<NFref>` refNFe, refNF, refNFP, refCTe |
| Contingency | 1590-1599 | dhCont, xJust |
| Emitter | 1645 | `<emit>` |
| Customer | 1604-1615 | `<dest>` |
| Withdrawal/Delivery | 1617-1634 | `<retirada>`, `<entrega>` |
| Authorized XML | 1637-1638 | `<autXML>` |
| Items | 1640-1647 | `<det>` with nItem |
| Totals (ICMSTot) | 1649-1742 | `<total><ICMSTot>` all legacy tax totals |
| **Totals (IBSCBSTot)** | 1826-1882 | `<total><IBSCBSTot>` Reforma Tributaria totals (vBCIBSCBS, gIBS, gCBS, gTribSN) |
| Transport | 1791-1834 | `<transp>` modFrete, carrier, vehicle, volumes |
| Billing | ~1836-1856 | `<cobr>` fat, dup |
| Payment | ~1858-1886 | `<pag>` detPag |
| Additional info | ~1888-1901 | `<infAdic>` |
| Technical responsible | ~1903-1909 | `<infRespTec>` |

---

## `SerializacaoQrcode` — Lines 2151-2251

Generates NFC-e QR Code URL. Handles online/offline modes and state-specific URL patterns (SP, BA, MG, etc.).

## `SerializacaoQrcodeMDFe` — Lines 2254-2277

Generates MDF-e QR Code URL using SVRS endpoint.

## `SerializacaoMDFe` — Lines 2280-2747

### Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `exportar()` | 2285-2311 | Main entry: exports MDF-e XML |
| `_serializar_emitente()` | 2319-2351 | MDF-e issuer (CPF/CNPJ, IE, address) |
| `_serializar_municipio_carrega()` | 2353-2363 | Loading municipality |
| `_serializar_percurso()` | 2365-2372 | Route (UF waypoints) |
| `_serializar_modal_rodoviario()` | 2374-2533 | **Road modal** (ANTT, CIOT, tolls, contractors, traction vehicle, trailer) |
| `_serializar_documentos()` | 2535-2559 | Linked documents (NF-e or CT-e) |
| `_serializar_seguradora()` | 2561-2581 | Insurance info |
| `_serializar_produto()` | 2583-2593 | Predominant product |
| `_serializar_totais()` | 2595-2615 | Totals (weight, qty) |
| `_serializar_lacres()` | 2617-2624 | Seals |
| `_serializar_responsavel_tecnico()` | 2626-2638 | Technical responsible |
| `_serializar_manifesto()` | 2640-2747 | **Main MDF-e assembly** (ide, emit, modal, doc, seg, prod, tot, lacres, infAdic, infRespTec) |
