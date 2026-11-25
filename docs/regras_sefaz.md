# Regras da SEFAZ

## O que a lib valida

A lib levanta `ValueError` antes de gerar o XML em dois casos:

1. **O XML ficaria inválido pelo schema.** Exemplos: `gRed` sem `pAliqEfet`, ou `gTribSN` sem `gCBSSN`.
2. **A lib teria que inventar dados.** Exemplo: CST de IBS/CBS tributado sem base nem alíquotas. Antes, a lib preenchia o `gIBSCBS` com `0.00` por conta própria.

**Regras de negócio da SEFAZ (rejeições) não são barradas pela lib.** Elas mudam por nota técnica e podem variar entre UFs e modelos, então quem valida é a SEFAZ. A aplicação que usa a lib pode checá-las antes do envio. As que já verificamos estão abaixo.

## Rejeições verificadas em homologação

Verificadas emitindo NF-e (modelo 55) na SEFAZ-SP, em homologação, com emitente do Simples Nacional - MEI (`CRT=4`).

| cStat | Motivo | Causa | Como evitar |
|-------|--------|-------|-------------|
| 442 | Descrição do pagamento não permitida | `xPag` informado com `tPag` diferente de 99 | Informar `x_pag` apenas com `t_pag="99"` (Outros). Com `tPag=99` e `xPag`, a nota foi autorizada |
| 1022 | Grupo gIBSCBS não informado | `gTribSN` sem `gIBSCBS` | A lib sempre emite o `gIBSCBS` para CST tributado |
| 1026 | Alíquota do IBS da UF inválida | `gIBSCBS` com alíquotas zeradas | Informar base e alíquotas (a lib recusa o grupo sem valores) |

### Ainda não verificadas

| cStat | Motivo | Causa | Fonte |
|-------|--------|-------|-------|
| 441 | Descrição do pagamento obrigatória para meio de pagamento 99-outros | `tPag=99` sem `xPag` | Par da 442, citado com ela na NT 2020.006 por fontes de terceiros |

A regra do `xPag` vem da NT 2020.006, segundo fontes de terceiros; o texto oficial da nota técnica não foi conferido.

Mais detalhes sobre IBS/CBS em [reforma_tributaria.md](reforma_tributaria.md).
