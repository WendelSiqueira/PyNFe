# AGENTS.md - pyNotas

Brazilian electronic fiscal document library (NF-e, NFC-e, MDF-e, CT-e) for SEFAZ webservice communication.

## Source Map Navigation (MANDATORY)

**Before reading any large file (>200 lines), you MUST first read its `{filename}_map.md` file** in the `docs/` directory. The source map contains:
- Section-by-section breakdown with exact line ranges
- Class/method index with purpose descriptions
- Field group documentation

This allows you to navigate directly to the specific line-window you need instead of reading the entire file.

### Available Source Maps

| Source Map | File | Lines | Description |
|------------|------|-------|-------------|
| `docs/serializacao_map.md` | `pynotas/processamento/serializacao.py` | 2747 | XML serialization (NF-e, MDF-e, QR codes) |
| `docs/comunicacao_map.md` | `pynotas/processamento/comunicacao.py` | 1102 | SEFAZ webservice communication |
| `docs/notafiscal_map.md` | `pynotas/entidades/notafiscal.py` | 1306 | Invoice entities and tax fields |
| `docs/manifesto_map.md` | `pynotas/entidades/manifesto.py` | 446 | MDF-e manifest entities |
| `docs/evento_map.md` | `pynotas/entidades/evento.py` | 235 | Event entities (cancel, correction, etc.) |
| `docs/flags_map.md` | `pynotas/utils/flags.py` | 679 | Constants, namespaces, tax codes |
| `docs/webservices_map.md` | `pynotas/utils/webservices.py` | 542 | SEFAZ endpoint URLs by state |
| `docs/utils_map.md` | `pynotas/utils/__init__.py` | 251 | Utility functions (municipality lookup, signing) |

### How to Use Source Maps

1. **Read the `_map.md` file first** to understand the file structure
2. **Identify the line range** you need from the map tables
3. **Read only that section** using `offset` and `limit` parameters
4. Example: To understand ICMS CST 60 serialization, read `docs/serializacao_map.md`, find it's at lines 747-770, then read `pynotas/processamento/serializacao.py` with `offset=747, limit=25`

## Project Structure

```
docs/                   # Documentation and source maps (*_map.md, reforma_tributaria.md)
pynotas/
├── entidades/          # Domain entities (data models)
│   ├── base.py         # Base entity class with kwargs init
│   ├── certificado.py  # A1 certificate handling
│   ├── cliente.py      # Customer entity
│   ├── emitente.py     # Issuer entity
│   ├── evento.py       # Event entities (cancel, correction, MDF-e events)
│   ├── manifesto.py    # MDF-e manifest entity
│   ├── notafiscal.py   # NF-e/NFC-e invoice entity + products + taxes
│   ├── produto.py      # Product entity (standalone)
│   └── transportadora.py  # Carrier entity
├── processamento/      # Core processing logic
│   ├── assinatura.py   # XML digital signing with A1 certificates
│   ├── comunicacao.py  # SEFAZ SOAP webservice communication
│   ├── serializacao.py # XML serialization (entities → SEFAZ XML)
│   └── validacao.py    # XML schema validation
├── utils/              # Utilities
│   ├── __init__.py     # Municipality lookup, XML signing helpers
│   ├── flags.py        # Constants, namespaces, tax code enumerations
│   ├── webservices.py  # SEFAZ endpoint URLs by state/environment
│   ├── bar_code_128.py # Code 128 barcode generation for DANFE
│   └── xml_writer.py   # XML element writing helpers
├── data/               # Reference data files
│   ├── IBPT/           # Tax tables by state (CSV)
│   ├── ISSQN/          # Service tax classification
│   ├── MunIBGE/        # Municipality IBGE codes by UF
│   └── XSDs/           # XML Schema definitions (NF-e, NFC-e, MDF-e, CT-e)
tests/                  # Test suite
```

## Key Concepts

- **NF-e** (modelo 55): Standard electronic invoice
- **NFC-e** (modelo 65): Consumer electronic invoice (retail)
- **MDF-e** (modelo 58): Transport manifest
- **CT-e**: Transport knowledge document (partial support)
- **NFS-e**: not supported (Betha/Ginfes providers were removed)
- **SEFAZ**: State tax authority webservices
- **Homologacao**: Test environment (`_ambiente=2`)
- **SVRS/SVAN**: Virtual SEFAZ environments for states without own webservices

## Commands

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

```bash
# Install (dev group is included by default)
uv sync

# Run tests
uv run pytest tests/

# Run specific test
uv run pytest tests/test_nfe_serializacao_geral.py

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## Dependencies

- `lxml` — XML processing
- `signxml` — XML digital signatures
- `cryptography` / `pyopenssl` — Certificate handling
- `requests` — HTTP communication with SEFAZ

## Important Notes

- The `pynotas/data/` directory contains reference data files that should not be modified casually
- Tax code serialization follows strict SEFAZ XML schema ordering — field order matters
- Each Brazilian state has its own SEFAZ endpoint configuration in `webservices.py`
