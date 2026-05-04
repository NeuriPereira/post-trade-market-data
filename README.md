# Pipeline de Ingestão — Post-Trade Market Data

---

## O contexto por trás dos dados

Imagine um mercado onde bilhões de reais são movimentados todos os dias. Onde cada operação precisa ser registrada, validada, conciliada e liquidada com precisão absoluta.

Por anos, esse mercado funcionou com múltiplas estruturas separadas — cada uma com suas próprias regras, sistemas e formas de operar. Corretoras operavam com modelos diferentes, produtos diferentes, volumes diferentes. Um mesmo cliente podia existir em mais de um ambiente, com códigos diferentes, regras diferentes e visões fragmentadas da sua própria posição.

Por trás disso: sistemas legados, processos manuais, integrações frágeis e uma forte dependência de arquivos e rotinas que precisavam "conversar" entre si.

Foi nesse cenário que surgiu um dos maiores movimentos de transformação do mercado financeiro brasileiro: **a integração da pós-negociação conduzida pela B3**.

A proposta parecia simples no papel — unificar as câmaras de compensação em uma única estrutura. Na prática, significava reescrever a forma como dados, sistemas e processos se conectavam. Os arquivos que antes seguiam um padrão passaram a adotar um novo modelo baseado em **ISO 20022**. Sistemas legados precisaram ser adaptados. Um único arquivo antigo passou a representar múltiplos novos arquivos. E era necessário garantir que toda a história do dado fosse preservada — clientes com múltiplos códigos precisavam ser unificados sem apagar o passado.

Esse trabalho exigiu um esforço coordenado entre negócio e tecnologia. Não era apenas sobre código — era sobre entender o funcionamento do mercado.

Veio então a etapa mais crítica: a **produção paralela**. Durante semanas, dados reais eram replicados para ambientes de certificação. As operações aconteciam em produção — e, ao mesmo tempo, eram reprocessadas em paralelo para validar se os novos sistemas estavam corretos. Qualquer divergência poderia indicar um problema grave. Se o cadastro estivesse incorreto, toda a cadeia quebrava: liquidação, risco, custódia, conciliação.

E então chegou a **virada**.

Durante um final de semana, após o fechamento do pregão, equipes técnicas e de negócio trabalharam de forma contínua. Validações a cada etapa. Decisões em tempo real. Checkpoints com o mercado, alinhamentos executivos, pressão por estabilidade.

Na segunda-feira, o sistema entrou em produção.

Como esperado em projetos dessa magnitude, problemas surgiram. E por semanas, equipes trabalharam intensamente para estabilizar o ambiente. Aos poucos, tudo começou a se ajustar. E ao final, o resultado foi uma infraestrutura mais eficiente, mais integrada e preparada para suportar o crescimento do mercado.

Os números falam por si:

- **~R$ 40 bilhões** em eficiência de capital liberados entre as duas fases da integração
- **1 milhão de transações/dia** em média, com picos de **3 milhões**
- Capacidade projetada para **10 milhões de transações diárias**
- Brasil posicionado entre os mercados com infraestrutura de pós-negociação mais avançada do mundo

Mas por trás de tudo isso havia algo fundamental: **dados**. Arquivos sendo enviados e recebidos. Sistemas sendo alimentados. Integrações sendo reescritas. Regras sendo aplicadas.

O que parecia apenas "um arquivo" era, na verdade, parte de um ecossistema complexo que sustentava todo o funcionamento do mercado.

---

## A fagulha

Este projeto é pequeno em escopo, mas preciso em propósito.

Ele ingere o **BVBG.086** — o Boletim de Negociação da B3, publicado diariamente após o fechamento do pregão. Um arquivo que carrega os preços, volumes e instrumentos negociados em um dia inteiro de operações no mercado de capitais brasileiro.

É um ponto de entrada. Uma fagulha.

Porque, como a história acima mostra, por trás de cada arquivo existe um ecossistema inteiro — e entender isso é o que diferencia um pipeline técnico de uma solução real de negócio.

### O que este pipeline faz hoje

```
B3 (pós-pregão 18h30)
        │
        ▼ download streaming — verifica assinatura ZIP
pesquisa-pregao.zip
        │
        ▼ extração dupla (ZIP dentro de ZIP)
PR{YYMMDD}.zip → BVBG.086.01_*.xml
        │
        ▼ parse XML streaming (ET.iterparse, ~195k registros/arquivo)
Lista de registros estruturados
        │
        ▼ armazenamento
Parquet + JSON  →  (roadmap: PostgreSQL Silver/Gold)
        │
        ▼ API
GET /ativos/{ticker}   POST /pipeline/run
```

### O que este pipeline pode se tornar

A B3 publica **múltiplos tipos de arquivo** via o mesmo mecanismo de pesquisa por pregão, cada um representando um processo de negócio diferente:

