---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-02-07'
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', '_bmad-output/brainstorming/brainstorming-session-2026-02-06.md']
workflowType: 'architecture'
project_name: 'Construtor de Questões'
user_name: 'Rodrigo Franco'
date: '2026-02-07'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (38 FRs across 7 categories):**

| Category | FRs | Architectural Implication |
|----------|-----|--------------------------|
| Gestão de Input | FR1-FR3 | Excel parsing layer, input validation, sub-focus generation modes |
| Pipeline de Geração | FR4-FR9 | Multi-agent orchestration core, statistical balancing engine, Bloom taxonomy mapping |
| Qualidade e Validação | FR10-FR18 | Blind review protocol, structured feedback loop, retry logic with limits, hybrid checkpoint system |
| RAG e Referências | FR19-FR22 | Pinecone integration layer, source restriction rules, reference verification |
| Output e Exportação | FR23-FR25 | 26-column Excel writer, partial progress persistence, atomic file operations |
| Métricas e Monitoramento | FR26-FR32 | Per-question metrics collection, real-time dashboard, model comparison engine |
| Configuração e Controle | FR33-FR38 | Dynamic configuration system, prompt management, process lifecycle (start/pause/resume) |

**Non-Functional Requirements (24 NFRs across 6 categories):**

| Category | NFRs | Architectural Driver |
|----------|------|---------------------|
| Performance | NFR1-4 | Async batch processing (asyncio), rate limiting with backoff, non-blocking I/O |
| Segurança | NFR5-7 | Environment-based secrets, no hardcoded credentials |
| Integração | NFR8-10 | Graceful API fallback, Pinecone timeout handling, robust response parsing |
| Resiliência | NFR11-14 | Batch-level state persistence, atomic Excel writes, fault isolation per question |
| Qualidade de Conteúdo | NFR15-20 | ≥85% first-round approval, 0% fake references, balanced answer positions, Brazilian Portuguese |
| Eficiência de Custo | NFR21-24 | Per-question cost tracking, model comparison data, cost projection |

**Scale & Complexity:**

- Primary domain: Backend data pipeline + Streamlit monitoring dashboard
- Complexity level: Medium — sophisticated multi-agent orchestration within bounded single-user scope
- Estimated architectural components: ~8-10 major modules (input parser, agent orchestrator, 3 agent interfaces, checkpoint manager, metrics collector, Excel writer, Streamlit dashboard, configuration manager)

### Technical Constraints & Dependencies

- **Python 3.11+** as runtime — ecosystem advantage for AI/data
- **Direct SDK integration** (openai, anthropic) — no orchestration framework overhead
- **Pinecone RAG** — existing infrastructure with curated medical documents
- **Streamlit** — dashboard framework, not a general-purpose web framework
- **pandas + openpyxl** — Excel I/O standard
- **Single user** — no auth, no multi-tenancy, no concurrent access concerns
- **Target: ~8,000 questions** — pipeline must sustain hours-long batch runs without degradation

### Cross-Cutting Concerns Identified

1. **Error Handling & Resilience** — Every pipeline stage must handle failures gracefully; individual question failure must not halt the batch
2. **Logging & Metrics** — Structured logging per question (model, tokens, cost, rounds, time, decision) feeds both the dashboard and post-run analysis
3. **Cost Tracking** — Token consumption and cost must be captured at every LLM call, aggregated per question and per model
4. **LLM Provider Abstraction** — Two providers (OpenAI, Anthropic) need a unified interface for generation, while preserving provider-specific capabilities
5. **Configuration Management** — Prompts, model selection, temperature, batch size, checkpoint intervals — all runtime-configurable via Streamlit sidebar
6. **Content Quality Enforcement** — Medical accuracy, Brazilian clinical protocols, reference verification, and statistical balancing are constraints that permeate the entire pipeline

## Starter Template Evaluation

### Primary Technology Domain

Backend data pipeline com dashboard de monitoramento — Python 3.11+, processamento batch multi-agente, execução local.

### Starter Options Considered

