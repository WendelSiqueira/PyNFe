# Source Map: `webservices.py` (542 lines)

SEFAZ webservice endpoint URLs organized by document type, state, and environment.

## Sections

| Section | Lines | Variable | Purpose |
|---------|-------|----------|---------|
| NFC-e endpoints | 8-292 | `NFCE` | NFC-e webservice URLs and QR Code URLs by state |
| NF-e endpoints | 294-468 | `NFE` | NF-e webservice URLs by state |
| MDF-e endpoints | 472-487 | `MDFE` | MDF-e URLs (SVRS only) |
| CT-e endpoints | 489-543 | `CTE` | CT-e URLs by state |

## URL Structure

Each state/virtual environment entry contains:
- `STATUS` — Service status check endpoint
- `AUTORIZACAO` — Authorization endpoint
- `RECIBO` — Receipt query endpoint
- `CHAVE` — Access key query endpoint
- `INUTILIZACAO` — Number invalidation endpoint
- `EVENTOS` — Event reception endpoint
- `CADASTRO` — Registration query endpoint (some states)
- `HTTPS` — Production base URL prefix
- `HOMOLOGACAO` — Homologation base URL prefix
- `QR` — QR Code URL (NFC-e only)
- `URL` — Consultation URL (NFC-e only)

## State/Virtual Environment Groups

### NFC-e (`NFCE`) — Lines 8-292
| Key | Lines | Description |
|-----|-------|-------------|
| Individual states | 9-275 | RO, AC, AM, RR, PA, AP, TO, MA, PI, CE, RN, PB, PE, AL, SE, BA, MG, ES, RJ, SP, PR, SC, RS, MS, MT, GO, DF |
| `SVRS` | 284-294 | Virtual SEFAZ RS (fallback for states without own NFC-e) |

### NF-e (`NFE`) — Lines 294-468
| Key | Lines | Description |
|-----|-------|-------------|
| `AN` | 302-309 | National environment (events, distribution) |
| Individual states | 307-425 | AM, MA, PE, BA, MG, SP, PR, RS, MS, MT, GO |
| `SVAN` | 430-440 | Virtual SEFAZ AN (MA for NF-e) |
| `SVRS` | 441-451 | Virtual SEFAZ RS (most states) |
| `SVC-AN` | 449-457 | Contingency AN |
| `SVC-RS` | 458-467 | Contingency RS |

### MDF-e (`MDFE`) — Lines 472-487
Only `SVRS` — single authorizer for all states.

### CT-e (`CTE`) — Lines 489-543
| Key | Lines | Description |
|-----|-------|-------------|
| `AN` | 493-497 | National environment (distribution) |
| Individual states | 495-529 | MT, MS, MG, PR, RS, SP |
| `SVRS` | 534-539 | Virtual SEFAZ RS |
| `SVSP` | 540-545 | Virtual SEFAZ SP (AP, PE, RR) |
