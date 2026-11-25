# Source Map: `pynotas/utils/__init__.py` (251 lines)

Utility functions for municipality/country lookups, XML signing, and helpers.

## Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| `so_numeros()` | 20-30 | Extract only digits from string |
| `obter_pais_por_codigo()` | 31-61 | Get country name by code (default: 1058=Brasil) |
| `normalizar_municipio()` | 62-69 | Normalize municipality name (remove accents, uppercase) |
| `carregar_arquivo_municipios()` | 70-99 | Load IBGE municipality file for a given UF |
| `carregar_arquivo_pais()` | 165-174 | Load country code file |
| `obter_municipio_por_codigo()` | 110-121 | Get municipality name by IBGE code + UF |
| `obter_codigo_por_municipio()` | 100-109 | Get IBGE code by municipality name + UF |
| `obter_municipio_e_codigo()` | 122-141 | Get both municipality name and code |
| `assinar_com_a1()` | ~190-228 | Sign XML using A1 digital certificate |
| `validar_xml()` | ~230-251 | Validate XML against XSD schema |

## Constants

| Constant | Lines | Purpose |
|----------|-------|---------|
| `CAMINHO_DATA` | 44 | Path to `pynotas/data/` directory |
| `CAMINHO_MUNICIPIOS` | 45 | Path to `pynotas/data/MunIBGE/` |
| `CARACTERS_ACENTUADOS` | 44-58 | Accent character translation table |
