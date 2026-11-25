# Source Map: `comunicacao.py` (1113 lines)

SEFAZ webservice communication for NF-e, NFC-e, MDF-e and CT-e.

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Comunicacao` | 30-46 | Abstract base class |
| `ComunicacaoSefaz` | 49-611 | NF-e/NFC-e SEFAZ communication |
| `ComunicacaoMDFe` | 614-884 | MDF-e SEFAZ communication |
| `ComunicacaoCTe` | 887-1113 | CT-e SEFAZ communication |

---

## `Comunicacao` (base) — Lines 30-46

Stores `uf`, `certificado`, `certificado_senha`, `_ambiente` (1=prod, 2=homolog).

## `ComunicacaoSefaz` — Lines 49-611

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `autorizacao()` | 55-129 | Send NF-e for authorization (sync/async) |
| `consulta_recibo()` | 131-154 | Query batch processing result |
| `consulta_nota()` | 156-174 | Query NF-e status by access key |
| `consulta_distribuicao()` | 176-230 | DF-e distribution query (distNSU, consNSU, consChNFe) |
| `consulta_cadastro()` | 232-291 | Taxpayer registration query |
| `evento()` | 293-319 | Send NF-e events (cancel, correction letter) |
| `status_servico()` | 321-334 | Check SEFAZ server status |
| `inutilizacao()` | 336-409 | Number range invalidation |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_get_url_an()` | 411-423 | Get national environment URL (AN) |
| `_get_url()` | 425-550 | **URL resolver** — routes to correct SEFAZ by UF, model, environment, contingency |
| `_construir_xml_soap()` | 552-569 | Build SOAP XML envelope |
| `_post_header()` | 571-580 | HTTP headers (PE requires SOAPAction) |
| `_post()` | 582-611 | Execute HTTPS POST with A1 certificate |

### URL Routing Detail (`_get_url`)
| Section | Lines | States |
|---------|-------|--------|
| Contingency SVRS | 428-461 | AM, BA, CE, GO, MA, MS, MT, PE, PR |
| Contingency SVAN | 462-475 | AC, AL, AP, DF, ES, MG, PA, PB, PI, RJ, RN, RO, RR, RS, SC, SE, SP, TO |
| Own webservices | 479-500 | PR, MS, SP, AM, CE, BA, GO, MG, MT, PE, RS |
| SVRS states | 503-532 | AC, AL, AP, DF, ES, PB, PI, RJ, RN, RO, RR, SC, SE, TO, PA |
| SVAN (MA only) | 535-547 | MA |

---

## `ComunicacaoMDFe` — Lines 614-884

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `autorizacao()` | 640-722 | Send MDF-e for authorization (sync/async) |
| `status_servico()` | 724-731 | Check MDF-e server status |
| `consulta()` | 733-742 | Query MDF-e by access key |
| `consulta_nao_encerrados()` | 744-756 | Query non-closed MDF-e |
| `consulta_recibo()` | 758-766 | Query batch processing result |
| `evento()` | 768-783 | Send MDF-e events (cancel, close, add driver, add DF-e, payment) |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_construir_xml_soap()` | 785-810 | Build SOAP XML with header |
| `_post_header()` | 812-827 | HTTP headers |
| `_post()` | 829-865 | Execute HTTPS POST with cert |
| `_cabecalho_soap()` | 867-873 | SOAP header with cUF and versaoDados |
| `_get_url()` | 875-884 | URL resolver (SVRS only) |

---

## `ComunicacaoCTe` — Lines 887-1113

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `status_servico()` | 902-913 | Check CT-e server status |
| `consulta_distribuicao()` | 915-966 | CT-e distribution query |
| `consulta()` | 968-977 | Query CT-e by access key |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_get_url_an()` | 979-985 | National environment URL |
| `_cabecalho_soap()` | 987-993 | SOAP header |
| `_get_url()` | 995-1047 | **URL resolver** — own (MT, MS, MG, PR, RS, SP), SVRS, SVSP |
| `_construir_xml_soap()` | 1049-1070 | Build SOAP XML envelope |
| `_post_header()` | 1072-1079 | HTTP headers |
| `_post()` | 1081-1114 | Execute HTTPS POST with cert |
