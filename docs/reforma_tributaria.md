# Reforma Tributaria - IBS/CBS (NT 2025.002-RTC)

Suporte ao IVA Dual brasileiro conforme a Emenda Constitucional 132/2023, Lei Complementar 214/2025 e Nota Tecnica NT 2025.002-RTC.

## Contexto

A Reforma Tributaria substitui gradualmente cinco tributos por um modelo de IVA Dual:

| Imposto | Tipo | Substitui | Competencia | Inicio |
|---------|------|-----------|-------------|--------|
| **CBS** (Contribuicao sobre Bens e Servicos) | Federal | PIS, COFINS | Uniao | 2026 (teste 0,9%) |
| **IBS** (Imposto sobre Bens e Servicos) | Subnacional | ICMS, ISS | Estados + Municipios | 2026 (teste 0,1% UF) |
| **IS** (Imposto Seletivo) | Extrafiscal | IPI (parcial) | Uniao | **2027** |

> **IBS e dividido em duas parcelas**: IBS-UF (estadual) e IBS-Mun (municipal), informadas separadamente no XML.

### Cronograma de transicao

- **2026**: Fase de testes — CBS 0,9%, IBS-UF 0,1%, IBS-Mun 0%. Obrigatorio para CRT=3.
- **2027**: CBS em aliquota plena. IS entra em vigor. Split Payment inicia.
- **2029-2032**: Reducao gradual de ICMS/ISS, aumento proporcional do IBS.
- **2033**: Extincao completa de ICMS, ISS, PIS, COFINS e IPI.

Durante a transicao, os impostos legados (ICMS, PIS, COFINS) **coexistem** com os novos (IBS, CBS) na mesma NF-e.

## Escopo da implementacao

A implementacao cobre:

- Grupo `<IBSCBS>` como filho direto de `<imposto>` (sem wrapper `<impostoMisto>`)
- CSTs de 3 digitos conforme NT 2025.002-RTC (ex: "000", "010", "222")
- `cClassTrib` (codigo de classificacao tributaria de 6 digitos)
- IBS dividido em `gIBSUF` e `gIBSMun`
- Base de calculo compartilhada (`vBC`) para IBS e CBS
- Totais em `<IBSCBSTot>` separado de `<ICMSTot>`
- `cMunFGIBS` no cabecalho (Group B)
- `vNF` **NAO inclui** IBS/CBS (proibido em 2025-2026)
- `finNFe=5` (Nota de Debito) e `finNFe=6` (Nota de Credito)
- Campos de entidade para IS (Imposto Seletivo) — **armazenados mas nao serializados** ate o schema suportar (2027)
- Reducao de aliquota per-item (`gRed`) em `gIBSUF`, `gIBSMun` e `gCBS`
- Simples Nacional (`gTribSN`) no item e nos totais (`IBSCBSTot/gTribSN`)
- Schemas validados contra o pacote oficial **PL_010h**

**Nao inclui** (ainda): Split Payment, cashback, eventos de apuracao assistida, Grupo VB (total do item), Grupo VC (referenciamento de DF-e), Grupo BB (antecipacao de pagamento), tributacao monofasica (`gIBSCBSMono`), diferimento per-item (`gDif`), devolucao de tributos per-item (`gDevTrib`), estorno de credito (`gEstornoCred`), credito presumido per-item (`gCredPresOper`, `gCredPresIBSZFM`).

## CSTs disponiveis

Tabelas oficiais da calculadora RTC da Receita Federal (base V0073: IT 2025.002 v1.71, publicada em 30/10/2026), em `pynotas.utils.flags`.

### IBS e CBS

```python
from pynotas.utils.flags import IBS_CBS_TIPOS_TRIBUTACAO, IBS_CBS_CST_GRUPOS
```