| Opção | Avaliação |
|-------|-----------|
| Cookiecutter Data Science v2 | Focado em data science (notebooks, modelos ML). Estrutura não alinhada com pipeline multi-agente. Descartado. |
| ETL Pipeline Template | Genérico demais, focado em ETL tradicional. Sem suporte a agentes IA. Descartado. |
| Scaffolding customizado com uv | Melhor fit — estrutura sob medida para pipeline multi-agente, ferramentas modernas, zero overhead desnecessário. **Selecionado.** |

### Selected Approach: Custom Scaffolding with uv

**Rationale:** Nenhum template existente atende a combinação específica de pipeline multi-agente + RAG + Streamlit dashboard. Um scaffolding customizado com uv permite montar exatamente o que o projeto precisa, sem código morto ou estrutura irrelevante.

**Initialization Command:**

```bash
uv init construtor-de-questoes --python 3.11
cd construtor-de-questoes
uv add openai anthropic pandas openpyxl pinecone pydantic streamlit
uv add --dev pytest ruff
```

**Architectural Decisions Provided by Setup:**

**Language & Runtime:** Python 3.11+ gerenciado pelo uv, virtual env automático

**Package Management:** uv v0.10.0 — lockfile reproduzível, resolução determinística de dependências

**Code Quality:** ruff v0.15.0 — linting + formatting unificados, configuração via pyproject.toml

**Testing Framework:** pytest — infraestrutura pronta, uso mínimo no MVP, expansível depois

**Project Configuration:** pyproject.toml como fonte única de verdade

**Code Organization:** src/ layout com módulos por domínio (agents, pipeline, io, metrics, config, dashboard)

**Project Structure:**

```
construtor-de-questoes/
├── src/
│   └── construtor/
│       ├── __init__.py
│       ├── __main__.py          # Entry point do pipeline
│       ├── agents/              # Criador, Comentador, Validador
│       ├── pipeline/            # Orquestração, retry, checkpoints
│       ├── io/                  # Excel input/output, Pinecone
│       ├── metrics/             # Coleta de métricas, custo, logging
│       ├── config/              # Configuração, prompts
│       └── dashboard/           # Streamlit app
├── tests/
├── prompts/                     # Arquivos de prompt dos agentes
├── data/                        # Excel de input (gitignored)
├── output/                      # Excel de output (gitignored)
├── pyproject.toml
├── .env.example
└── .gitignore
```

**Execution:**

- Pipeline: `uv run python -m construtor`
- Dashboard: `uv run streamlit run src/construtor/dashboard/app.py`

## Core Architectural Decisions

### Decision Priority Analysis

**Decisões Críticas (Bloqueiam Implementação):**
- Abstração de provedores LLM (OpenAI + Anthropic)
- Saída estruturada via Pydantic + JSON mode
- Persistência de estado com SQLite
- Protocolo de comunicação entre agentes via Pydantic models
- Estratégia async com asyncio + semáforo

**Decisões Importantes (Moldam a Arquitetura):**
- Gerenciamento de prompts em arquivos separados
- Remoção do Google/Gemini do escopo (simplificação)

**Decisões Adiadas (Pós-MVP):**
- Geração de flashcards (Phase 2)
- Teste A/B automático (Phase 2)
- Inversão Comentador-primeiro (Phase 3)

### Abstração de Provedores LLM

| Campo | Valor |
|-------|-------|
| **Decisão** | Interface abstrata simples (Protocol/ABC) — classe `LLMProvider` com método `generate()` |
| **Provedores** | OpenAI + Anthropic apenas (Google/Gemini removido do escopo) |
| **Rationale** | Controle total sobre tokens/custo/latência. 2 provedores não justificam framework externo. Abstração própria permite comparativo direto. |
| **Afeta** | agents/, pipeline/, metrics/, config/ |
| **Dependências** | `openai`, `anthropic` |

### Saída Estruturada dos LLMs

| Campo | Valor |
|-------|-------|
| **Decisão** | Pydantic models + JSON mode dos SDKs |
| **Rationale** | Validação automática, type safety, retry se parsing falhar. Pydantic já é dependência indireta. Padrão da indústria para structured output. |
| **Afeta** | agents/ (modelos de output de cada agente), pipeline/ (validação + retry) |
| **Dependência** | `pydantic` |

### Persistência de Estado

