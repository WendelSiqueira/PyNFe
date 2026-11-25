## PyNFe (fork com Reforma Tributária)

Fork do [PyNFe](https://github.com/TadaSoftware/PyNFe), biblioteca Python de emissão de documentos fiscais eletrônicos, atualizado para a **Reforma Tributária (IBS/CBS)** e para o **pacote de schemas PL_010h** da NF-e.

O projeto original está sem novos merges desde fevereiro de 2026, enquanto as notas técnicas da Reforma continuam saindo. Este fork mantém a lib em dia para uso próprio, com foco em **NF-e modelo 55 emitida por empresas do Simples Nacional**.

Biblioteca de interface com os webservices de Nota Fiscal Eletrônica (NF-e) e Nota Fiscal de Consumidor Eletrônica (NFC-e) da SEFAZ e Receita Federal do Brasil, Nota Fiscal de Serviço Eletrônica (NFS-e) para Prefeituras e Manifesto de Documentos Fiscais Eletrônicos (MDF-e).


O que muda em relação ao original
------------

| Mudança | Situação |
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

* NFS-e (herdado do original, sem manutenção neste fork):
    * Emissão de nota fiscal de serviço eletrônico (Abrasf: Ginfes e Betha)
    * Consultar pelo número da NFS-e
    * Consultar por RPS (recibo provisório de serviço)
    * Consultar Lote
    * Cancelar NFS-e

* MDF-e (herdado do original, sem manutenção neste fork):
    * Versão 3.00, modelo 58
    * Emissão de Manifesto, consultas e eventos (cancelamento, encerramento, inclusão de condutor e de DF-e, pagamento)

* CT-e (herdado do original): apenas Consultar Distribuição DF-e


Instalação
-----------

Este fork não é publicado no PyPI. Para instalar direto do repositório:

```sh
pip install git+https://github.com/WendelSiqueira/PyNFe.git@main
```

Dependências opcionais:

```sh
pip install 'pynfe[nfse] @ git+https://github.com/WendelSiqueira/PyNFe.git@main'      # NFS-e
pip install 'pynfe[impressao] @ git+https://github.com/WendelSiqueira/PyNFe.git@main'  # DANFE (brazilfiscalreport)
```

Dependências principais: `lxml` (XML), `signxml` (assinatura), `pyopenssl` e `cryptography` (certificado A1) e `requests` (webservices da SEFAZ). Para NFS-e, também `suds-community` e `PyXB-X`.


Exemplo de uso
-----------

Consulta de status do serviço:

```python
from pynfe.processamento.comunicacao import ComunicacaoSefaz

certificado = "/home/user/certificado.pfx"
senha = 'senha'
uf = 'pr'
homologacao = True

con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
xml = con.status_servico('nfe')
print(xml.text)
```

Exemplos de emissão com IBS/CBS em [docs/reforma_tributaria.md](docs/reforma_tributaria.md). Mais exemplos gerais no [Wiki do projeto original](https://github.com/TadaSoftware/PyNFe/wiki).


Desenvolvimento
-----------

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/pip install -e .

# Testes (os de NFS-e precisam também de requirements-nfse.txt)
.venv/bin/pytest

# Lint e formatação (ruff 0.12, versão declarada no pyproject.toml)
.venv/bin/ruff check .
.venv/bin/ruff format .
```

Para atualizar os bindings XSD da NFS-e, execute `gerarnfsebindings.sh`.

Navegação no código: arquivos grandes têm mapas em `docs/*_map.md` (ver [AGENTS.md](AGENTS.md)).


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

Licenciado sob a [LGPL-3.0](LICENSE), a mesma do projeto original.
