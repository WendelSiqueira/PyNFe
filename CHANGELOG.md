# Changelog

## Não publicado

### Novo

- **Intermediador da transação** (marketplace, NT 2020.006): grupo `infIntermed` com `intermediador_cnpj` e `intermediador_id_cadastro`. Até a 0.8.0, uma venda com `indicador_intermediador=1` saía sem o grupo e era rejeitada com 438. Verificado em homologação SP com a Shopee, dentro da UF e interestadual.
- `indIntermed` passa a ser emitido também na venda presencial quando há intermediador, como a NT permite.

## 0.8.0 — 2026-11-25

Primeira versão publicada como `pynotas-br`. O import continua `pynotas`.

### Novo

- **CEST** no produto, com indicador de escala relevante (`ind_escala`) e CNPJ do fabricante (`cnpj_fabricante`).
- **Verificação TLS** dos servidores da SEFAZ, que antes era desligada. Usa as CAs do `certifi` e as da ICP-Brasil, que vêm com a lib. Parâmetro `verificar_ssl` em `Comunicacao`.
- **XSDs no pacote**: a validação de schema funciona com a lib instalada como dependência.
- **Tabela oficial de CST de IBS/CBS** (calculadora RTC da Receita, IT 2025.002 v1.71), com os grupos exigidos por CST (`flags.IBS_CBS_CST_GRUPOS`).
- **Ferramenta de homologação** (`scripts/homologacao.py`): status, cadastro, emissão, consulta, carta de correção, cancelamento e inutilização contra a SEFAZ, sempre em homologação.
- `docs/regras_sefaz.md`: o que a lib valida e as rejeições verificadas em homologação.

### Corrigido

- A tabela de CST de IBS/CBS vinha errada (222 tratado como isenção, CSTs inexistentes e faltando), e o `gIBSCBS` era emitido ou omitido para os CSTs errados.
- O `gIBSCBS` passa a ser emitido junto com o `gTribSN`. A SEFAZ rejeita sem ele (1022) e com ele zerado (1026).
- Removidos dois `print()` que mostravam o XML assinado enviado à SEFAZ.

### Mudanças que podem quebrar código

- Removido o suporte a **NFS-e** (Betha, Ginfes e PyXB).
- CST de IBS/CBS que exige um grupo ainda não implementado (monofásico, transferência de crédito, ZFM, ajuste e diferimento) levanta `NotImplementedError`.
- CST tributado sem base nem alíquotas levanta `ValueError`, em vez de gerar um `gIBSCBS` zerado.

### Avisos

- `FutureWarning` na autorização assíncrona e na inutilização em AC, BA e SP (NT 2023.002).

## 0.7.0 — 2026-11-25

- Projeto renomeado de PyNFe para **pyNotas** (`import pynotas`).
- Schemas da NF-e no pacote **PL_010h** (Reforma Tributária).
- Novos grupos `gRed` (redução de alíquota) e `gTribSN` (Simples Nacional).
- Dependências gerenciadas com `uv`.
