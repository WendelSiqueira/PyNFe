# Source Map: `manifesto.py` (446 lines)

Entity models for MDF-e (Manifesto de Documentos Fiscais Eletrônicos).

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Manifesto` | 11-228 | Main MDF-e entity |
| `ManifestoEmitente` | 368-415 | MDF-e issuer |
| `ManifestoMunicipioCarrega` | 231-236 | Loading municipality |
| `ManifestoPercurso` | 239-241 | Route waypoint (UF) |
| `ManifestoModalRodoviario` | ~249-289 | Road transport modal |
| `ManifestoCIOT` | 254-256 | CIOT (toll system) |
| `ManifestoPedagio` | 259-263 | Toll information |
| `ManifestoContratante` | 266-270 | Contractor info |
| `ManifestoVeiculoTracao` | 273-284 | Traction vehicle |
| `ManifestoVeiculoReboque` | 287-296 | Trailer vehicle |
| `ManifestoProprietario` | ~386-399 | Vehicle owner |
| `ManifestoCondutor` | 299-301 | Driver |
| `ManifestoDocumentos` | 304-312 | Linked documents (NF-e/CT-e) |
| `ManifestoSeguradora` | 323-340 | Insurance |
| `ManifestoTotais` | 418-433 | Totals (weight, cargo value) |

## `Manifesto` — Lines 11-228

### Field Groups
| Section | Lines | Fields |
|---------|-------|--------|
| Identity | 11-67 | uf, tipo_emitente, tipo_transportador, modelo (58), serie, numero_mdfe, codigo_numerico_aleatorio, modal, data_emissao, forma_emissao, processo_emissao, UFIni, UFFim |
| Read-only | 64-71 | digest_value, protocolo, data |
| Relationships | 73-109 | municipio_carrega, percurso, dhIniViagem, emitente, modal_rodoviario, documentos, seguradora, produto, totais, lacres, responsavel_tecnico |
| Additional info | ~111-119 | informacoes_adicionais_interesse_fisco, informacoes_complementares_interesse_contribuinte |

### Methods
| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__()` | 110-119 | Initialize all list fields |
| `adicionar_*()` | ~141-184 | Add municipio_carrega, percurso, emitente, modal_rodoviario, documento, seguradora, produto, totais, lacre, responsavel_tecnico |
| `_codigo_numerico_aleatorio()` | 170-172 | Generate random 8-digit code |
| `_dv_codigo_numerico()` | 174-199 | Calculate check digit (mod 11) |
| `identificador_unico` (property) | ~200+ | Build 44-char MDF-e access key |