| Campo | Valor |
|-------|-------|
| **Decisão** | SQLite como banco de estado e métricas |
| **Rationale** | Arquivo único, zero setup, suporte nativo Python. Queries para dashboard Streamlit. 8.000 registros é trivial para SQLite. Escrita atômica para resiliência. |
| **Afeta** | pipeline/ (progresso), metrics/ (coleta), dashboard/ (leitura), io/ (Excel export a partir do SQLite) |
| **Dependência** | `sqlite3` (stdlib Python — zero dependências extras) |

### Protocolo de Comunicação entre Agentes

| Campo | Valor |
|-------|-------|
| **Decisão** | Pydantic models como contratos entre agentes |
| **Rationale** | Consistente com saída estruturada dos LLMs. Contratos explícitos no código. Qualquer agente de IA implementando sabe exatamente o formato de entrada/saída. |
| **Modelos-chave** | `CriadorOutput`, `ComentadorInput`, `ComentadorOutput`, `ValidadorInput`, `ValidadorOutput`, `FeedbackEstruturado` |
| **Afeta** | agents/, pipeline/ |

### Estratégia Async

| Campo | Valor |
|-------|-------|
| **Decisão** | asyncio com Semaphore para controle de concorrência |
| **Rationale** | Ambos SDKs (OpenAI, Anthropic) têm clientes async nativos. Semáforo controla concorrência respeitando rate limits. Conforme NFR3. |
| **Configurável** | Limite de concorrência via Streamlit sidebar |
| **Afeta** | pipeline/ (orquestração), agents/ (chamadas async) |

### Gerenciamento de Prompts

| Campo | Valor |
|-------|-------|
| **Decisão** | Arquivos Markdown separados na pasta `prompts/` |
| **Rationale** | Prompts são conteúdo, não código. Editáveis sem tocar no pipeline. Versionados pelo Git. Streamlit carrega para edição (FR37). Template strings para variáveis. |
| **Estrutura** | `prompts/criador.md`, `prompts/comentador.md`, `prompts/validador.md`, `prompts/subfoco-generator.md` |
| **Afeta** | agents/ (carregamento), config/ (paths), dashboard/ (edição) |

### Segurança

| Campo | Valor |
|-------|-------|
| **Decisão** | API keys via `.env` + carregamento do environment |
| **Rationale** | Conforme NFR5-7. Único usuário, execução local. `.env.example` no repositório, `.env` no `.gitignore`. |
| **Keys necessárias** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PINECONE_API_KEY` |

### Decision Impact Analysis

**Sequência de Implementação:**
1. Pydantic models (contratos entre agentes) — fundação de tudo
2. Abstração LLM provider (OpenAI + Anthropic)
3. SQLite schema (estado + métricas)
4. Agentes individuais (Criador → Comentador → Validador)
5. Orquestração async do pipeline
6. Prompts + template system
7. Dashboard Streamlit

**Dependências entre Decisões:**
- Pydantic models são pré-requisito para os agentes e o pipeline
- Abstração LLM é pré-requisito para os agentes
- SQLite é pré-requisito para o dashboard e a resiliência
- Async depende da abstração LLM estar pronta

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Pontos de conflito potenciais identificados:** 8 áreas onde agentes de IA poderiam fazer escolhas diferentes

### Naming Patterns

**Convenções de Nomenclatura Python (PEP 8 estrito):**

| Elemento | Padrão | Exemplo |
|----------|--------|---------|
| Módulos/arquivos | `snake_case` | `excel_reader.py`, `llm_provider.py` |
| Classes | `PascalCase` | `CriadorAgent`, `LLMProvider` |
| Funções/métodos | `snake_case` | `generate_question()`, `validate_output()` |
| Variáveis | `snake_case` | `question_count`, `approval_rate` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TEMPERATURE` |
| Pydantic models | `PascalCase` | `CriadorOutput`, `ValidadorFeedback` |
| Campos Pydantic | `snake_case` | `resposta_correta`, `nivel_dificuldade` |

**Idioma nos nomes:** Código em inglês (funções, classes, variáveis de lógica). Campos do domínio médico/Excel em **português** (alinhados ao Excel de output — `enunciado`, `alternativa_a`, `resposta_correta`).

**SQLite — Nomenclatura e Schema:**

