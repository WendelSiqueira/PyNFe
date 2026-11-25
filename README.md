## pyNotas

Biblioteca Python de interface com os webservices de Nota Fiscal Eletrônica (NF-e) e Nota Fiscal de Consumidor Eletrônica (NFC-e) da SEFAZ e Receita Federal do Brasil, e de Manifesto de Documentos Fiscais Eletrônicos (MDF-e).

Atualizada para a **Reforma Tributária (IBS/CBS)** e para o **pacote de schemas PL_010h** da NF-e, com foco em **NF-e modelo 55 emitida por empresas do Simples Nacional**.


Reforma Tributária
------------

| Item | Situação |
|---------|----------|
| Schemas da NF-e atualizados para o **PL_010h** (inclui `DFeTiposBasicos_v1.00.xsd` com os tipos de IBS/CBS) | feito |
| Testes da Reforma validam o XML gerado contra o schema oficial | feito |
| **`gRed`**: redução de alíquota em `gIBSUF`, `gIBSMun` e `gCBS` | feito |
| **`gTribSN`**: IBS e CBS do Simples Nacional, no item e nos totais (`IBSCBSTot`) | feito |
| Revisão da tabela de CST de IBS/CBS contra os dados oficiais da Receita | a fazer |
| Demais grupos da Reforma: `gDif`, `gDevTrib`, `gIBSCBSMono`, `gEstornoCred`, `gCredPresOper` | a fazer |