| Arquivo | Descrição | Processo |
|---|---|---|
| BVBG.086 | Boletim de Negociação | **Precificação** — atual |
| BVBG.087 | Arquivo de Índices | Indicadores de mercado |
| BVBG.028 | Cadastro de Instrumentos | Gestão de cadastro |
| BVBG.029 | Instrumentos Indicadores | Referência de preço |
| BVBG.186 | Boletim Simplificado Ações | Renda variável |
| BVBG.187 | Boletim Simplificado Derivativos | Derivativos |

Cada um desses arquivos poderia ter seu próprio pipeline, com suas próprias regras de transformação, validação e armazenamento — **segregados por processo de negócio**, assim como a câmara de compensação segrega internamente liquidação, custódia, risco e conciliação.

Há ainda uma dimensão mais profunda: participantes do mercado (corretoras, custodiantes) não apenas *consomem* arquivos da B3 — eles também *enviam*. O padrão de **estímulo e resposta** funciona assim:

```
Participante                    B3
     │                           │
     │──── arquivo de estímulo ──▶│  (posição, operação, instrução)
     │                           │  (processa, valida, liquida)
     │◀─── arquivo de resposta ───│  (confirmação, extrato, aviso)
```

Um pipeline completo de pós-negociação precisaria tratar os dois lados desse fluxo. Este projeto trata o lado da leitura — mas a estrutura já está preparada para crescer.

---

## Arquitetura

### Camadas de dados (Medallion)

```
Bronze  ── XMLs brutos preservados em extraidos/{data}/
Silver  ── Dados estruturados em Parquet/JSON em saida/        (atual)
                                 PostgreSQL                     (roadmap)
Gold    ── Visão consolidada e deduplicada por pregão          (roadmap)
               A B3 publica múltiplos arquivos ao longo do dia;
               o último é o definitivo — a camada Gold resolve isso.
```

### Containers (Docker Compose)

```
┌─────────────────────────────────────────────────────────┐
│  post-trade-mkt          FastAPI        :8000            │
│  ─────────────────────────────────────────────────────  │
│  airflow-webserver       API Server     :8081            │
│  airflow-scheduler       Scheduler                       │
│  airflow-dag-processor   DAG Processor  (Airflow 3.x)    │
│  airflow-db              PostgreSQL 16  (metadata)       │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Pré-requisitos

- Docker e Docker Compose instalados
- Porta 8000 e 8081 disponíveis

### Subir o ambiente

```bash
git clone <repo>
cd download_arquivo
docker-compose up -d
```

Aguarde todos os containers estarem saudáveis:

```bash
docker-compose ps
```

| Serviço | URL | Credenciais |
|---|---|---|
| API FastAPI | http://localhost:8000/docs | — |
| Airflow UI | http://localhost:8081 | admin / admin |

### Executar o pipeline manualmente

```bash
# Disparar pipeline para uma data específica
curl -X POST "http://localhost:8000/pipeline/run?data=2026-04-17"

# Resposta esperada
{"status": "ok", "data": "2026-04-17", "registros": 195432}
```

### Consultar um ativo

```bash
curl "http://localhost:8000/ativos/PETR4?data=2026-04-17"
```

---

## API

### `POST /pipeline/run`

Dispara o pipeline completo para uma data: download → extração → parse → armazenamento.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `string` | Data do pregão no formato `YYYY-MM-DD` |

```bash
curl -X POST "http://localhost:8000/pipeline/run?data=2026-04-17"
# {"status": "ok", "data": "2026-04-17", "registros": 195432}
```

Retorna `422` se o arquivo não estiver disponível para a data informada.

---

### `GET /ativos/{ticker}`

Consulta os dados de negociação de um instrumento para uma data.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `ticker` | `string` (path) | Código do instrumento (ex: `PETR4`) |
| `data` | `string` (query) | Data no formato `YYYY-MM-DD` |

```bash
curl "http://localhost:8000/ativos/PETR4?data=2026-04-17"
```

---

## Airflow

### DAG: `b3_ingestao_bvbg086`

| Propriedade | Valor |
|---|---|
| Schedule | Segunda a sexta, 18h30 horário de Brasília |
| Catchup | Desativado |
| Arquivo | `dags/ingestao.py` |

### Fluxo de execução

```
verificar_arquivo_disponivel  ──▶  executar_pipeline
   (ShortCircuitOperator)            (PythonOperator)

   Faz GET streaming na B3           Chama POST /pipeline/run
   Verifica assinatura ZIP (PK)      Aguarda conclusão (timeout 5min)
   Retorna False → pipeline skip     Retorna registros processados
