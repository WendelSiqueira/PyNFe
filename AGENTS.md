# AGENTS.md - pyNotas

Brazilian electronic fiscal document library (NF-e, NFC-e, MDF-e, CT-e) for SEFAZ webservice communication.

## Navigating Large Files

`serializacao.py` (~2,700 lines), `notafiscal.py` and `comunicacao.py` are large. Find what you need by name instead of reading them whole, for example `grep -n "def _serializar_ibscbs" pynotas/processamento/serializacao.py`, then read only that range. XML tags appear literally in the serializer (`grep -n '"gTribSN"'`).

## Project Structure

```
docs/                   # Documentation (reforma_tributaria.md)
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
│   ├── tls.py          # TLS verification for SEFAZ (certifi + ICP-Brasil CAs)
│   └── xml_writer.py   # XML element writing helpers
├── data/               # Reference data files
│   ├── IBPT/           # Tax tables by state (CSV)
│   ├── certificados/   # ICP-Brasil CA chain (icp-brasil.pem), see scripts/
│   ├── ISSQN/          # Service tax classification
│   ├── MunIBGE/        # Municipality IBGE codes by UF
│   └── XSDs/           # XML Schema definitions (NF-e, NFC-e, MDF-e, CT-e)
scripts/                # Maintenance (atualizar_cadeia_icp_brasil.py)
tests/                  # Test suite (network tests need PYNOTAS_TESTES_REDE=1)
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