| CST | Descricao | Grupos exigidos | Na lib |
|-----|-----------|-----------------|--------|
| 000 | Tributação integral | gIBSCBS | sim |
| 010 | Tributação com alíquotas uniformes | gIBSCBS | sim |
| 011 | Tributação com alíquotas uniformes reduzidas | gIBSCBS, gRed | sim |
| 200 | Alíquota reduzida | gIBSCBS, gRed | sim |
| 220 | Alíquota fixa | gIBSCBS | sim |
| 221 | Alíquota fixa proporcional | gIBSCBS | sim |
| 222 | Redução de Base de Cálculo | gIBSCBS | sim |
| 400 | Isenção | — | sim |
| 410 | Imunidade e não incidência | — | sim |
| 510 | Diferimento | gIBSCBS, gDif | nao (gDif) |
| 515 | Diferimento com redução de alíquota | gIBSCBS, gRed, gDif | nao (gDif) |
| 550 | Suspensão | gIBSCBS | sim |
| 620 | Tributação monofásica | gIBSCBSMono | nao |
| 800 | Transferência de crédito | gTransfCred | nao |
| 810 | Ajustes de IBS na ZFM | gCredPresIBSZFM | nao |
| 811 | Ajustes | gAjusteCompet | nao |
| 820 | Tributação em documento específico | — | sim |
| 830 | Exclusão de base de cálculo | gIBSCBS | sim |

- `gIBSCBS` e emitido conforme a tabela. Para CST que exige um grupo que a lib ainda nao gera, a serializacao levanta `NotImplementedError`. CST fora da tabela gera um aviso e so CST + cClassTrib.
- `gRed` (reducao de aliquota) e informado pelo usuario (campos `ibscbs_p_red_aliq_*`); a lib nao bloqueia a falta dele nos CSTs 011, 200 e 515 (regra da SEFAZ).
- Alguns cClassTrib exigem grupos proprios, como `gTribRegular` (rejeicao 1065 em homologacao com o cClassTrib 550001), ainda nao implementado.
- O cClassTrib precisa ser permitido para o modelo do documento: em homologacao, cClassTrib de 400 e 222 (exportacao e transporte) foram rejeitados em NF-e com 1025.

### IS (Imposto Seletivo) — a partir de 2027

```python
from pynotas.utils.flags import IS_TIPOS_TRIBUTACAO
```

| CSTIS | Descricao |
|-------|-----------|
| 000 | Tributado com Imposto Seletivo |
| 100 | Imunidade |
| 200 | Não ocorrência do Fato Gerador |
| 300 | Devolução |
| 400 | Suspensão |
| 500 | Alíquota Zero |
| 600 | Isenção |

> **IS nao e serializado no XML em 2026.** Os campos de entidade (`is_*`) estao prontos; a serializacao fica desabilitada ate 2027.

## Como usar

### Exemplo: produto com IBSCBS (tributacao integral CST 000)

```python
from decimal import Decimal

nota_fiscal.adicionar_produto_servico(
    # ... campos obrigatorios do produto ...
    codigo="001",
    descricao="Produto exemplo",
    ncm="99999999",
    ean="SEM GTIN",
    cfop="5102",
    unidade_comercial="UN",
    quantidade_comercial=Decimal("10"),
    valor_unitario_comercial=Decimal("100.00"),
    valor_total_bruto=Decimal("1000.00"),
    unidade_tributavel="UN",
    quantidade_tributavel=Decimal("10"),
    valor_unitario_tributavel=Decimal("100.00"),
    ean_tributavel="SEM GTIN",
    ind_total=1,

    # ... impostos legados (ICMS, PIS, COFINS) continuam obrigatorios ...
    icms_modalidade="00",
    icms_origem=0,
    icms_csosn="",
    pis_modalidade="99",
    cofins_modalidade="99",
    pis_valor=Decimal("0.00"),
    cofins_valor=Decimal("0.00"),

    # IBSCBS — Group UB
    ibscbs_cst="000",                           # CST 3 digitos
    ibscbs_c_class_trib="000001",               # cClassTrib 6 digitos
    ibscbs_vbc=Decimal("1000.00"),              # Base de calculo compartilhada IBS+CBS
    ibscbs_p_ibs_uf=Decimal("0.1000"),          # Aliquota IBS UF (4 casas)
    ibscbs_v_ibs_uf=Decimal("1.00"),            # Valor IBS UF
    ibscbs_p_ibs_mun=Decimal("0.0000"),         # Aliquota IBS Municipal
    ibscbs_v_ibs_mun=Decimal("0.00"),           # Valor IBS Municipal
    ibscbs_v_ibs=Decimal("1.00"),               # Valor total IBS (UF + Mun)
    ibscbs_p_cbs=Decimal("0.9000"),             # Aliquota CBS (4 casas)
    ibscbs_v_cbs=Decimal("9.00"),               # Valor CBS

    # IS — armazenado na entidade mas NAO serializado no XML (2026)
    # is_cst_selec="000",
    # is_c_class_trib="010001",
    # is_vbc=Decimal("1000.00"),
    # is_aliquota=Decimal("1.0000"),
    # is_valor=Decimal("10.00"),
)
```