```

O sensor verifica a assinatura magic bytes do ZIP (`b'PK'`) via GET streaming — a B3 não retorna `Content-Length` no HEAD, por isso a verificação é feita assim.

### Acionar manualmente via UI

1. Acesse http://localhost:8081
2. Ative a DAG `b3_ingestao_bvbg086` (toggle)
3. Clique em **Trigger DAG w/ config**
4. Informe a data lógica desejada
5. Monitore as tasks em **Grid view**

---

## Configuração

As variáveis de ambiente do container `post-trade-mkt` são definidas no `docker-compose.yml`:

| Variável | Descrição |
|---|---|
| `SRC_DOWNLOADS` | Diretório onde os ZIPs são salvos |
| `SRC_EXTRAIDOS` | Diretório onde os XMLs são extraídos |
| `SRC_PATH` | Raiz do código-fonte dentro do container |

Os volumes `./downloads` e `./extraidos` são montados do host, mantendo os arquivos acessíveis fora do container.

---

## Estrutura de diretórios

```
download_arquivo/
│
├── dags/
│   └── ingestao.py              # DAG do Airflow — sensor + pipeline trigger
│
├── src/
│   ├── api.py                   # FastAPI — endpoints /pipeline/run e /ativos
│   ├── main.py                  # Orquestrador do pipeline
│   ├── baixar_arquivos_b3.py    # Download B3 (suporta múltiplos tipos de arquivo)
│   ├── extrair_zip_duplo_b3.py  # Extração ZIP aninhado
│   ├── parse_bvbg086_dinamico2.py  # Parser XML streaming (BVBG.086)
│   ├── config/
│   │   └── config.py            # Variáveis de ambiente com validação fail-fast
│   └── infra/
│       └── storage_handler.py   # Persistência Parquet/JSON e busca por ticker
│
├── downloads/                   # ZIPs baixados da B3 (volume Docker)
├── extraidos/                   # XMLs extraídos por data (volume Docker)
├── saida/                       # Saída Parquet e JSON
│
├── Dockerfile                   # Imagem da aplicação (python:3.13-slim)
├── docker-compose.yml           # Orquestração completa (app + Airflow)
├── requirements.txt             # Dependências Python
└── .env.example                 # Template de configuração local
```

---

## Dependências

| Pacote | Versão | Uso |
|---|---|---|
| fastapi | 0.115.12 | API REST |
| uvicorn | 0.34.0 | Servidor ASGI |
| pandas | 2.2.3 | Manipulação de dados |
| pyarrow | 19.0.1 | Serialização Parquet |
| requests | 2.32.3 | Download B3 |
| python-dotenv | 1.1.0 | Variáveis de ambiente |

> Versões compatíveis com Python 3.13 (wheels pré-compilados disponíveis para todas).

---

## Roadmap

Este pipeline é a primeira camada de algo maior. O que vem a seguir:

### Camada Bronze — armazenamento de arquivos brutos
Persistir os ZIPs e XMLs originais em object storage (MinIO local ou S3), garantindo rastreabilidade e reprocessamento sem necessidade de re-download.

### Camada Silver — PostgreSQL
Gravar os registros parseados em PostgreSQL, substituindo os arquivos Parquet locais por um banco consultável.

### Camada Gold — deduplicação e consolidação
A B3 publica múltiplos arquivos BVBG.086 ao longo do pregão — geralmente o último é o definitivo. A camada Gold identifica e consolida a visão correta por data, eliminando duplicatas.

### Múltiplos tipos de arquivo
O módulo `baixar_arquivos_b3.py` já suporta BVBG.087, BVBG.028, BVBG.029, BVBG.186 e BVBG.187. O próximo passo é criar parsers e pipelines dedicados para cada processo de negócio — precificação, cadastro de instrumentos, derivativos — cada um com suas próprias regras de transformação e validação.

### Agente de IA
Interface conversacional (LangGraph + Chainlit) para consulta de dados via linguagem natural: *"Qual foi o volume negociado de VALE3 na semana passada?"*, *"Quais ações tiveram maior variação hoje?"*. Alimentado pela camada Gold no PostgreSQL.

### Dashboard
Visualização do desempenho histórico de tickers ao longo do tempo, construído sobre a camada Gold.

---

## Notas técnicas relevantes

**Por que GET streaming no sensor do Airflow, não HEAD?**
A B3 não retorna `Content-Length` em requisições HEAD — o header sempre vem vazio. A verificação de disponibilidade é feita via GET streaming, acumulando bytes até obter ao menos 2, e então checando a assinatura magic bytes do ZIP (`b'PK\x03\x04'`).

**Por que `chunk_size` não é suficiente sozinho?**
O parâmetro `chunk_size` no `iter_content` do requests é uma sugestão, não uma garantia. O servidor pode retornar menos bytes que o solicitado. Por isso o loop acumula até atingir o mínimo necessário antes de verificar.

**Airflow 3.x — diferenças críticas em relação ao 2.x**
- `webserver` foi renomeado para `api-server`
- `dag-processor` é um componente separado obrigatório
- `LocalExecutor` comunica com o API server via HTTP — `AIRFLOW__CORE__EXECUTION_API_SERVER_URL` precisa apontar para o container correto
- `AIRFLOW__API_AUTH__JWT_SECRET` deve ser idêntico em todos os containers — se auto-gerado, cada container terá um valor diferente e as tasks falharão com "Invalid auth token"

---

*Um arquivo. Um pipeline. O começo de um ecossistema.*
