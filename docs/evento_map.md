# Source Map: `evento.py` (235 lines)

Event entity models for NF-e and MDF-e lifecycle operations.

## Classes Overview

| Class | Lines | Purpose |
|-------|-------|---------|
| `Evento` | 9-44 | Base event class |
| `EventoCancelarNota` | 47-58 | NF-e cancellation (tp_evento=110111) |
| `EventoCartaCorrecao` | 61-88 | NF-e correction letter (tp_evento=110110) |
| `EventoManifestacaoDest` | 91-131 | Recipient manifestation (confirm/unknown/not performed/unaware) |
| `EventoOperacaoNaoRealizada` | ~130-143 | Operation not performed |
| `EventoCancelarMDFe` | ~145-158 | MDF-e cancellation |
| `EventoEncerrarMDFe` | ~160-178 | MDF-e closure |
| `EventoIncluirCondutorMDFe` | ~180-193 | Add driver to MDF-e |
| `EventoIncluirDFeMDFe` | ~195-213 | Add DF-e to MDF-e |
| `EventoPagamentoMDFe` | ~215-235 | MDF-e operation payment |

## `Evento` (base) — Lines 9-44

Fields: `id`, `orgao`, `cnpj`, `chave`, `data_emissao`, `uf`, `tp_evento`, `n_seq_evento`, `descricao`.

Property `identificador` builds: `"ID" + tp_evento + chave + n_seq_evento(2 digits)`.

## Key Event Types

| Class | tp_evento | descricao |
|-------|-----------|-----------|
| `EventoCancelarNota` | 110111 | "Cancelamento" |
| `EventoCartaCorrecao` | 110110 | "Carta de Correcao" |
| `EventoManifestacaoDest` | 91-131 | Various manifestation types |
| `EventoOperacaoNaoRealizada` | 110112 | "Operacao nao Realizada" |
| `EventoCancelarMDFe` | 110111 | "Cancelamento" (MDF-e) |
| `EventoEncerrarMDFe` | 110112 | "Encerramento" |
| `EventoIncluirCondutorMDFe` | 110114 | "Inclusão Condutor" |
| `EventoIncluirDFeMDFe` | 110115 | "Inclusao DF-e" |
| `EventoPagamentoMDFe` | 110116 | "Pagamento Operacao MDF-e" |