### Exemplo: imunidade e nao incidencia (CST 410, sem gIBSCBS)

```python
nota_fiscal.adicionar_produto_servico(
    # ... campos do produto ...

    # Apenas CST e cClassTrib, sem valores (autorizado em homologacao SP)
    ibscbs_cst="410",
    ibscbs_c_class_trib="410001",
)
```

### Exemplo: reducao de aliquota (gRed)

Valores do exemplo oficial da calculadora RTC da Receita Federal (reducao de 60%):

```python
nota_fiscal.adicionar_produto_servico(
    # ... campos do produto ...
    ibscbs_cst="200",
    ibscbs_c_class_trib="200028",
    ibscbs_vbc=Decimal("1200.00"),

    ibscbs_p_ibs_uf=Decimal("0.05"),
    ibscbs_p_red_aliq_ibs_uf=Decimal("60.00"),   # gIBSUF/gRed/pRedAliq
    ibscbs_p_aliq_efet_ibs_uf=Decimal("0.02"),   # gIBSUF/gRed/pAliqEfet
    ibscbs_v_ibs_uf=Decimal("0.24"),

    ibscbs_p_ibs_mun=Decimal("0.05"),
    ibscbs_p_red_aliq_ibs_mun=Decimal("60.00"),
    ibscbs_p_aliq_efet_ibs_mun=Decimal("0.02"),
    ibscbs_v_ibs_mun=Decimal("0.24"),

    ibscbs_v_ibs=Decimal("0.48"),

    ibscbs_p_cbs=Decimal("8.80"),
    ibscbs_p_red_aliq_cbs=Decimal("60.00"),
    ibscbs_p_aliq_efet_cbs=Decimal("3.52"),
    ibscbs_v_cbs=Decimal("42.24"),
)
```

Regras:

- `gRed` e emitido por tributo, apenas quando `ibscbs_p_red_aliq_*` for informado. O padrao e `None` (sem reducao); `0` e um valor valido, pois reducao de 100% gera aliquota efetiva zero.
- `pAliqEfet` e obrigatorio quando ha reducao. Sem ele, a serializacao levanta `ValueError`. A lib nao calcula a aliquota efetiva nem o valor do tributo.
- Ordem no XML: `pXXX`, `gRed`, `vXXX`.

### Exemplo: Simples Nacional (gTribSN)

Composicao do IBS e da CBS para optantes do Simples. O `gIBSCBS` tambem precisa ser informado: a SEFAZ rejeita o `gTribSN` sem ele. Os valores abaixo usam as aliquotas de teste de 2026 e sao ilustrativos:

```python
nota_fiscal.adicionar_produto_servico(
    # ... campos do produto, ICMS com CSOSN ...
    ibscbs_cst="000",
    ibscbs_c_class_trib="000001",

    # gIBSCBS (obrigatorio tambem para o Simples)
    ibscbs_vbc=Decimal("10.00"),
    ibscbs_p_ibs_uf=Decimal("0.1000"),
    ibscbs_v_ibs_uf=Decimal("0.01"),
    ibscbs_p_ibs_mun=Decimal("0.0000"),
    ibscbs_v_ibs_mun=Decimal("0.00"),
    ibscbs_v_ibs=Decimal("0.01"),
    ibscbs_p_cbs=Decimal("0.9000"),
    ibscbs_v_cbs=Decimal("0.09"),

    # gTribSN
    ibscbs_p_ibs_sn=Decimal("0.1000"),  # gTribSN/gIBSSN/pIBSSN - aliquota efetiva
    ibscbs_v_ibs_sn=Decimal("0.01"),    # gTribSN/gIBSSN/vIBSSN
    ibscbs_p_cbs_sn=Decimal("0.9000"),  # gTribSN/gCBSSN/pCBSSN - aliquota efetiva
    ibscbs_v_cbs_sn=Decimal("0.09"),    # gTribSN/gCBSSN/vCBSSN
)
```

XML gerado (estrutura de uma NF-e autorizada em homologacao na SEFAZ-SP, emitente MEI):

