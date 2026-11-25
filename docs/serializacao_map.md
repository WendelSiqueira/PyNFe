# Source Map: `serializacao.py` (2748 lines)

XML serialization of NF-e, NFC-e and MDF-e documents into SEFAZ-compliant XML format.

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Serializacao` | 31-64 | Abstract base class (not instantiable directly) |
| `SerializacaoXML` | 67-2149 | Main NF-e/NFC-e XML serialization |
| `SerializacaoQrcode` | 2152-2252 | NFC-e QR Code generation |
| `SerializacaoQrcodeMDFe` | 2255-2278 | MDF-e QR Code generation |
| `SerializacaoMDFe` | 2281-2748 | MDF-e XML serialization |

---

## `Serializacao` (base class) — Lines 31-64

Abstract base for all serializers. Stores `_fonte_dados`, `_ambiente` (1=prod, 2=homolog), `_contingencia`, `_so_cpf`.

## `SerializacaoXML` — Lines 67-2149

### Exported Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `exportar()` | 72-98 | Main entry: exports NF-e XML from data source |
| `serializar_evento()` | ~1862 | Serializes NF-e events (cancellation, correction letter) |
| `serializar_evento_mdfe()` | ~1896 | Serializes MDF-e events (cancel, close, add driver, add DF-e, payment) |

### Internal Serializers (NF-e)
| Method | Lines | Purpose |
|--------|-------|---------|
| `_serializar_emitente()` | 106-147 | Issuer data (CNPJ/CPF, address, IE, CRT) |
| `_serializar_cliente()` | 149-201 | Customer/destination data (document, address, IE indicator) |
| `_serializar_transportadora()` | 203-229 | Carrier data |
| `_serializar_entrega_retirada()` | 231-256 | Delivery/withdrawal address |
| `_serializar_autorizados_baixar_xml()` | 258-271 | Authorized XML downloaders |
| `_serializar_produto_servico()` | 280-467 | **Product/service item** (prod data, fuel, taxes dispatch incl. IBSCBS) |
| `_serializar_responsavel_tecnico()` | 1489-1501 | Technical responsible (NT2018/003) |
| `_serializar_nota_fiscal()` | 1555-2021 | **Main NF-e assembly** (ide w/ cMunFGIBS, emit, dest, items, totals incl. IBSCBSTot, transport, billing, payment, additional info) |

### Tax Serializers (within `SerializacaoXML`)
| Method | Lines | Purpose |
|--------|-------|---------|
| `_serializar_imposto_icms()` | 469-1086 | **ICMS tax** — all CST/CSOSN modalities |
| `_serializar_imposto_ipi()` | 1088-1126 | IPI tax |
| `_serializar_imposto_pis()` | 1128-1191 | PIS tax |
| `_serializar_imposto_cofins()` | 1193-1256 | COFINS tax |
| `_serializar_imposto_importacao()` | 1258-1287 | Import tax (II) |
| `_serializar_imposto_ibscbs()` | 1289-1307 | **Reforma Tributaria** — dispatches IBSCBS + IS serialization |
| `_serializar_ibscbs()` | 1309-1371 | IBSCBS (IBS + CBS) — `<IBSCBS>` as direct child of `<imposto>` |
| `_serializar_gtribsn()` | 1373-1400 | gTribSN (TTribSN) — IBS/CBS do Simples Nacional (gIBSSN opcional, gCBSSN obrigatorio); raises ValueError if incomplete |
| `_serializar_gred()` | 1402-1418 | gRed (TRed) — reducao de aliquota inside gIBSUF/gIBSMun/gCBS; raises ValueError if pAliqEfet missing |
| `_serializar_is()` | 1420-1435 | IS (Imposto Seletivo) — ready but not called until 2027 |
| `_serializar_declaracao_importacao()` | 1437-1487 | Import declaration (DI) |

### ICMS Modalities Detail (within `_serializar_imposto_icms`)
| CST/CSOSN | Lines | Description |
|-----------|-------|-------------|
| 00 | 461-485 | Fully taxed |
| 02 | 487-500 | Monophasic on fuels |
| 10 | 503-564 | Taxed + ICMS ST |
| 15 | 567-596 | Monophasic + retention on fuels |
| 20 | 599-638 | Reduced base |
| 30 | 641-681 | Exempt + ICMS ST |
| 40/41/50 | 684-695 | Exempt / Not taxed / Suspended |
| 51 | 698-715 | Deferral |
| 53 | 718-740 | Monophasic deferred on fuels |
| 60/ST | 743-766 | Previously charged by ST |
| 61 | 769-781 | Monophasic previously charged on fuels |
| 70 | 784-851 | Reduced base + ICMS ST |
| 90 | 854-926 | Other |
| 101 | 931-940 | Simples Nacional with credit |
| 102/103/300/400 | 947-950 | Simples Nacional without credit |
| 201/202/203 | 955-1000 | Simples Nacional + ICMS ST |
| 500 | 1003-1006 | SN previously charged by ST |
| 900 | 1009-1071 | SN Other |

### Payment Serializers
| Method | Lines | Purpose |
|--------|-------|---------|
| `_serializar_pagamentos_antigo_deprecado()` | 1503-1522 | Legacy payment (deprecated) |
| `_serializar_pagamentos()` | 1524-1553 | Current payment serialization |

### NF-e Assembly Detail (`_serializar_nota_fiscal`)
| Section | Lines | XML tags |
|---------|-------|----------|
| IDE (identification) | 1496-1551 | `<ide>` cUF, cNF, natOp, mod, serie, nNF, dhEmi, tpNF, cMunFG, **cMunFGIBS**, etc. |
| Referenced NF-e | 1553-1589 | `<NFref>` refNFe, refNF, refNFP, refCTe |
| Contingency | 1591-1600 | dhCont, xJust |
| Emitter | 1645 | `<emit>` |
| Customer | 1605-1616 | `<dest>` |
| Withdrawal/Delivery | 1618-1635 | `<retirada>`, `<entrega>` |
| Authorized XML | 1638-1639 | `<autXML>` |
| Items | 1641-1648 | `<det>` with nItem |
| Totals (ICMSTot) | 1650-1743 | `<total><ICMSTot>` all legacy tax totals |
| **Totals (IBSCBSTot)** | 1827-1883 | `<total><IBSCBSTot>` Reforma Tributaria totals (vBCIBSCBS, gIBS, gCBS, gTribSN) |
| Transport | 1792-1835 | `<transp>` modFrete, carrier, vehicle, volumes |
| Billing | ~1837-1857 | `<cobr>` fat, dup |
| Payment | ~1859-1887 | `<pag>` detPag |
| Additional info | ~1889-1902 | `<infAdic>` |
| Technical responsible | ~1904-1910 | `<infRespTec>` |

---

## `SerializacaoQrcode` — Lines 2152-2252

Generates NFC-e QR Code URL. Handles online/offline modes and state-specific URL patterns (SP, BA, MG, etc.).

## `SerializacaoQrcodeMDFe` — Lines 2255-2278

Generates MDF-e QR Code URL using SVRS endpoint.

## `SerializacaoMDFe` — Lines 2281-2748

### Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `exportar()` | 2286-2312 | Main entry: exports MDF-e XML |
| `_serializar_emitente()` | 2320-2352 | MDF-e issuer (CPF/CNPJ, IE, address) |
| `_serializar_municipio_carrega()` | 2354-2364 | Loading municipality |
| `_serializar_percurso()` | 2366-2373 | Route (UF waypoints) |
| `_serializar_modal_rodoviario()` | 2375-2534 | **Road modal** (ANTT, CIOT, tolls, contractors, traction vehicle, trailer) |
| `_serializar_documentos()` | 2536-2560 | Linked documents (NF-e or CT-e) |
| `_serializar_seguradora()` | 2562-2582 | Insurance info |
| `_serializar_produto()` | 2584-2594 | Predominant product |
| `_serializar_totais()` | 2596-2616 | Totals (weight, qty) |
| `_serializar_lacres()` | 2618-2625 | Seals |
| `_serializar_responsavel_tecnico()` | 2627-2639 | Technical responsible |
| `_serializar_manifesto()` | 2641-2748 | **Main MDF-e assembly** (ide, emit, modal, doc, seg, prod, tot, lacres, infAdic, infRespTec) |
