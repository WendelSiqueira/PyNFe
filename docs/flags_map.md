# Source Map: `flags.py` (679 lines)

Constants, namespaces, tax code enumerations, and state codes used throughout pyNotas.

## Sections

| Section | Lines | Purpose |
|---------|-------|---------|
| Namespaces | 1-22 | XML namespaces for NF-e, MDF-e, CT-e, SOAP, signatures |
| XSD paths | 24-37 | Paths to XML Schema files |
| ICMS types | 40-82 | `ICMS_TIPOS_TRIBUTACAO` — all CST/CSOSN codes |
| ICMS origins | 84-121 | `ICMS_ORIGENS` — product origin codes (0-8) |
| ICMS modalities | 123-138 | `ICMS_MODALIDADES` and `ICMS_ST_MODALIDADES` |
| ICMS exemption reasons | 140-159 | `ICMS_MOTIVO_DESONERACAO` |
| NF-e status | 161-180 | `NF_STATUS` and `MDFE_STATUS` tuples |
| NF-e enumerations | 182-246 | Document types, emission processes, DANFE types, payment forms, emission forms, **emission purposes (incl. finNFe 5/6)**, referenced types, specific products, environments |
| IPI types | 248-268 | `IPI_TIPOS_TRIBUTACAO` and `IPI_TIPOS_CALCULO` |
| PIS types | 270-405 | `PIS_TIPOS_TRIBUTACAO` — all CST codes (01-99) |
| COFINS types | 409-546 | `COFINS_TIPOS_TRIBUTACAO` — all CST codes (01-99) |
| Reforma Tributaria | 548-580 | `IBS_CBS_TIPOS_TRIBUTACAO` (15 CSTs, 3-digit) and `IS_TIPOS_TRIBUTACAO` (7 CSTs, 2-digit) — IVA Dual (EC 132/2023) |
| Freight modalities | 582-589 | `MODALIDADES_FRETE` (0-9) |
| Process origins | 591-597 | `ORIGENS_PROCESSO` |
| State codes | 599-631 | `CODIGOS_ESTADOS` — UF to IBGE code mapping |
| Card brands | 633-662 | `BANDEIRA_CARTAO` (01-99) |
| Payment methods | 664-679 | `FORMAS_PAGAMENTO` (01-99) |

## Key Constants

| Constant | Value | Used For |
|----------|-------|----------|
| `NAMESPACE_NFE` | `http://www.portalfiscal.inf.br/nfe` | NF-e XML |
| `NAMESPACE_MDFE` | `http://www.portalfiscal.inf.br/mdfe` | MDF-e XML |
| `NAMESPACE_CTE` | `http://www.portalfiscal.inf.br/cte` | CT-e XML |
| `VERSAO_PADRAO` | `4.00` | NF-e version |
| `VERSAO_MDFE` | `3.00` | MDF-e version |
| `VERSAO_CTE` | `3.00` | CT-e version |
| `VERSAO_QRCODE` | `2` | QR Code version |
| `CODIGO_BRASIL` | `1058` | Country code for Brazil |