```xml
<IBSCBS>
  <CST>000</CST>
  <cClassTrib>000001</cClassTrib>
  <gIBSCBS>
    <vBC>10.00</vBC>
    <gIBSUF><pIBSUF>0.1000</pIBSUF><vIBSUF>0.01</vIBSUF></gIBSUF>
    <gIBSMun><pIBSMun>0.0000</pIBSMun><vIBSMun>0.00</vIBSMun></gIBSMun>
    <vIBS>0.01</vIBS>
    <gCBS><pCBS>0.9000</pCBS><vCBS>0.09</vCBS></gCBS>
  </gIBSCBS>
  <gTribSN>
    <gIBSSN><pIBSSN>0.1000</pIBSSN><vIBSSN>0.01</vIBSSN></gIBSSN>
    <gCBSSN><pCBSSN>0.9000</pCBSSN><vCBSSN>0.09</vCBSSN></gCBSSN>
  </gTribSN>
</IBSCBS>
```

Regras:

- `gTribSN` e emitido quando algum campo `ibscbs_*_sn` e informado (padrao `None`).
- `gCBSSN` e obrigatorio; `gIBSSN` e opcional (sem IBS, por exemplo CRT=2). Cada subgrupo exige aliquota e valor, senao a serializacao levanta `ValueError`.
- `gIBSCBS` e emitido antes do `gTribSN` e precisa estar preenchido. Para CST tributado sem base nem aliquotas, a serializacao levanta `ValueError` em vez de gerar um grupo zerado.
- Totais: `IBSCBSTot/gTribSN` com `vIBSSN` e `vCBSSN` somados dos itens. `vIBSSN` e sempre emitido (obrigatorio no schema), com `0.00` quando nenhum item tem IBS.
- A lib nao calcula aliquotas efetivas nem valores. Para o calculo, ver a calculadora oficial da Receita Federal para o Simples Nacional (`ReceitaFederal/calculadora-rtc-simples-nacional`).

Rejeicoes verificadas em homologacao (SEFAZ-SP; lista completa em [regras_sefaz.md](regras_sefaz.md)):

| cStat | Motivo | Causa |
|-------|--------|-------|
| 1022 | Grupo gIBSCBS nao informado | `gTribSN` sem `gIBSCBS` |
| 1026 | Aliquota do IBS da UF invalida | `gIBSCBS` com aliquotas zeradas |

> **A confirmar com a contabilidade:** quais CST/cClassTrib e quais valores usar nos itens do Simples. A estrutura acima foi aceita pela SEFAZ; os valores sao de teste.

### Exemplo: sem reforma tributaria (compatibilidade retroativa)

Se nenhum campo `ibscbs_*` for informado, o grupo `<IBSCBS>` **nao e emitido** no XML. Isso garante compatibilidade total com NF-e que nao precisam dos novos impostos.

```python
# Produto sem campos de reforma = XML identico ao anterior
nota_fiscal.adicionar_produto_servico(
    # ... apenas campos legados (ICMS, PIS, COFINS) ...
)
```

### cMunFGIBS no cabecalho

```python
nota_fiscal = NotaFiscal(
    # ... demais campos ...
    municipio_fato_gerador_ibs="4118402",  # Codigo IBGE — gera <cMunFGIBS> no <ide>
)
```

## Campos disponiveis

### Campos do produto (`adicionar_produto_servico`)

