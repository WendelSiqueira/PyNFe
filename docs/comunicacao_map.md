# Source Map: `comunicacao.py` (1102 lines)

SEFAZ webservice communication for NF-e, NFC-e, MDF-e and CT-e.

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Comunicacao` | 29-45 | Abstract base class |
| `ComunicacaoSefaz` | 48-608 | NF-e/NFC-e SEFAZ communication |
| `ComunicacaoMDFe` | 611-873 | MDF-e SEFAZ communication |
| `ComunicacaoCTe` | 876-1102 | CT-e SEFAZ communication |

---

## `Comunicacao` (base) — Lines 29-45

Stores `uf`, `certificado`, `certificado_senha`, `_ambiente` (1=prod, 2=homolog).

## `ComunicacaoSefaz` — Lines 48-608

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `autorizacao()` | 54-128 | Send NF-e for authorization (sync/async) |
| `consulta_recibo()` | 130-153 | Query batch processing result |
| `consulta_nota()` | 155-173 | Query NF-e status by access key |
| `consulta_distribuicao()` | 175-229 | DF-e distribution query (distNSU, consNSU, consChNFe) |
| `consulta_cadastro()` | 231-288 | Taxpayer registration query |
| `evento()` | 290-316 | Send NF-e events (cancel, correction letter) |
| `status_servico()` | 318-331 | Check SEFAZ server status |
| `inutilizacao()` | 333-406 | Number range invalidation |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_get_url_an()` | 408-420 | Get national environment URL (AN) |
| `_get_url()` | 422-547 | **URL resolver** — routes to correct SEFAZ by UF, model, environment, contingency |
| `_construir_xml_soap()` | 549-566 | Build SOAP XML envelope |
| `_post_header()` | 568-577 | HTTP headers (PE requires SOAPAction) |
| `_post()` | 579-608 | Execute HTTPS POST with A1 certificate |

### URL Routing Detail (`_get_url`)
| Section | Lines | States |
|---------|-------|--------|
| Contingency SVRS | 425-458 | AM, BA, CE, GO, MA, MS, MT, PE, PR |
| Contingency SVAN | 459-472 | AC, AL, AP, DF, ES, MG, PA, PB, PI, RJ, RN, RO, RR, RS, SC, SE, SP, TO |
| Own webservices | 476-497 | PR, MS, SP, AM, CE, BA, GO, MG, MT, PE, RS |
| SVRS states | 500-529 | AC, AL, AP, DF, ES, PB, PI, RJ, RN, RO, RR, SC, SE, TO, PA |
| SVAN (MA only) | 532-544 | MA |

---

## `ComunicacaoMDFe` — Lines 611-873

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `autorizacao()` | 637-717 | Send MDF-e for authorization (sync/async) |
| `status_servico()` | 719-726 | Check MDF-e server status |
| `consulta()` | 728-737 | Query MDF-e by access key |
| `consulta_nao_encerrados()` | 739-751 | Query non-closed MDF-e |
| `consulta_recibo()` | 753-761 | Query batch processing result |
| `evento()` | 763-778 | Send MDF-e events (cancel, close, add driver, add DF-e, payment) |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_construir_xml_soap()` | 780-802 | Build SOAP XML with header |
| `_post_header()` | 804-819 | HTTP headers |
| `_post()` | 821-854 | Execute HTTPS POST with cert |
| `_cabecalho_soap()` | 856-862 | SOAP header with cUF and versaoDados |
| `_get_url()` | 864-873 | URL resolver (SVRS only) |

---

## `ComunicacaoCTe` — Lines 876-1102

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `status_servico()` | 891-902 | Check CT-e server status |
| `consulta_distribuicao()` | 904-955 | CT-e distribution query |
| `consulta()` | 957-966 | Query CT-e by access key |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_get_url_an()` | 968-974 | National environment URL |
| `_cabecalho_soap()` | 976-982 | SOAP header |
| `_get_url()` | 984-1036 | **URL resolver** — own (MT, MS, MG, PR, RS, SP), SVRS, SVSP |
| `_construir_xml_soap()` | 1038-1059 | Build SOAP XML envelope |
| `_post_header()` | 1061-1068 | HTTP headers |
| `_post()` | 1070-1102 | Execute HTTPS POST with cert |
