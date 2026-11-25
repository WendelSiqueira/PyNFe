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

Detalhes, campos e exemplos de XML em [docs/reforma_tributaria.md](docs/reforma_tributaria.md).

A lib **serializa** os valores de IBS/CBS informados, mas **não calcula** alíquotas nem valores. Para o cálculo, a Receita Federal publicou calculadoras oficiais em código aberto:

- [calculadora-rtc-regime-regular](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular): regime regular, com tabelas oficiais de CST, cClassTrib, NCM e alíquotas
- [calculadora-rtc-simples-nacional](https://github.com/ReceitaFederal/calculadora-rtc-simples-nacional): Simples Nacional


Características
------------

* NF-e e NFC-e:
    * Versão 4.00, schemas PL_010h
    * Reforma Tributária: grupos `IBSCBS`, `gRed`, `gTribSN` e totais `IBSCBSTot`
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

A lib não é publicada no PyPI. Para usar como dependência de outro projeto, direto do repositório:

```sh
uv add "pynotas @ git+https://github.com/WendelSiqueira/pyNotas.git@main"
```

Dependência opcional para impressão do DANFE (brazilfiscalreport):

```sh
uv add "pynotas[impressao] @ git+https://github.com/WendelSiqueira/pyNotas.git@main"
```

Com pip, o mesmo endereço funciona: `pip install "pynotas @ git+https://github.com/WendelSiqueira/pyNotas.git@main"`.

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

Exemplos de emissão com IBS/CBS em [docs/reforma_tributaria.md](docs/reforma_tributaria.md). O que a lib valida, e as rejeições da SEFAZ já verificadas em homologação, estão em [docs/regras_sefaz.md](docs/regras_sefaz.md). Mais exemplos gerais no [Wiki](https://github.com/TadaSoftware/PyNFe/wiki).


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

Para atualizar as ACs da ICP-Brasil a partir do pacote oficial do ITI: `uv run python scripts/atualizar_cadeia_icp_brasil.py`. Testes que acessam a SEFAZ só rodam com `PYNOTAS_TESTES_REDE=1`.

Orientações para agentes de IA que trabalham no código estão no [AGENTS.md](AGENTS.md).


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

Baseado no [PyNFe](https://github.com/TadaSoftware/PyNFe), da TadaSoftware e colaboradores. Autoria original e créditos em [AUTHORS](AUTHORS).

Licenciado sob a [LGPL-3.0](LICENSE).
