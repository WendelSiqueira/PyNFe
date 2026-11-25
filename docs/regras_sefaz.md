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

### Regras do `xPag` (NT 2020.006)

As regras do `xPag` estão na Nota Técnica 2020.006 (versão 1.31, setembro de 2022), valem para NF-e e NFC-e (modelos 55 e 65) em todas as UFs, desde 01/09/2021 em produção:

| Regra | cStat | Texto da NT | Verificada em homologação |
|-------|-------|-------------|---------------------------|
| YA02a-10 | 441 | Quando o código do meio de pagamento (tag: tPag) for preenchido com o código 99-outros, obrigatório o preenchimento da descrição do meio de pagamento (tag: xPag) | não |
| YA02a-20 | 442 | Quando o código do meio de pagamento for diferente 99-outros (tag: tPag<>99), proibido o preenchimento da descrição do meio de pagamento (tag: xPag) | sim |

## Onde está a documentação oficial

As regras de validação e os códigos de rejeição são publicados no Portal Nacional da NF-e (nfe.fazenda.gov.br): no Manual de Orientação do Contribuinte (MOC), anexo de leiaute e regras de validação, e nas Notas Técnicas, que alteram o MOC. Cada regra tem um código (por exemplo, YA02a-20), os modelos a que se aplica e o cStat da rejeição.

Mais detalhes sobre IBS/CBS em [reforma_tributaria.md](reforma_tributaria.md).