| Elemento | Padrão | Exemplo |
|----------|--------|---------|
| Tabelas | `snake_case`, plural | `questions`, `metrics`, `checkpoints` |
| Colunas | `snake_case` | `question_id`, `created_at`, `approval_status` |
| Primary keys | `id` (autoincrement) | `INTEGER PRIMARY KEY AUTOINCREMENT` |
| Timestamps | ISO 8601 string | `2026-02-07T14:30:00` |
| Booleans | INTEGER (0/1) | `concordancia_comentador INTEGER DEFAULT 0` |
| Enums | TEXT com valores definidos | `status TEXT CHECK(status IN ('pending','approved','rejected','failed'))` |

### Structure Patterns

**Pydantic Models — Padrões de Contrato:**

```python
# PADRÃO: Todos os modelos herdam de BaseModel
# PADRÃO: Campos obrigatórios sem default, opcionais com Optional + default
# PADRÃO: Validação via Field() com description
# PADRÃO: model_config para JSON serialization

class CriadorOutput(BaseModel):
    model_config = ConfigDict(strict=True)

    enunciado: str = Field(..., description="Texto completo do enunciado")
    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str
    resposta_correta: Literal["A", "B", "C", "D"]
    objetivo_educacional: str
    nivel_dificuldade: Literal[1, 2, 3]
    tipo_enunciado: str
```

**Regra:** Todo agente retorna um Pydantic model. Nunca dicts soltos. Se o JSON do LLM não parseia, retry automático.

### Process Patterns

**Error Handling — Hierarquia de Exceções:**

```python
class PipelineError(Exception): pass
class LLMProviderError(PipelineError): pass
class LLMRateLimitError(LLMProviderError): pass
class LLMTimeoutError(LLMProviderError): pass
class OutputParsingError(PipelineError): pass
class ValidationError(PipelineError): pass
class PineconeError(PipelineError): pass
```

**Regras de tratamento:**
- try/except específico, NUNCA bare except
- Falha em questão individual → log + continue
- Falha em provider → fallback para outro provider
- Falha sistêmica (3+) → pause + notify

**Níveis de Log:**

| Nível | Uso |
|-------|-----|
| `DEBUG` | Detalhes de chamada API, payload enviado/recebido |
| `INFO` | Questão gerada, aprovada, checkpoint atingido |
| `WARNING` | Retry necessário, fallback ativado, discordância agente |
| `ERROR` | Falha em questão, parsing falhou, API indisponível |
| `CRITICAL` | Erro sistêmico, pipeline parado |

**Logging — Formato Estruturado:**

```python
import logging
logger = logging.getLogger(__name__)
# Formato: [2026-02-07 14:30:00] [INFO] [pipeline.orchestrator] Questão 42/8000 aprovada (rodada 1, modelo=gpt-4o, custo=$0.023)
```

Todo log de questão inclui: `question_id`, `foco`, `modelo`, `rodada`, `decisão`.

### Communication Patterns

**Async — Padrões de Concorrência:**

```python
# Semáforo global para controlar concorrência
semaphore = asyncio.Semaphore(MAX_CONCURRENT_CALLS)

# Toda chamada API passa pelo semáforo
async def call_llm(self, prompt: str) -> str:
    async with self.semaphore:
        return await self.client.generate(prompt)
```

- Backoff exponencial com jitter para rate limits
- Timeout configurável por chamada
- Nunca fire-and-forget — sempre await

**Configuração — Padrões de Gestão:**

```python
class PipelineConfig(BaseModel):
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_retries: int = 3
    batch_size: int = 50
    checkpoint_interval: int = 10
    max_concurrent_calls: int = 5
```

- Configuração centralizada num Pydantic model
- Defaults sensatos, overridable via Streamlit sidebar
- Secrets via environment variables, NUNCA em config files

**Testes — Padrões Mínimos:**

- `tests/` espelha `src/construtor/`
- pytest com fixtures
- Mocks para chamadas API (nunca chamar LLM real em teste)
- Teste de Pydantic models com dados válidos e inválidos

### Enforcement Guidelines

**Todo agente de IA implementando código DEVE:**

