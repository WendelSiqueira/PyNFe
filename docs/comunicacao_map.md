# Source Map: `comunicacao.py` (1103 lines)

SEFAZ webservice communication for NF-e, NFC-e, MDF-e and CT-e.

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Comunicacao` | 30-46 | Abstract base class |
| `ComunicacaoSefaz` | 49-609 | NF-e/NFC-e SEFAZ communication |
| `ComunicacaoMDFe` | 612-874 | MDF-e SEFAZ communication |
| `ComunicacaoCTe` | 877-1103 | CT-e SEFAZ communication |

---

## `Comunicacao` (base) — Lines 30-46

Stores `uf`, `certificado`, `certificado_senha`, `_ambiente` (1=prod, 2=homolog).

## `ComunicacaoSefaz` — Lines 49-609

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `autorizacao()` | 55-129 | Send NF-e for authorization (sync/async) |
| `consulta_recibo()` | 131-154 | Query batch processing result |
| `consulta_nota()` | 156-174 | Query NF-e status by access key |
| `consulta_distribuicao()` | 176-230 | DF-e distribution query (distNSU, consNSU, consChNFe) |
| `consulta_cadastro()` | 232-289 | Taxpayer registration query |
| `evento()` | 291-317 | Send NF-e events (cancel, correction letter) |
| `status_servico()` | 319-332 | Check SEFAZ server status |
| `inutilizacao()` | 334-407 | Number range invalidation |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_get_url_an()` | 409-421 | Get national environment URL (AN) |
| `_get_url()` | 423-548 | **URL resolver** — routes to correct SEFAZ by UF, model, environment, contingency |
| `_construir_xml_soap()` | 550-567 | Build SOAP XML envelope |
| `_post_header()` | 569-578 | HTTP headers (PE requires SOAPAction) |
| `_post()` | 580-609 | Execute HTTPS POST with A1 certificate |

### URL Routing Detail (`_get_url`)
| Section | Lines | States |
|---------|-------|--------|
| Contingency SVRS | 426-459 | AM, BA, CE, GO, MA, MS, MT, PE, PR |
| Contingency SVAN | 460-473 | AC, AL, AP, DF, ES, MG, PA, PB, PI, RJ, RN, RO, RR, RS, SC, SE, SP, TO |
| Own webservices | 477-498 | PR, MS, SP, AM, CE, BA, GO, MG, MT, PE, RS |
| SVRS states | 501-530 | AC, AL, AP, DF, ES, PB, PI, RJ, RN, RO, RR, SC, SE, TO, PA |
| SVAN (MA only) | 533-545 | MA |

---

## `ComunicacaoMDFe` — Lines 612-874

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `autorizacao()` | 638-718 | Send MDF-e for authorization (sync/async) |
| `status_servico()` | 720-727 | Check MDF-e server status |
| `consulta()` | 729-738 | Query MDF-e by access key |
| `consulta_nao_encerrados()` | 740-752 | Query non-closed MDF-e |
| `consulta_recibo()` | 754-762 | Query batch processing result |
| `evento()` | 764-779 | Send MDF-e events (cancel, close, add driver, add DF-e, payment) |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_construir_xml_soap()` | 781-803 | Build SOAP XML with header |
| `_post_header()` | 805-820 | HTTP headers |
| `_post()` | 822-855 | Execute HTTPS POST with cert |
| `_cabecalho_soap()` | 857-863 | SOAP header with cUF and versaoDados |
| `_get_url()` | 865-874 | URL resolver (SVRS only) |

---

## `ComunicacaoCTe` — Lines 877-1103

### Public Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `status_servico()` | 892-903 | Check CT-e server status |
| `consulta_distribuicao()` | 905-956 | CT-e distribution query |
| `consulta()` | 958-967 | Query CT-e by access key |

### Internal Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `_get_url_an()` | 969-975 | National environment URL |
| `_cabecalho_soap()` | 977-983 | SOAP header |
| `_get_url()` | 985-1037 | **URL resolver** — own (MT, MS, MG, PR, RS, SP), SVRS, SVSP |
| `_construir_xml_soap()` | 1039-1060 | Build SOAP XML envelope |
| `_post_header()` | 1062-1069 | HTTP headers |
| `_post()` | 1071-1103 | Execute HTTPS POST with cert |