Detalhes, campos e exemplos de XML em [docs/reforma_tributaria.md](https://github.com/WendelSiqueira/pyNotas/blob/main/docs/reforma_tributaria.md).

A lib **serializa** os valores de IBS/CBS informados, mas **não calcula** alíquotas nem valores. Para o cálculo, a Receita Federal publicou calculadoras oficiais em código aberto:

- [calculadora-rtc-regime-regular](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular): regime regular, com tabelas oficiais de CST, cClassTrib, NCM e alíquotas
- [calculadora-rtc-simples-nacional](https://github.com/ReceitaFederal/calculadora-rtc-simples-nacional): Simples Nacional


Características
------------

* NF-e e NFC-e:
    * Versão 4.00, schemas PL_010h
    * Reforma Tributária: grupos `IBSCBS`, `gRed`, `gTribSN` e totais `IBSCBSTot`
    * CEST, com indicador de escala relevante e CNPJ do fabricante
    * Modelo de Documento fiscal 55 e 65
    * Configuração para utilização em ambiente de produção e homologação (testes)
    * Emissão de notas fiscais normal e em contingência
    * Consulta Status do Serviço
    * Consultar Cadastro de contribuinte
    * Consultar nota fiscal pela chave de acesso
    * Consultar protocolo
    * Evento de cancelamento de notas
    * Evento de carta de correção
    * Evento de inutilizar de notas
    * Evento de manifestação do destinatário
    * Consultar Distribuição DF-e

* MDF-e:
    * Versão 3.00, modelo 58
    * Emissão de Manifesto, consultas e eventos (cancelamento, encerramento, inclusão de condutor e de DF-e, pagamento)

* CT-e: Consultar Distribuição DF-e

NFS-e (nota de serviço) não é suportada. Os provedores municipais Betha e Ginfes foram removidos; o caminho para NFS-e seria o padrão nacional.


Instalação
-----------

O pacote se chama `pynotas-br` e o import é `pynotas`.

Como dependência de outro projeto, pela tag da versão no repositório:

```sh
uv add "pynotas-br @ git+https://github.com/WendelSiqueira/pyNotas.git@v0.8.0"
uv add "pynotas-br[impressao] @ git+https://github.com/WendelSiqueira/pyNotas.git@v0.8.0"  # DANFE (brazilfiscalreport)
```

Com pip, o mesmo endereço funciona: `pip install "pynotas-br @ git+https://github.com/WendelSiqueira/pyNotas.git@v0.8.0"`.

A versão 0.8.0 também está no **TestPyPI**, o índice de testes do PyPI. Como lá qualquer pessoa publica qualquer nome, instale só o `pynotas-br` de lá e as dependências do PyPI oficial:

```sh
uv pip install --no-deps --index-url https://test.pypi.org/simple/ "pynotas-br==0.8.0"
uv pip install "requests>=2.32.4,<3" certifi "lxml>=5.4.0" "signxml>=4.1.0" "cryptography>=43.0.3" "pyopenssl>=25.1.0,<26"
```

Evite `--extra-index-url` com o TestPyPI: as dependências podem acabar vindo de lá. O histórico de versões está no [CHANGELOG](https://github.com/WendelSiqueira/pyNotas/blob/main/CHANGELOG.md).

Dependências principais: `lxml` (XML), `signxml` (assinatura), `pyopenssl` e `cryptography` (certificado A1) e `requests` (webservices da SEFAZ).


Exemplo de uso
-----------

Consulta de status do serviço:

```python
from pynotas.processamento.comunicacao import ComunicacaoSefaz

certificado = "/home/user/certificado.pfx"
senha = 'senha'
uf = 'pr'
homologacao = True

con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
xml = con.status_servico('nfe')
print(xml.text)
```

A conexão com a SEFAZ verifica o certificado do servidor usando as CAs padrão (`certifi`) e as da ICP-Brasil, que vêm com a lib (`pynotas/data/certificados/icp-brasil.pem`). Para usar outra cadeia, passe o caminho em `verificar_ssl="/caminho/cas.pem"`. `verificar_ssl=False` desliga a verificação, mas deixa a conexão sujeita a interceptação.

Exemplos de emissão com IBS/CBS em [docs/reforma_tributaria.md](https://github.com/WendelSiqueira/pyNotas/blob/main/docs/reforma_tributaria.md). O que a lib valida, e as rejeições da SEFAZ já verificadas em homologação, estão em [docs/regras_sefaz.md](https://github.com/WendelSiqueira/pyNotas/blob/main/docs/regras_sefaz.md). Mais exemplos gerais no [Wiki](https://github.com/TadaSoftware/PyNFe/wiki).


Desenvolvimento
-----------

As dependências são gerenciadas com o [uv](https://docs.astral.sh/uv/) (`pyproject.toml` e `uv.lock`).

```sh
# Ambiente com as dependências de desenvolvimento
uv sync

# Testes
uv run pytest

# Lint e formatação (ruff fixado no grupo dev do pyproject.toml)
uv run ruff check .
uv run ruff format .
```

Para testar contra a SEFAZ em **homologação** (notas sem valor fiscal) com o seu certificado A1, use `scripts/homologacao.py`. A configuração fica fora do repositório, em `~/.config/pynotas/homologacao.env` (caminho do certificado, senha e UF), e os dados do emitente vêm do certificado e da consulta de cadastro da SEFAZ:

```sh
uv run python scripts/homologacao.py status          # status da SEFAZ e cadastro do emitente
uv run python scripts/homologacao.py emitir          # emite uma NF-e de teste
uv run python scripts/homologacao.py emitir --reforma
uv run python scripts/homologacao.py emitir --cest 2003800 --escala N --cnpj-fabricante 11222333000181
uv run python scripts/homologacao.py notas           # notas emitidas pela ferramenta
uv run python scripts/homologacao.py consultar       # sem chave: ultima nota emitida
uv run python scripts/homologacao.py cce --correcao "texto da correcao"
uv run python scripts/homologacao.py cancelar
uv run python scripts/homologacao.py inutilizar --inicio 10 --fim 12
```

Para atualizar as ACs da ICP-Brasil a partir do pacote oficial do ITI: `uv run python scripts/atualizar_cadeia_icp_brasil.py`. Testes que acessam a SEFAZ só rodam com `PYNOTAS_TESTES_REDE=1`.

Orientações para agentes de IA que trabalham no código estão no [AGENTS.md](https://github.com/WendelSiqueira/pyNotas/blob/main/AGENTS.md).


Referências
-----------

- Portal da NF-e: http://www.nfe.fazenda.gov.br/
- Tabela de classificação tributária (cClassTrib): https://dfe-portal.svrs.rs.gov.br/DFE/TabelaClassificacaoTributaria
- MDF-e: https://dfe-portal.svrs.rs.gov.br/mdfe
- Validador de XML da NF-e: https://www.sefaz.rs.gov.br/NFE/NFE-VAL.aspx
- Validador de assinaturas: https://servicos.receita.fazenda.gov.br/servicos/assinadoc/ValidadorAssinaturas.app/valida.aspx
- Impressão de documentos fiscais: https://github.com/Engenere/BrazilFiscalReport


Créditos e licença
-----------

Baseado no [PyNFe](https://github.com/TadaSoftware/PyNFe), da TadaSoftware e colaboradores. Autoria original e créditos em [AUTHORS](https://github.com/WendelSiqueira/pyNotas/blob/main/AUTHORS).

Licenciado sob a [LGPL-3.0](https://github.com/WendelSiqueira/pyNotas/blob/main/LICENSE).