1. Seguir PEP 8 + convenções de nomenclatura definidas acima
2. Usar Pydantic models para qualquer dado estruturado — nunca dicts soltos
3. Usar exceções customizadas da hierarquia definida — nunca bare `except`
4. Incluir `question_id` e contexto em toda mensagem de log
5. Passar toda chamada API pelo semáforo de concorrência
6. Manter campos de domínio médico/Excel em português
7. Manter código (funções, classes, variáveis de lógica) em inglês

### Anti-Patterns (PROIBIDOS)

```python
# ❌ NUNCA: dict solto como retorno de agente
return {"enunciado": "...", "alternativa_a": "..."}
# ✅ SEMPRE: Pydantic model
return CriadorOutput(enunciado="...", alternativa_a="...")

# ❌ NUNCA: bare except
except: pass
# ✅ SEMPRE: exceção específica
except LLMRateLimitError as e:
    logger.warning(f"Rate limit hit: {e}")

# ❌ NUNCA: chamada API sem semáforo
response = await client.generate(prompt)
# ✅ SEMPRE: via semáforo
async with semaphore:
    response = await client.generate(prompt)
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
construtor-de-questoes/
│
├── pyproject.toml                          # Dependências, config ruff/pytest, metadata
├── .env.example                            # Template de variáveis de ambiente
├── .gitignore                              # data/, output/, .env, *.db, __pycache__/
│
├── prompts/                                # Prompts dos agentes (Markdown)
│   ├── criador.md                          # Prompt do Agente Criador
│   ├── comentador.md                       # Prompt do Agente Comentador (revisão cega)
│   ├── validador.md                        # Prompt do Agente Validador (árbitro)
│   └── subfoco_generator.md                # Prompt para geração de sub-focos em batch
│
├── data/                                   # Excel de input (gitignored)
│   └── .gitkeep
│
├── output/                                 # Excel de output + SQLite (gitignored)
│   └── .gitkeep
│
├── src/
│   └── construtor/
│       ├── __init__.py
│       ├── __main__.py                     # Entry point: parse args, inicia pipeline ou dashboard
│       │
│       ├── models/                         # Pydantic models — contratos do sistema
│       │   ├── __init__.py
│       │   ├── question.py                 # CriadorOutput, QuestionRecord (26 colunas)
│       │   ├── feedback.py                 # ComentadorOutput, ValidadorOutput, FeedbackEstruturado
│       │   ├── pipeline.py                 # BatchState, CheckpointResult, RetryContext
│       │   └── metrics.py                  # QuestionMetrics, BatchMetrics, ModelComparison
│       │
│       ├── agents/                         # Agentes de IA — cada um isolado
│       │   ├── __init__.py
│       │   ├── base.py                     # BaseAgent (ABC) — interface comum
│       │   ├── criador.py                  # CriadorAgent — gera questão + gabarito
│       │   ├── comentador.py               # ComentadorAgent — revisão cega + comentário
│       │   ├── validador.py                # ValidadorAgent — arbitragem + feedback
│       │   └── subfoco_generator.py        # SubFocoGenerator — batch de 50 sub-focos
│       │
│       ├── providers/                      # Abstração de provedores LLM
│       │   ├── __init__.py
│       │   ├── base.py                     # LLMProvider (Protocol) — interface generate()
│       │   ├── openai_provider.py          # OpenAIProvider — wrapper async SDK openai
│       │   └── anthropic_provider.py       # AnthropicProvider — wrapper async SDK anthropic
│       │
│       ├── pipeline/                       # Orquestração do pipeline
│       │   ├── __init__.py
│       │   ├── orchestrator.py             # PipelineOrchestrator — fluxo Criador→Comentador→Validador
│       │   ├── batch_processor.py          # BatchProcessor — processamento em massa de focos
│       │   ├── retry.py                    # RetryManager — retry com feedback estruturado
│       │   ├── checkpoint.py               # CheckpointManager — checkpoints híbridos
│       │   └── balancer.py                 # StatisticalBalancer — balanceamento A/B/C/D
│       │
│       ├── io/                             # Input/Output — Excel e Pinecone
│       │   ├── __init__.py
│       │   ├── excel_reader.py             # ExcelReader — leitura + validação do input
│       │   ├── excel_writer.py             # ExcelWriter — escrita atômica do output (26 colunas)
│       │   └── pinecone_client.py          # PineconeClient — consulta RAG para Comentador
│       │
│       ├── metrics/                        # Coleta e armazenamento de métricas
│       │   ├── __init__.py
│       │   ├── collector.py                # MetricsCollector — tokens, custo, latência por chamada
│       │   └── store.py                    # MetricsStore — interface SQLite
│       │
│       ├── config/                         # Configuração e gestão de prompts
│       │   ├── __init__.py
│       │   ├── settings.py                 # PipelineConfig (Pydantic) — config centralizada
│       │   ├── prompt_loader.py            # PromptLoader — carrega templates de prompts/
│       │   └── exceptions.py               # Hierarquia de exceções customizadas
│       │
│       └── dashboard/                      # Streamlit dashboard
│           ├── __init__.py
│           ├── app.py                      # Entry point Streamlit
│           ├── pages/                      # Páginas do dashboard
│           │   ├── overview.py             # Progresso, aprovadas/rejeitadas/pendentes
│           │   ├── metrics.py              # Taxa aprovação, custo, latência, concordância
│           │   ├── model_comparison.py     # Comparativo entre modelos
│           │   ├── checkpoint_view.py      # Amostra para validação humana
│           │   └── incidents.py            # Log de incidentes
│           └── components/                 # Componentes reutilizáveis
│               ├── sidebar.py              # Sidebar: modelo, temperatura, retries, batch
│               └── question_card.py        # Card de visualização de questão
│
└── tests/
    ├── __init__.py
    ├── conftest.py                         # Fixtures compartilhadas (mock LLM, sample data)
    ├── test_models/
    │   ├── test_question.py
    │   └── test_feedback.py
    ├── test_agents/
    │   ├── test_criador.py
    │   └── test_validador.py
    ├── test_pipeline/
    │   ├── test_orchestrator.py
    │   ├── test_retry.py
    │   └── test_checkpoint.py
    └── test_io/
        ├── test_excel_reader.py
        └── test_excel_writer.py
```

