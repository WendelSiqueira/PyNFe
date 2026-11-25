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
| 539 | Duplicidade de NF-e com diferença na Chave de Acesso | Número já usado na mesma série (a resposta traz a chave da nota existente) | Controlar a numeração por série no emissor; não há serviço para consultar o último número |
| 438 | Obrigatória as informações do intermediador da transação para operação por site de terceiros | `indIntermed=1` sem o grupo `infIntermed` (era o que a lib até a 0.8.0 gerava) | Informar `intermediador_cnpj` e `intermediador_id_cadastro` |
| 879 | Informado item "Produzido em Escala NÃO Relevante" e não informado CNPJ do Fabricante | `indEscala="N"` sem `CNPJFab` | Com `ind_escala="N"`, informar `cnpj_fabricante` |
| 1022 | Grupo gIBSCBS não informado | `gTribSN` sem `gIBSCBS` | A lib sempre emite o `gIBSCBS` para CST tributado |
| 1026 | Alíquota do IBS da UF inválida | `gIBSCBS` com alíquotas zeradas | Informar base e alíquotas (a lib recusa o grupo sem valores) |

### Eventos e consultas verificados

Na mesma nota, em homologação SP:

| Operação | Resultado |
|----------|-----------|
| Consulta da NF-e | 100 - Autorizado o uso da NF-e |
| Carta de correção | 135 - Evento registrado e vinculado a NF-e |
| Cancelamento | 135 - Evento registrado e vinculado a NF-e |
| Consulta após o cancelamento | 101 - Cancelamento de NF-e homologado |
| Inutilização de numeração | **998 - Serviço Desativado** (ver abaixo) |
| Emissão com CEST, com `indEscala` S e com `indEscala` N + `CNPJFab` | 100 - Autorizado o uso da NF-e |
| Venda pela internet sem intermediador (`indPres=2`, `indIntermed=0`) | 100 - Autorizado o uso da NF-e |
| Venda por marketplace (Shopee, CNPJ 35.635.824/0001-12) dentro da UF e interestadual (CFOP 6102) | 100 - Autorizado o uso da NF-e |

### Fim da inutilização e da autorização assíncrona (NT 2023.002)

A NT 2023.002 v1.02 (outubro de 2026) desativa o serviço de inutilização de numeração no AC, na BA e em SP, com retorno HTTP 404 ou rejeição 998 ("Serviço Desativado"), e elimina a autorização assíncrona (`indSinc=0`) até 01/02/2027. Em SP, havendo salto na numeração, segue-se a partir do número seguinte, sem pedir inutilização. A rejeição 998 foi confirmada em homologação SP; as datas e o alcance vêm de resumos da NT por terceiros e devem ser conferidos na NT oficial.

Para quem usa a lib: emita com `ind_sinc=1` (autorização síncrona, o padrão de `autorizacao()`), e não dependa de `inutilizacao()` nas UFs afetadas.

### Regras do `xPag` (NT 2020.006)

As regras do `xPag` estão na Nota Técnica 2020.006 (versão 1.31, setembro de 2022), valem para NF-e e NFC-e (modelos 55 e 65) em todas as UFs, desde 01/09/2021 em produção:

| Regra | cStat | Texto da NT | Verificada em homologação |
|-------|-------|-------------|---------------------------|
| YA02a-10 | 441 | Quando o código do meio de pagamento (tag: tPag) for preenchido com o código 99-outros, obrigatório o preenchimento da descrição do meio de pagamento (tag: xPag) | não |
| YA02a-20 | 442 | Quando o código do meio de pagamento for diferente 99-outros (tag: tPag<>99), proibido o preenchimento da descrição do meio de pagamento (tag: xPag) | sim |

### Intermediador (NT 2020.006)

| Regra | cStat | O que exige |
|-------|-------|-------------|
| B25c-10 | 434 | `indIntermed` obrigatório em nota de saída normal com `indPres` 2, 3, 4 ou 9. A lib emite o campo sempre nesses casos |
| B25c-20 | 435 | `indIntermed=1` proibido com `indPres` 0 ou 5 |
| YB01-10 | 438 | Com `indIntermed=1`, o grupo `infIntermed` (CNPJ e `idCadIntTran`) é obrigatório (verificado em homologação) |
| YB01-20 | 439 | Sem intermediador, o grupo é proibido |
| YB02-10 | 440 | CNPJ do intermediador precisa ser válido |

## Onde está a documentação oficial

As regras de validação e os códigos de rejeição são publicados no Portal Nacional da NF-e (nfe.fazenda.gov.br): no Manual de Orientação do Contribuinte (MOC), anexo de leiaute e regras de validação, e nas Notas Técnicas, que alteram o MOC. Cada regra tem um código (por exemplo, YA02a-20), os modelos a que se aplica e o cStat da rejeição.

Mais detalhes sobre IBS/CBS em [reforma_tributaria.md](reforma_tributaria.md).
