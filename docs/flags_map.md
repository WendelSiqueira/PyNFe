# Source Map: `flags.py` (685 lines)

Constants, namespaces, tax code enumerations, and state codes used throughout pyNotas.

## Sections

| Section | Lines | Purpose |
|---------|-------|---------|
| Namespaces | 1-22 | XML namespaces for NF-e, MDF-e, CT-e, SOAP, signatures |
| XSD paths | 24-43 | Paths to XML Schema files, absolute from the package (`XSD_FOLDER`, `XSD_FOLDER_NFE`, `XSD_FOLDER_MDFE`) |
| ICMS types | 46-88 | `ICMS_TIPOS_TRIBUTACAO` — all CST/CSOSN codes |
| ICMS origins | 90-127 | `ICMS_ORIGENS` — product origin codes (0-8) |
| ICMS modalities | 129-144 | `ICMS_MODALIDADES` and `ICMS_ST_MODALIDADES` |
| ICMS exemption reasons | 146-165 | `ICMS_MOTIVO_DESONERACAO` |
| NF-e status | 167-186 | `NF_STATUS` and `MDFE_STATUS` tuples |
| NF-e enumerations | 188-252 | Document types, emission processes, DANFE types, payment forms, emission forms, **emission purposes (incl. finNFe 5/6)**, referenced types, specific products, environments |
| IPI types | 254-274 | `IPI_TIPOS_TRIBUTACAO` and `IPI_TIPOS_CALCULO` |
| PIS types | 276-411 | `PIS_TIPOS_TRIBUTACAO` — all CST codes (01-99) |
| COFINS types | 415-552 | `COFINS_TIPOS_TRIBUTACAO` — all CST codes (01-99) |
| Reforma Tributaria | 554-586 | `IBS_CBS_TIPOS_TRIBUTACAO` (15 CSTs, 3-digit) and `IS_TIPOS_TRIBUTACAO` (7 CSTs, 2-digit) — IVA Dual (EC 132/2023) |
| Freight modalities | 588-595 | `MODALIDADES_FRETE` (0-9) |
| Process origins | 597-603 | `ORIGENS_PROCESSO` |
| State codes | 605-637 | `CODIGOS_ESTADOS` — UF to IBGE code mapping |
| Card brands | 639-668 | `BANDEIRA_CARTAO` (01-99) |
| Payment methods | 670-685 | `FORMAS_PAGAMENTO` (01-99) |

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