### Requirements to Structure Mapping

| Categoria FR | Módulo Principal | Arquivos |
|-------------|-----------------|----------|
| Gestão de Input (FR1-FR3) | `io/` | `excel_reader.py`, `input_validator` (dentro do reader) |
| Pipeline de Geração (FR4-FR9) | `pipeline/` + `agents/` | `orchestrator.py`, `balancer.py`, `criador.py`, `subfoco_generator.py` |
| Qualidade e Validação (FR10-FR18) | `agents/` + `pipeline/` | `comentador.py`, `validador.py`, `checkpoint.py`, `retry.py` |
| RAG e Referências (FR19-FR22) | `io/` | `pinecone_client.py` |
| Output e Exportação (FR23-FR25) | `io/` | `excel_writer.py` |
| Métricas e Monitoramento (FR26-FR32) | `metrics/` + `dashboard/` | `collector.py`, `store.py`, `pages/*.py` |
| Configuração e Controle (FR33-FR38) | `config/` + `dashboard/` | `settings.py`, `prompt_loader.py`, `sidebar.py` |

### Architectural Boundaries

**Boundary 1: Agents ↔ Providers**
- Agentes NUNCA chamam SDKs diretamente
- Sempre via `LLMProvider.generate()` — permite trocar modelo sem tocar no agente
- Provider retorna response padronizada com `tokens_used`, `cost`, `latency`

**Boundary 2: Pipeline ↔ Agents**
- Pipeline orquestra a sequência, agentes executam tarefas isoladas
- Comunicação APENAS via Pydantic models (contratos definidos em `models/`)
- Pipeline decide retry/checkpoint, agente não sabe sobre batches

**Boundary 3: Pipeline ↔ IO**
- Pipeline não lê/escreve Excel diretamente
- `ExcelReader` entrega lista de focos como Pydantic models
- `ExcelWriter` recebe `QuestionRecord` e persiste
- `PineconeClient` é injetado no `ComentadorAgent`

**Boundary 4: Metrics ↔ Todos**
- `MetricsCollector` é passado como dependência a providers e pipeline
- Providers reportam tokens/custo/latência a cada chamada
- Pipeline reporta decisões (aprovação, retry, checkpoint)
- `MetricsStore` escreve em SQLite — dashboard lê de lá