#### IBSCBS (Group UB)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `ibscbs_cst` | `str` | CST 3 digitos (ex: "000", "222") |
| `ibscbs_c_class_trib` | `str` | cClassTrib 6 digitos (classificacao tributaria) |
| `ibscbs_vbc` | `Decimal` | Base de calculo compartilhada IBS + CBS |
| `ibscbs_p_ibs_uf` | `Decimal` | Aliquota IBS estadual (4 casas decimais) |
| `ibscbs_v_ibs_uf` | `Decimal` | Valor IBS estadual |
| `ibscbs_p_ibs_mun` | `Decimal` | Aliquota IBS municipal (4 casas decimais) |
| `ibscbs_v_ibs_mun` | `Decimal` | Valor IBS municipal |
| `ibscbs_v_ibs` | `Decimal` | Valor total IBS (UF + Mun) |
| `ibscbs_p_cbs` | `Decimal` | Aliquota CBS (4 casas decimais) |
| `ibscbs_v_cbs` | `Decimal` | Valor CBS |
| `ibscbs_p_red_aliq_ibs_uf` | `Decimal \| None` | `gIBSUF/gRed/pRedAliq` — percentual de reducao |
| `ibscbs_p_aliq_efet_ibs_uf` | `Decimal \| None` | `gIBSUF/gRed/pAliqEfet` — aliquota efetiva |
| `ibscbs_p_red_aliq_ibs_mun` | `Decimal \| None` | `gIBSMun/gRed/pRedAliq` |
| `ibscbs_p_aliq_efet_ibs_mun` | `Decimal \| None` | `gIBSMun/gRed/pAliqEfet` |
| `ibscbs_p_red_aliq_cbs` | `Decimal \| None` | `gCBS/gRed/pRedAliq` |
| `ibscbs_p_aliq_efet_cbs` | `Decimal \| None` | `gCBS/gRed/pAliqEfet` |
| `ibscbs_p_ibs_sn` | `Decimal \| None` | `gTribSN/gIBSSN/pIBSSN` — aliquota efetiva do IBS no Simples |
| `ibscbs_v_ibs_sn` | `Decimal \| None` | `gTribSN/gIBSSN/vIBSSN` |
| `ibscbs_p_cbs_sn` | `Decimal \| None` | `gTribSN/gCBSSN/pCBSSN` — aliquota efetiva da CBS no Simples |
| `ibscbs_v_cbs_sn` | `Decimal \| None` | `gTribSN/gCBSSN/vCBSSN` |

#### IS (Imposto Seletivo) — armazenado, nao serializado em 2026

| Campo | XML Tag | Descricao |
|-------|---------|-----------|
| `is_cst_selec` | `CSTIS` | CSTIS 3 digitos (ex: "000"), a partir de 2027 |
| `is_c_class_trib` | `cClassTribIS` | cClassTribIS 6 digitos |
| `is_vbc` | `vBCIS` | Base de calculo IS |
| `is_aliquota` | `pIS` | Aliquota IS (4 casas decimais) |
| `is_valor` | `vIS` | Valor IS |

### Totais da nota fiscal (acumulados automaticamente)

| Campo | XML Path em `IBSCBSTot` | Descricao |
|-------|-------------------------|-----------|
| `totais_vbc_ibscbs` | `vBCIBSCBS` | Soma de `ibscbs_vbc` de todos os produtos |
| `totais_ibs_uf` | `gIBS/gIBSUF/vIBSUF` | Soma de `ibscbs_v_ibs_uf` de todos os produtos |
| `totais_ibs_mun` | `gIBS/gIBSMun/vIBSMun` | Soma de `ibscbs_v_ibs_mun` de todos os produtos |
| `totais_ibs` | `gIBS/vIBS` | Soma de `ibscbs_v_ibs` de todos os produtos |
| `totais_cbs` | `gCBS/vCBS` | Soma de `ibscbs_v_cbs` de todos os produtos |
| `totais_is` | *(nao emitido)* | Soma de `is_valor` — acumulado internamente, nao no XML |

Os totais sao acumulados automaticamente ao chamar `adicionar_produto_servico()`.

> **IMPORTANTE**: IBS/CBS/IS **NAO sao somados** ao `vNF` (proibido em 2025-2026 conforme NT 2025.002-RTC).

### Campo do cabecalho

| Campo | XML Tag | Descricao |
|-------|---------|-----------|
| `municipio_fato_gerador_ibs` | `cMunFGIBS` | Codigo IBGE do municipio do fato gerador IBS (7 digitos) |

## Estrutura XML gerada

### Item — dentro de `<det><imposto>`

O grupo `<IBSCBS>` e adicionado como filho direto de `<imposto>`, apos `<COFINS>`:

```xml
<det nItem="1">
  <prod>...</prod>
  <imposto>
    <ICMS>...</ICMS>
    <PIS>...</PIS>
    <COFINS>...</COFINS>
    <IBSCBS>
      <CST>000</CST>
      <cClassTrib>000001</cClassTrib>
      <gIBSCBS>
        <vBC>1000.00</vBC>
        <gIBSUF>
          <pIBSUF>0.1000</pIBSUF>
          <vIBSUF>1.00</vIBSUF>
        </gIBSUF>
        <gIBSMun>
          <pIBSMun>0.0000</pIBSMun>
          <vIBSMun>0.00</vIBSMun>
        </gIBSMun>
        <vIBS>1.00</vIBS>
        <gCBS>
          <pCBS>0.9000</pCBS>
          <vCBS>9.00</vCBS>
        </gCBS>
      </gIBSCBS>
    </IBSCBS>
  </imposto>
</det>
```

