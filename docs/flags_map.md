# Source Map: `flags.py` (686 lines)

Constants, namespaces, tax code enumerations, and state codes used throughout pyNotas.

## Sections

| Section | Lines | Purpose |
|---------|-------|---------|
| Namespaces | 1-23 | XML namespaces for NF-e, MDF-e, CT-e, SOAP, signatures |
| XSD paths | 25-44 | Paths to XML Schema files, absolute from the package (`XSD_FOLDER`, `XSD_FOLDER_NFE`, `XSD_FOLDER_MDFE`) |
| ICMS types | 47-89 | `ICMS_TIPOS_TRIBUTACAO` — all CST/CSOSN codes |
| ICMS origins | 91-128 | `ICMS_ORIGENS` — product origin codes (0-8) |
| ICMS modalities | 130-145 | `ICMS_MODALIDADES` and `ICMS_ST_MODALIDADES` |
| ICMS exemption reasons | 147-166 | `ICMS_MOTIVO_DESONERACAO` |
| NF-e status | 168-187 | `NF_STATUS` and `MDFE_STATUS` tuples |
| NF-e enumerations | 189-253 | Document types, emission processes, DANFE types, payment forms, emission forms, **emission purposes (incl. finNFe 5/6)**, referenced types, specific products, environments |
| IPI types | 255-275 | `IPI_TIPOS_TRIBUTACAO` and `IPI_TIPOS_CALCULO` |
| PIS types | 277-412 | `PIS_TIPOS_TRIBUTACAO` — all CST codes (01-99) |
| COFINS types | 416-553 | `COFINS_TIPOS_TRIBUTACAO` — all CST codes (01-99) |
| Reforma Tributaria | 555-587 | `IBS_CBS_TIPOS_TRIBUTACAO` (15 CSTs, 3-digit) and `IS_TIPOS_TRIBUTACAO` (7 CSTs, 2-digit) — IVA Dual (EC 132/2023) |
| Freight modalities | 589-596 | `MODALIDADES_FRETE` (0-9) |
| Process origins | 598-604 | `ORIGENS_PROCESSO` |
| State codes | 606-638 | `CODIGOS_ESTADOS` — UF to IBGE code mapping |
| Card brands | 640-669 | `BANDEIRA_CARTAO` (01-99) |
| Payment methods | 671-686 | `FORMAS_PAGAMENTO` (01-99) |

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