**Boundary 5: Dashboard ↔ Pipeline**
- Dashboard lê dados do SQLite (read-only)
- Configuração escrita pelo dashboard salva em `PipelineConfig`
- Pipeline lê config no início de cada batch
- Sem comunicação real-time entre dashboard e pipeline em execução

### Data Flow

```
Excel Input (data/)
    → ExcelReader → List[FocoInput]
        → SubFocoGenerator → List[SubFocoInput] (batch de 50)
            → Para cada sub-foco:
                → StatisticalBalancer → posição correta sorteada
                → CriadorAgent → CriadorOutput
                → ComentadorAgent (+ PineconeClient RAG) → ComentadorOutput
                → ValidadorAgent → ValidadorOutput
                    → Aprovada → QuestionRecord → SQLite + ExcelWriter
                    → Rejeitada → RetryManager → volta ao CriadorAgent (max 3x)
                    → Falha final → fila revisão humana (status='failed' no SQLite)
            → A cada 10 focos → CheckpointManager → amostra 5 questões
                → Erro pontual → refaz questão individual
                → Erro sistêmico (3+) → pausa + ajuste parâmetros
    → Métricas por chamada → MetricsCollector → MetricsStore (SQLite)
    → Dashboard lê SQLite → Streamlit pages
Excel Output (output/)
    → ExcelWriter gera Excel final a partir do SQLite
```

### External Integrations

| Integração | Módulo | Protocolo |
|-----------|--------|-----------|
| OpenAI API | `providers/openai_provider.py` | HTTPS async, JSON mode, API key via env |
| Anthropic API | `providers/anthropic_provider.py` | HTTPS async, JSON mode, API key via env |
| Pinecone | `io/pinecone_client.py` | HTTPS, query por tema+foco, API key via env |

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
Todas as tecnologias funcionam juntas sem conflitos. Python 3.11+ com uv, ambos SDKs (openai, anthropic) com clientes async e JSON mode, Pydantic como espinha dorsal de contratos, SQLite stdlib para persistência, Streamlit para dashboard, pandas+openpyxl para Excel I/O, Pinecone para RAG. Nenhuma incompatibilidade de versão identificada.

**Pattern Consistency:**
PEP 8 com português nos campos de domínio — claro e consistente. Pydantic em todos os contratos (LLM output, entre agentes, config). Hierarquia de exceções alinhada com categorias do pipeline. asyncio + semáforo funciona com clientes async de ambos SDKs. Logging stdlib com formato estruturado.

**Structure Alignment:**
src/ layout com 8 módulos cobre todos os requisitos. 5 boundaries claramente definidos entre componentes. Fluxo de dados mapeado end-to-end. Tests/ espelha src/construtor/ para organização clara.

### Requirements Coverage Validation ✅

**Functional Requirements — 38/38 cobertos:**

| FR | Descrição | Suporte Arquitetural |
|----|-----------|---------------------|
| FR1-FR3 | Gestão de Input | `io/excel_reader.py` + validação |
| FR4 | Sub-focos em batch (50) | `agents/subfoco_generator.py` |
| FR5-FR9 | Geração de questões | `agents/criador.py` + `pipeline/balancer.py` |
| FR10-FR11 | Revisão cega + comentário | `agents/comentador.py` + `io/pinecone_client.py` |
| FR12-FR13 | Validação + feedback | `agents/validador.py` + `models/feedback.py` |
| FR14-FR15 | Retry + fila humana | `pipeline/retry.py` + SQLite status |
| FR16-FR18 | Checkpoints híbridos | `pipeline/checkpoint.py` + `dashboard/checkpoint_view.py` |
| FR19-FR22 | RAG + referências | `io/pinecone_client.py` + prompt restrictions |
| FR23-FR25 | Excel output + persistência | `io/excel_writer.py` + SQLite |
| FR26-FR32 | Métricas + monitoramento | `metrics/` + `dashboard/pages/` |
| FR33-FR38 | Configuração + controle | `config/settings.py` + `dashboard/sidebar.py` |

**Non-Functional Requirements — 24/24 cobertos:**