Para CSTs sem grupo (ex: 410 — imunidade e nao incidencia):

```xml
<IBSCBS>
  <CST>410</CST>
  <cClassTrib>410001</cClassTrib>
</IBSCBS>
```

### Totais — Group W03 (`<IBSCBSTot>`)

Os totais ficam em um grupo **separado** de `<ICMSTot>`, como irmao dentro de `<total>`. O tipo XSD e `TIBSCBSMonoTot` (definido em `DFeTiposBasicos_v1.00.xsd`).

```xml
<total>
  <ICMSTot>
    <!-- totais existentes (ICMS, PIS, COFINS, etc.) -->
    <vNF>1250.00</vNF>  <!-- NAO inclui IBS/CBS/IS -->
  </ICMSTot>
  <IBSCBSTot>
    <vBCIBSCBS>1000.00</vBCIBSCBS>       <!-- Total BC (obrigatorio, primeiro filho) -->
    <gIBS>                                 <!-- Totalizacao do IBS (opcional) -->
      <gIBSUF>
        <vDif>0.00</vDif>                 <!-- Total diferimento IBS UF -->
        <vDevTrib>0.00</vDevTrib>          <!-- Total devolucao tributos IBS UF -->
        <vIBSUF>1.00</vIBSUF>             <!-- Total IBS estadual -->
      </gIBSUF>
      <gIBSMun>
        <vDif>0.00</vDif>
        <vDevTrib>0.00</vDevTrib>
        <vIBSMun>0.50</vIBSMun>           <!-- Total IBS municipal -->
      </gIBSMun>
      <vIBS>1.50</vIBS>                   <!-- Total IBS (UF + Mun) -->
      <vCredPres>0.00</vCredPres>          <!-- Total credito presumido IBS -->
      <vCredPresCondSus>0.00</vCredPresCondSus>
    </gIBS>
    <gCBS>                                 <!-- Totalizacao da CBS (opcional) -->
      <vDif>0.00</vDif>
      <vDevTrib>0.00</vDevTrib>
      <vCBS>9.00</vCBS>                   <!-- Total CBS -->
      <vCredPres>0.00</vCredPres>
      <vCredPresCondSus>0.00</vCredPresCondSus>
    </gCBS>
    <!-- gMono: totais monofasia (nao implementado) -->
    <!-- gEstornoCred: totais estorno de credito (nao implementado) -->
  </IBSCBSTot>
</total>
```

> Os subgrupos `gIBS` e `gCBS` sao opcionais (`minOccurs="0"`) — emitidos apenas quando ha valores. Os campos `vDif`, `vDevTrib`, `vCredPres` e `vCredPresCondSus` sao obrigatorios dentro de cada subgrupo (emitidos como "0.00" quando nao utilizados).

### Cabecalho — `cMunFGIBS` no `<ide>`

```xml
<ide>
  <!-- ... campos existentes ... -->
  <cMunFG>4118402</cMunFG>
  <cMunFGIBS>4118402</cMunFGIBS>
  <tpImp>1</tpImp>
  <!-- ... -->
</ide>
```

## Regras de serializacao

### Grupos por CST

Definidos por `IBS_CBS_CST_GRUPOS` (ver "CSTs disponiveis"). Os CSTs que exigem `gIBSCBS` geram o subgrupo completo com `vBC`, `gIBSUF`, `gIBSMun`, `vIBS` e `gCBS`; os demais geram apenas `<CST>` e `<cClassTrib>`.

### Outras regras

- **`cClassTrib`**: Emitido quando informado (campo obrigatorio na pratica)
- **`cMunFGIBS`**: Emitido no `<ide>` apenas quando informado
- **`<IBSCBSTot>`**: Tipo `TIBSCBSMonoTot`. Omitido se todos os totais forem zero. Quando emitido, `vBCIBSCBS` e obrigatorio como primeiro filho; `gIBS` e `gCBS` sao opcionais
- **`<IBSCBS>`**: Tipo `TTribNFe`. Omitido completamente se `ibscbs_cst` nao for informado
- **IS (`<IS>`)**: Tipo `TIS`. **Nao emitido no XML** — serializacao desabilitada ate 2027
- **`<ISTot>`**: Tipo `TISTot`. **Nao emitido** — sera irmao de `<IBSCBSTot>` (antes dele no schema)
- **`vNF`**: NAO inclui valores de IBS, CBS ou IS (proibido em 2025-2026)