| NFR | Categoria | Suporte |
|-----|-----------|---------|
| NFR1-4 | Performance | asyncio + semáforo + SQLite intermediário |
| NFR5-7 | Segurança | .env + env vars |
| NFR8-10 | Integração | LLMProvider fallback + Pydantic parsing |
| NFR11-14 | Resiliência | SQLite persistence + atomic writes + fault isolation |
| NFR15-20 | Qualidade | Agent pipeline + prompts + validation |
| NFR21-24 | Custo | MetricsCollector + Dashboard |

### Implementation Readiness Validation ✅

**Decision Completeness:**
Todas as decisões críticas documentadas com rationale, versões e impacto. Exemplos de código para Pydantic models, exceções, async patterns. Anti-patterns documentados com exemplos concretos.

**Structure Completeness:**
40+ arquivos específicos mapeados a requisitos. Todos os módulos com responsabilidades claras. Nenhum placeholder genérico — todos os arquivos têm propósito definido.

**Pattern Completeness:**
8 categorias de conflito potencial identificadas e endereçadas. Convenções de nomenclatura cobrindo Python, SQLite, Pydantic. Error handling, logging, async, config — todos com padrões e exemplos.

### Gap Analysis Results

**Gaps Críticos:** Nenhum identificado.

**Gaps Importantes (não bloqueiam implementação):**

1. **Schema SQLite** — Tabelas e colunas não detalhados. Deriváveis dos Pydantic models durante implementação.
2. **Sync Dashboard ↔ Pipeline** — Pipeline lê config no início de cada batch (não real-time). Mudanças de config aplicam no próximo batch.
3. **Variáveis dos templates de prompt** — Serão definidas durante engenharia de prompts.

**Gaps Nice-to-Have (aceitáveis para MVP):**
- Sem CI/CD (único usuário, local)
- Estratégia de query Pinecone (threshold, campos) — durante implementação
- Sem migration strategy para SQLite (trivial para single-user)

### Architecture Completeness Checklist

**✅ Análise de Requisitos**

- [x] Contexto do projeto analisado
- [x] Escala e complexidade avaliadas
- [x] Constraints técnicos identificados
- [x] Cross-cutting concerns mapeados

**✅ Decisões Arquiteturais**

- [x] Decisões críticas documentadas com versões
- [x] Stack tecnológico totalmente especificado
- [x] Padrões de integração definidos
- [x] Performance endereçada

**✅ Padrões de Implementação**

- [x] Convenções de nomenclatura estabelecidas
- [x] Padrões estruturais definidos
- [x] Padrões de comunicação especificados
- [x] Padrões de processo documentados

**✅ Estrutura do Projeto**

- [x] Estrutura de diretórios completa
- [x] Boundaries estabelecidos
- [x] Pontos de integração mapeados
- [x] Requisitos mapeados à estrutura

### Architecture Readiness Assessment

**Status:** PRONTO PARA IMPLEMENTAÇÃO

**Nível de Confiança:** Alto — arquitetura coesa, 100% dos requisitos cobertos, padrões claros com exemplos e anti-patterns.

**Pontos Fortes:**
- Pydantic como espinha dorsal garante consistência entre todos os componentes
- Boundaries claros entre módulos previnem acoplamento
- Fluxo de dados documentado end-to-end
- 2 provedores (OpenAI + Anthropic) simplifica sem sacrificar comparativo
- Padrões com exemplos concretos e anti-patterns documentados

**Áreas para Aprimoramento Futuro:**
- Schema SQLite detalhado (durante implementação)
- Engenharia de prompts (pós-arquitetura)
- Estratégia de query Pinecone (durante integração)

### Implementation Handoff

**Diretrizes para Agentes de IA:**

- Seguir todas as decisões arquiteturais exatamente como documentadas
- Usar padrões de implementação consistentemente em todos os componentes
- Respeitar estrutura do projeto e boundaries
- Consultar este documento para todas as questões arquiteturais

**Primeira Prioridade de Implementação:**

```bash
uv init construtor-de-questoes --python 3.11
cd construtor-de-questoes
uv add openai anthropic pandas openpyxl pinecone pydantic streamlit
uv add --dev pytest ruff
```

Após scaffolding: implementar `models/` (Pydantic contracts) como fundação de tudo.