## IS (Imposto Seletivo) — preparado para 2027

O IS esta implementado nas entidades mas desabilitado na serializacao:

- **Entidade** (`NotaFiscalProduto`): campos `is_cst_selec`, `is_c_class_trib`, `is_vbc`, `is_aliquota`, `is_valor` — podem ser preenchidos normalmente
- **Totais** (`NotaFiscal`): `totais_is` e acumulado internamente
- **Serializacao**: `_serializar_is()` existe e usa as tags corretas do schema (`CSTIS`, `cClassTribIS`, `vBCIS`, `pIS`, `vIS`) mas nao e chamado
- **XML**: nao emite `<IS>` nem `<ISTot>`

Quando a serializacao do IS for ativada (previsto para 2027):
1. Descomentar a chamada em `_serializar_imposto_ibscbs()`
2. Adicionar serializacao de `<ISTot>` em `_serializar_nota_fiscal()` (irmao de `<IBSCBSTot>`, antes dele)
3. Atualizar os testes

## Referencia tecnica

| Recurso | Descricao |
|---------|-----------|
| NT 2025.002-RTC (v1.30+) | Nota Tecnica com alteracoes nos layouts XML |
| PL 010b | Pacote de schemas XML (`leiauteNFe_v4.00.xsd` + `DFeTiposBasicos_v1.00.xsd`) |
| LC 214/2025 | Lei Complementar que regulamenta a reforma |
| [Tabela cClassTrib](https://dfe-portal.svrs.rs.gov.br/DFE/TabelaClassificacaoTributaria) | Tabela oficial de classificacao tributaria (JSON disponivel) |
| [Tabela cCredPres](https://dfe-portal.svrs.rs.gov.br/DFE/TabelaCreditoPresumido) | Tabela de credito presumido |

### Tipos XSD relevantes (DFeTiposBasicos_v1.00.xsd)

| Tipo XSD | Elemento XML | Uso |
|----------|-------------|-----|
| `TTribNFe` | `IBSCBS` | Per-item: CST, cClassTrib, choice(gIBSCBS/gIBSCBSMono/...) |
| `TCIBS` | `gIBSCBS` | Per-item: vBC, gIBSUF, gIBSMun, vIBS, gCBS |
| `TIS` | `IS` | Per-item: CSTIS, cClassTribIS, vBCIS, pIS, vIS |
| `TIBSCBSMonoTot` | `IBSCBSTot` | Totais: vBCIBSCBS, gIBS, gCBS, gMono, gEstornoCred |
| `TISTot` | `ISTot` | Totais: vIS |
| `TDif` | `gDif` | Diferimento (pDif, vDif) |
| `TDevTrib` | `gDevTrib` | Devolucao de tributo (vDevTrib) |
| `TRed` | `gRed` | Reducao de aliquota (pRedAliq, pAliqEfet) |
| `TCredPres` | `gCredPresOper` | Credito presumido (pCredPres, vCredPres/vCredPresCondSus) |

## Notas importantes

- Os nomes das tags XML seguem estritamente os tipos XSD do PL 010b (`DFeTiposBasicos_v1.00.xsd`):
  - Per-item: `TTribNFe` (`IBSCBS`), `TCIBS` (`gIBSCBS`), `TIS` (`IS`)
  - Totais: `TIBSCBSMonoTot` (`IBSCBSTot`), `TISTot` (`ISTot`)
- O calculo dos valores (base de calculo, aliquota, valor) deve ser feito pela aplicacao consumidora. pyNotas apenas serializa os valores informados.
- Durante a fase de transicao (2026-2033), os impostos legados e os novos coexistem no mesmo XML.
- Aliquotas de teste para 2026: CBS=0,9%, IBS-UF=0,1%, IBS-Mun=0%.
- Campos de diferimento (`vDif`), devolucao de tributos (`vDevTrib`) e credito presumido (`vCredPres`, `vCredPresCondSus`) sao emitidos como "0.00" nos totais. Suporte completo para esses campos sera adicionado conforme necessidade.
