---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', '_bmad-output/planning-artifacts/architecture.md']
---

# Construtor de Questões - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Construtor de Questões, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**1. Gestão de Input (FR1-FR3)**
- FR1: Rodrigo pode importar Excel de input contendo temas, focos e períodos
- FR2: O sistema valida a estrutura do Excel de input e reporta erros antes do processamento
- FR3: Rodrigo pode definir se sub-focos são gerados pela IA ou fornecidos manualmente

**2. Pipeline de Geração de Questões (FR4-FR9)**
- FR4: O sistema gera sub-focos em bloco (batch de 50) a partir de um foco
- FR5: O Agente Criador gera questão completa (enunciado + 4 alternativas + gabarito + objetivo educacional)
- FR6: O sistema sorteia a posição da alternativa correta (A/B/C/D) com balanceamento estatístico antes da geração
- FR7: O Agente Criador seleciona automaticamente o tipo de enunciado adequado ao tema, foco e nível
- FR8: O sistema aplica 3 níveis de dificuldade mapeados à Taxonomia de Bloom
- FR9: O sistema constrói distratores por natureza cognitiva do nível de dificuldade

**3. Qualidade e Validação (FR10-FR18)**
- FR10: O Agente Comentador analisa a questão sem conhecer o gabarito e declara qual alternativa considera correta
- FR11: O Agente Comentador gera comentário estruturado completo (Introdução → Visão Específica → Alt. por Alt. → Visão do Aprovado)
- FR12: O Agente Validador compara gabarito do Criador com resposta do Comentador e emite aprovação ou rejeição
- FR13: O Agente Validador fornece feedback por categorias de erro (enunciado ambíguo, distratores fracos, gabarito questionável, comentário incompleto, fora do nível)
- FR14: O sistema reenvia questões rejeitadas ao Criador com feedback do Validador (max 2-3 rodadas)
- FR15: O sistema encaminha questões sem aprovação após o limite para fila de revisão humana
- FR16: O sistema executa checkpoints a cada 10 focos, com amostra de 5 questões para validação humana
- FR17: O sistema diferencia erro pontual de erro sistêmico (3+) e aplica ação corretiva adequada
- FR18: Rodrigo pode aprovar ou rejeitar checkpoint e ajustar parâmetros antes de reprocessar o lote

**4. RAG e Referências Bibliográficas (FR19-FR22)**
- FR19: O Agente Comentador consulta documentos médicos curados no Pinecone (área "assistant")
- FR20: O sistema restringe referências a fontes permitidas por período/tema
- FR21: O sistema associa referência bibliográfica verificável a cada questão
- FR22: O sistema filtra questões com relevância clínica insuficiente ou ultraespecificidades

**5. Output e Exportação (FR23-FR25)**
- FR23: O sistema gera Excel de output com todas as 26 colunas do modelo de dados
- FR24: O sistema salva progresso parcial para recuperação em caso de falha
- FR25: O sistema exporta Excel final pronto para entrega à equipe de importação

**6. Métricas e Monitoramento (FR26-FR32)**
- FR26: O sistema registra métricas por questão: modelo, tokens, custo, rodadas, tempo, decisão
- FR27: Rodrigo visualiza taxa de aprovação em tempo real
- FR28: Rodrigo visualiza custo acumulado em tokens
- FR29: Rodrigo visualiza taxa de concordância Comentador vs gabarito
- FR30: Rodrigo compara qualidade, custo e velocidade entre modelos de LLM
- FR31: Rodrigo visualiza progresso total (geradas/total, aprovadas/rejeitadas/pendentes)
- FR32: O sistema registra log de incidentes (erros pontuais e sistêmicos)

**7. Configuração e Controle (FR33-FR38)**
- FR33: Rodrigo seleciona modelo de LLM
- FR34: Rodrigo ajusta temperatura de geração
- FR35: Rodrigo define limite de rodadas de retry
- FR36: Rodrigo define tamanho do batch e intervalo de checkpoints
- FR37: Rodrigo ajusta prompts dos agentes (Criador, Comentador, Validador)
- FR38: Rodrigo pode iniciar, pausar e retomar processamento em massa

### NonFunctional Requirements

**Performance (NFR1-NFR4)**
- NFR1: Latência média por questão completa (3 agentes) monitorada e otimizada para viabilizar ~8.000 questões no prazo
- NFR2: Processamento batch suporta execução contínua por horas sem degradação ou memory leaks
- NFR3: Chamadas paralelas (asyncio) respeitam rate limits com backoff exponencial
- NFR4: Escrita do Excel não bloqueia o pipeline — salvamentos parciais rápidos

**Segurança (NFR5-NFR7)**
- NFR5: API keys armazenadas em variáveis de ambiente ou .env, nunca hardcoded
- NFR6: Credenciais nunca commitadas em repositório
- NFR7: Acesso ao Pinecone via autenticação segura por API key

**Integração (NFR8-NFR10)**
- NFR8: Fallback gracioso quando API de LLM indisponível — modelo alternativo ou pausa
- NFR9: Consultas Pinecone com timeout configurável e fallback para geração sem RAG (questão flagada)
- NFR10: Parsing robusto com validação de estrutura para mudanças de formato das APIs

**Resiliência (NFR11-NFR14)**
- NFR11: Estado de progresso salvo a cada batch — retomada exata do ponto de parada
- NFR12: Crash não corrompe Excel parcial — escrita atômica ou arquivo temporário
- NFR13: Erros logados com contexto (questão, foco, modelo, rodada) para diagnóstico
- NFR14: Falha em questão individual não interrompe batch inteiro

**Qualidade de Conteúdo (NFR15-NFR20)**
- NFR15: Taxa de aprovação ≥ 85% na primeira rodada
- NFR16: 100% das questões aprovadas com comentário estruturado completo (5 seções)
- NFR17: 0% de referências bibliográficas inexistentes
- NFR18: Balanceamento da posição correta entre 20-30% para cada letra (A/B/C/D)
- NFR19: Cada alternativa errada com justificativa educacional no comentário
- NFR20: Terminologia médica em português brasileiro, contexto SUS

**Eficiência de Custo (NFR21-NFR24)**
- NFR21: Custo por questão aprovada registrado e monitorável
- NFR22: Comparação custo-benefício entre modelos antes da produção em massa
- NFR23: Custo incremental de retries rastreado separadamente
- NFR24: Dashboard exibe projeção de custo total (custo médio × questões restantes)

### Additional Requirements

**Da Arquitetura:**

- **Starter Template:** Scaffolding customizado com uv (`uv init construtor-de-questoes --python 3.11`) — impacta Epic 1 Story 1
- Abstração de provedores LLM via Protocol/ABC com método `generate()` — apenas OpenAI + Anthropic (Google/Gemini removido do escopo)
- Saída estruturada dos LLMs via Pydantic models + JSON mode dos SDKs
- Persistência de estado via SQLite (arquivo único, zero setup, escrita atômica para resiliência)
- Protocolo de comunicação entre agentes via Pydantic models: `CriadorOutput`, `ComentadorInput/Output`, `ValidadorInput/Output`, `FeedbackEstruturado`
- Estratégia async: asyncio com Semaphore para controle de concorrência
- Gerenciamento de prompts em arquivos Markdown separados na pasta `prompts/`
- Segurança: API keys via `.env` + carregamento do environment
- Hierarquia de exceções customizadas: `PipelineError` → `LLMProviderError`, `LLMRateLimitError`, `LLMTimeoutError`, `OutputParsingError`, `ValidationError`, `PineconeError`
- Estrutura src/ layout com 8 módulos: `models`, `agents`, `providers`, `pipeline`, `io`, `metrics`, `config`, `dashboard`
- 5 boundaries arquiteturais: Agents↔Providers, Pipeline↔Agents, Pipeline↔IO, Metrics↔Todos, Dashboard↔Pipeline
- Sequência de implementação: Pydantic models → LLM abstraction → SQLite → Agents → Pipeline → Prompts → Dashboard
- Convenções: código em inglês, campos de domínio médico/Excel em português. PEP 8 estrito, ruff para linting/formatting
- Dependências: `openai`, `anthropic`, `pandas`, `openpyxl`, `pinecone`, `pydantic`, `streamlit` (prod) + `pytest`, `ruff` (dev)

### FR Coverage Map

| FR | Epic | Descrição |
|----|------|-----------|
| FR1 | Epic 1 | Importar Excel de input |
| FR2 | Epic 1 | Validar estrutura do Excel |
| FR3 | Epic 2 | Sub-focos gerados pela IA ou manuais |
| FR4 | Epic 2 | Gerar sub-focos em batch de 50 |
| FR5 | Epic 2 | Criador gera questão completa |
| FR6 | Epic 2 | Sorteio balanceado da posição correta |
| FR7 | Epic 2 | Seleção automática do tipo de enunciado |
| FR8 | Epic 2 | 3 níveis de dificuldade (Bloom) |
| FR9 | Epic 2 | Distratores por natureza cognitiva |
| FR10 | Epic 2 | Comentador analisa sem conhecer gabarito |
| FR11 | Epic 2 | Comentário estruturado completo |
| FR12 | Epic 2 | Validador compara e arbitra |
| FR13 | Epic 2 | Feedback por categorias de erro |
| FR14 | Epic 2 | Retry com feedback (max 2-3 rodadas) |
| FR15 | Epic 2 | Fila de revisão humana |
| FR16 | Epic 3 | Checkpoints a cada 10 focos |
| FR17 | Epic 3 | Erro pontual vs sistêmico |
| FR18 | Epic 3 | Aprovar/rejeitar checkpoint + ajustar |
| FR19 | Epic 2 | Consulta Pinecone RAG |
| FR20 | Epic 2 | Restrição de fontes por período/tema |
| FR21 | Epic 2 | Referência verificável por questão |
| FR22 | Epic 2 | Filtro de relevância clínica |
| FR23 | Epic 1 | Excel output 26 colunas |
| FR24 | Epic 1 | Progresso parcial salvo |
| FR25 | Epic 3 | Excel final para entrega |
| FR26 | Epic 4 | Métricas por questão |
| FR27 | Epic 4 | Taxa aprovação tempo real |
| FR28 | Epic 4 | Custo acumulado |
| FR29 | Epic 4 | Concordância Comentador |
| FR30 | Epic 4 | Comparativo entre modelos |
| FR31 | Epic 4 | Progresso total |
| FR32 | Epic 4 | Log de incidentes |
| FR33 | Epic 4 | Selecionar modelo LLM |
| FR34 | Epic 4 | Ajustar temperatura |
| FR35 | Epic 4 | Limite de retries |
| FR36 | Epic 4 | Tamanho batch e intervalo checkpoints |
| FR37 | Epic 4 | Ajustar prompts |
| FR38 | Epic 3 | Iniciar/pausar/retomar processamento |

## Epic List

### Epic 1: Fundação do Projeto e Infraestrutura Core
Rodrigo pode inicializar o projeto, ler um Excel de input, escrever um Excel de output, e ter toda a infraestrutura pronta (modelos de dados, abstração LLM, persistência SQLite, hierarquia de exceções).
**FRs cobertos:** FR1, FR2, FR23, FR24
**NFRs endereçados:** NFR5-7 (segurança), NFR11-12 (resiliência base)

### Epic 2: Pipeline de Geração de Questão Completa
Rodrigo pode gerar questões completas passando pelos 3 agentes (Criador → Comentador cego com RAG → Validador árbitro), com sorteio balanceado da posição correta, retry automático com feedback estruturado, e fila de revisão humana para falhas.
**FRs cobertos:** FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR19, FR20, FR21, FR22
**NFRs endereçados:** NFR8-10 (integração/fallback), NFR15-20 (qualidade de conteúdo)

### Epic 3: Produção em Massa com Checkpoints
Rodrigo pode disparar produção em massa de milhares de questões, com checkpoints a cada 10 focos, detecção automática de erros sistêmicos vs pontuais, recuperação em caso de falha, e exportação do Excel final.
**FRs cobertos:** FR16, FR17, FR18, FR25, FR38
**NFRs endereçados:** NFR1-4 (performance/async), NFR13-14 (resiliência avançada)

### Epic 4: Dashboard de Métricas e Configuração
Rodrigo pode monitorar o pipeline em tempo real via Streamlit — taxa de aprovação, custo, concordância, comparativo entre modelos, visualização de checkpoints, log de incidentes — e configurar todos os parâmetros (modelo, temperatura, retries, batch size, prompts).
**FRs cobertos:** FR26, FR27, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR36, FR37
**NFRs endereçados:** NFR21-24 (eficiência de custo)

---

## Epic 1: Fundação do Projeto e Infraestrutura Core

Rodrigo pode inicializar o projeto, ler um Excel de input, escrever um Excel de output, e ter toda a infraestrutura pronta (modelos de dados, abstração LLM, persistência SQLite, hierarquia de exceções).

### Story 1.1: Inicializar Projeto e Estrutura Base

Como Rodrigo,
Eu quero inicializar o projeto com a estrutura de diretórios completa e dependências configuradas,
Para que eu tenha a fundação do projeto pronta para desenvolvimento.

**Acceptance Criteria:**

**Given** que não existe projeto inicializado
**When** executo o comando `uv init construtor-de-questoes --python 3.11`
**Then** o projeto é criado com Python 3.11+
**And** a estrutura de diretórios src/construtor/ é criada com os 8 módulos (models/, agents/, providers/, pipeline/, io/, metrics/, config/, dashboard/)
**And** todas as dependências são instaladas (`openai`, `anthropic`, `pandas`, `openpyxl`, `pinecone`, `pydantic`, `streamlit`)
**And** dependências de dev são instaladas (`pytest`, `ruff`)
**And** o arquivo pyproject.toml está configurado corretamente
**And** os diretórios prompts/, data/, output/ são criados
**And** o arquivo .env.example está presente com as variáveis OPENAI_API_KEY, ANTHROPIC_API_KEY, PINECONE_API_KEY
**And** o .gitignore está configurado para ignorar data/, output/, .env, *.db, __pycache__/

### Story 1.2: Criar Modelos Pydantic de Dados

Como Rodrigo,
Eu quero ter todos os modelos Pydantic definidos para estruturar os dados do sistema,
Para que todas as trocas de dados entre componentes sejam validadas e type-safe.

**Acceptance Criteria:**

**Given** que a estrutura do projeto está inicializada
**When** implemento os modelos Pydantic em src/construtor/models/
**Then** o módulo models/question.py contém os modelos CriadorOutput com todos os campos (enunciado, alternativa_a/b/c/d, resposta_correta, objetivo_educacional, nivel_dificuldade, tipo_enunciado)
**And** o modelo QuestionRecord contém as 26 colunas do Excel de output (tema, foco, sub_foco, periodo, nivel_dificuldade, tipo_enunciado, enunciado, alternativa_a/b/c/d, resposta_correta, objetivo_educacional, comentario_introducao, comentario_visao_especifica, comentario_alt_a/b/c/d, comentario_visao_aprovado, referencia_bibliografica, suporte_imagem, fonte_imagem, modelo_llm, rodadas_validacao, concordancia_comentador)
**And** o módulo models/feedback.py contém ComentadorOutput e ValidadorOutput com campos estruturados
**And** o módulo models/feedback.py contém FeedbackEstruturado com categorias de erro (enunciado_ambiguo, distratores_fracos, gabarito_questionavel, comentario_incompleto, fora_do_nivel)
**And** o módulo models/pipeline.py contém BatchState, CheckpointResult, RetryContext
**And** o módulo models/metrics.py contém QuestionMetrics (modelo, tokens, custo, rodadas, tempo, decisao), BatchMetrics, ModelComparison
**And** todos os modelos usam model_config = ConfigDict(strict=True)
**And** campos obrigatórios não têm default, campos opcionais usam Optional com default
**And** campos de domínio médico/Excel estão em português (enunciado, alternativa_a, resposta_correta)

### Story 1.3: Implementar Abstração de Provedores LLM

Como Rodrigo,
Eu quero uma abstração unificada para chamar OpenAI e Anthropic,
Para que eu possa trocar modelos facilmente e comparar custos/qualidade sem alterar código dos agentes.

**Acceptance Criteria:**

**Given** que os modelos Pydantic estão criados
**When** implemento a abstração de provedores LLM em src/construtor/providers/
**Then** o módulo providers/base.py define LLMProvider como Protocol com método async generate(prompt: str, model: str, temperature: float) -> dict
**And** o método generate() retorna dict com campos: content (str), tokens_used (int), cost (float), latency (float)
**And** o módulo providers/openai_provider.py implementa OpenAIProvider usando o SDK openai com cliente async
**And** OpenAIProvider suporta JSON mode e parsing para Pydantic models
**And** o módulo providers/anthropic_provider.py implementa AnthropicProvider usando o SDK anthropic com cliente async
**And** AnthropicProvider suporta JSON mode e parsing para Pydantic models
**And** ambos providers calculam custo em tokens baseado no modelo usado
**And** ambos providers respeitam o Semaphore de concorrência passado no construtor
**And** ambos providers implementam backoff exponencial com jitter para rate limits (NFR3)
**And** ambos providers têm timeout configurável por chamada
**And** erros de API lançam LLMProviderError, rate limits lançam LLMRateLimitError, timeouts lançam LLMTimeoutError

### Story 1.4: Configurar SQLite para Persistência de Estado

Como Rodrigo,
Eu quero um banco SQLite para persistir o estado do pipeline e métricas,
Para que o progresso seja salvo e eu possa retomar de onde parei em caso de falha (NFR11, NFR12).

**Acceptance Criteria:**

**Given** que os modelos Pydantic estão definidos
**When** implemento a camada de persistência SQLite em src/construtor/metrics/store.py
**Then** o módulo metrics/store.py cria um banco SQLite em output/pipeline_state.db
**And** a tabela `questions` é criada com colunas mapeadas aos campos de QuestionRecord
**And** a coluna id é INTEGER PRIMARY KEY AUTOINCREMENT
**And** colunas de timestamp usam formato ISO 8601 string
**And** colunas booleanas usam INTEGER (0/1)
**And** a coluna status usa TEXT com CHECK constraint (status IN ('pending','approved','rejected','failed'))
**And** a tabela `metrics` é criada para armazenar QuestionMetrics por questão
**And** a tabela `checkpoints` é criada para armazenar CheckpointResult
**And** todas as escritas são atômicas usando transações SQLite
**And** o módulo fornece métodos: save_question(), update_question_status(), get_questions_by_status(), save_metrics(), get_batch_progress()
**And** nomenclatura segue snake_case para tabelas (plural) e colunas
**And** escrita não bloqueia o pipeline (NFR4)

### Story 1.5: Implementar Leitor de Excel de Input

Como Rodrigo,
Eu quero importar um Excel de input com temas, focos e períodos,
Para que o sistema possa processar os dados estruturados e gerar questões (FR1, FR2).

**Acceptance Criteria:**

**Given** que tenho um arquivo Excel com colunas tema, foco, periodo
**When** executo ExcelReader.read_input(file_path) em src/construtor/io/excel_reader.py
**Then** o sistema lê o Excel usando pandas + openpyxl
**And** valida que as colunas obrigatórias (tema, foco, periodo) existem
**And** valida que periodo contém apenas valores válidos (1º ano, 2º ano, 3º ano, 4º ano)
**And** valida que não há linhas com dados faltantes nas colunas obrigatórias
**And** retorna uma lista de objetos Pydantic FocoInput(tema: str, foco: str, periodo: str)
**And** se a validação falhar, lança ValidationError com mensagem clara indicando qual coluna/linha tem problema
**And** se o arquivo não existir, lança FileNotFoundError
**And** se o formato não for Excel válido, lança OutputParsingError
**And** logs estruturados são gerados com INFO para sucesso, ERROR para falhas

### Story 1.6: Implementar Escritor de Excel de Output

Como Rodrigo,
Eu quero exportar questões aprovadas para um Excel com as 26 colunas estruturadas,
Para que eu possa entregar o arquivo final à equipe de importação (FR23, FR25).

**Acceptance Criteria:**

**Given** que tenho questões aprovadas salvas no SQLite
**When** executo ExcelWriter.export_to_excel(output_path) em src/construtor/io/excel_writer.py
**Then** o sistema lê todas as questões com status='approved' do SQLite
**And** cria um DataFrame pandas com as 26 colunas na ordem: tema, foco, sub_foco, periodo, nivel_dificuldade, tipo_enunciado, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, resposta_correta, objetivo_educacional, comentario_introducao, comentario_visao_especifica, comentario_alt_a, comentario_alt_b, comentario_alt_c, comentario_alt_d, comentario_visao_aprovado, referencia_bibliografica, suporte_imagem, fonte_imagem, modelo_llm, rodadas_validacao, concordancia_comentador
**And** escreve o Excel usando openpyxl com formatação básica (header em negrito)
**And** a escrita é atômica usando arquivo temporário + rename para evitar corrupção (NFR12)
**And** se o caminho de output não existir, cria os diretórios necessários
**And** se a escrita falhar, lança IOError com contexto do erro
**And** logs estruturados registram INFO com número de questões exportadas e caminho do arquivo
**And** progresso não é perdido em caso de crash (NFR12)

### Story 1.7: Criar Hierarquia de Exceções Customizadas

Como Rodrigo,
Eu quero exceções customizadas que categorizam erros do pipeline,
Para que eu possa tratar cada tipo de erro adequadamente e ter logs claros (NFR13).

**Acceptance Criteria:**

**Given** que o projeto está inicializado
**When** implemento a hierarquia de exceções em src/construtor/config/exceptions.py
**Then** PipelineError é a exceção base que herda de Exception
**And** LLMProviderError herda de PipelineError
**And** LLMRateLimitError herda de LLMProviderError
**And** LLMTimeoutError herda de LLMProviderError
**And** OutputParsingError herda de PipelineError
**And** ValidationError herda de PipelineError
**And** PineconeError herda de PipelineError
**And** cada exceção aceita mensagem customizada no construtor
**And** cada exceção pode armazenar contexto adicional (question_id, foco, modelo, rodada) como atributos
**And** nenhum código usa bare except - sempre exceções específicas
**And** tratamento segue: try/except específico, falha em questão individual → log + continue (NFR14)

### Story 1.8: Configurar Gerenciamento de Secrets (.env)

Como Rodrigo,
Eu quero armazenar API keys em variáveis de ambiente,
Para que credenciais nunca sejam commitadas e o sistema seja seguro (NFR5, NFR6, NFR7).

**Acceptance Criteria:**

**Given** que o arquivo .env.example existe
**When** crio um arquivo .env na raiz do projeto
**Then** o .env contém as variáveis OPENAI_API_KEY, ANTHROPIC_API_KEY, PINECONE_API_KEY
**And** o módulo src/construtor/config/settings.py carrega variáveis do .env usando python-dotenv ou similar
**And** o modelo PipelineConfig (Pydantic) lê secrets do environment
**And** se uma API key obrigatória não for encontrada, o sistema lança ConfigurationError com mensagem clara
**And** o .gitignore garante que .env NUNCA é commitado
**And** .env.example documenta cada variável com descrição e exemplo (valor fake)
**And** nenhuma credencial é hardcoded em código
**And** logs nunca imprimem valores de API keys (máscara parcial se necessário: "sk-...xyz")

---

## Epic 2: Pipeline de Geração de Questão Completa

Rodrigo pode gerar questões completas passando pelos 3 agentes (Criador → Comentador cego com RAG → Validador árbitro), com sorteio balanceado da posição correta, retry automático com feedback estruturado, e fila de revisão humana para falhas.

### Story 2.1: Implementar Gerador de Sub-focos

Como Rodrigo,
Eu quero gerar sub-focos em lote (batch de 50) a partir de um foco,
Para que cada sub-foco se torne uma questão específica e o sistema tenha granularidade adequada (FR3, FR4).

**Acceptance Criteria:**

**Given** que tenho um FocoInput (tema, foco, periodo)
**When** executo SubFocoGenerator.generate_batch(foco_input, count=50) em src/construtor/agents/subfoco_generator.py
**Then** o agente carrega o prompt de prompts/subfoco_generator.md
**And** o prompt contém variáveis {tema}, {foco}, {periodo}, {count}
**And** o agente usa LLMProvider para gerar o batch de sub-focos
**And** o agente valida que exatamente 50 sub-focos foram gerados
**And** cada sub-foco é uma string específica e única (sem duplicatas no batch)
**And** sub-focos são relevantes ao tema/foco e apropriados ao período acadêmico
**And** retorna uma lista de SubFocoInput(tema, foco, sub_foco, periodo)
**And** métricas da chamada (tokens, custo, latência) são registradas via MetricsCollector
**And** se o LLM retornar menos de 50, o sistema tenta novamente (max 2 retries)
**And** se após retries não conseguir 50, lança OutputParsingError
**And** logs estruturados registram INFO com número de sub-focos gerados

### Story 2.2: Implementar Agente Criador de Questões

Como Rodrigo,
Eu quero que o Agente Criador gere questão completa (enunciado + 4 alternativas + gabarito + objetivo educacional),
Para que eu tenha a questão base para o pipeline de validação (FR5, FR7, FR8, FR9).

**Acceptance Criteria:**

**Given** que tenho um SubFocoInput e a posição da correta pré-sorteada (ex: "B")
**When** executo CriadorAgent.create_question(subfoco_input, posicao_correta) em src/construtor/agents/criador.py
**Then** o agente carrega o prompt de prompts/criador.md
**And** o prompt contém instruções para Taxonomia de Bloom (3 níveis de dificuldade)
**And** o prompt instrui a criar distratores por natureza cognitiva do nível (FR9)
**And** o prompt inclui variáveis {tema}, {foco}, {sub_foco}, {periodo}, {posicao_correta}, {nivel_dificuldade}
**And** o agente seleciona automaticamente o tipo de enunciado adequado (conceitual, caso clínico, interpretação de dados, etc.) (FR7)
**And** o agente usa LLMProvider com JSON mode para gerar CriadorOutput
**And** CriadorOutput contém: enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, resposta_correta (A/B/C/D), objetivo_educacional, nivel_dificuldade (1/2/3), tipo_enunciado
**And** a alternativa correta está na posição especificada (posicao_correta)
**And** as 3 alternativas incorretas (distratores) refletem erros cognitivos reais de alunos no nível especificado (FR9)
**And** o enunciado é preciso, completo e não ambíguo
**And** métricas da chamada são registradas via MetricsCollector
**And** se o parsing JSON falhar, lança OutputParsingError
**And** logs estruturados registram INFO com question_id, foco, nível, tipo de enunciado

### Story 2.3: Implementar Balanceamento Estatístico da Posição Correta

Como Rodrigo,
Eu quero que o sistema sorteie a posição da alternativa correta (A/B/C/D) com balanceamento estatístico,
Para que não haja viés de construção e o balanceamento fique entre 20-30% por letra (FR6, NFR18).

**Acceptance Criteria:**

**Given** que tenho um conjunto de questões a gerar
**When** executo StatisticalBalancer.get_next_position() em src/construtor/pipeline/balancer.py
**Then** o balanceador mantém contadores internos para A, B, C, D
**And** o balanceador sorteia a próxima posição com probabilidade ajustada para balancear
**And** posições com menor contagem têm maior probabilidade de serem sorteadas
**And** após N questões, a distribuição está entre 20-30% para cada letra (NFR18)
**And** o balanceador persiste o estado no SQLite (tabela balancer_state)
**And** em caso de retomada, o balanceador carrega o estado do SQLite (NFR11)
**And** o método reset() reinicia os contadores
**And** o método get_statistics() retorna dict com contagens e percentuais atuais
**And** logs estruturados registram DEBUG a cada sorteio com posição escolhida e estatísticas atuais

### Story 2.4: Implementar Cliente Pinecone para RAG

Como Rodrigo,
Eu quero que o sistema consulte documentos médicos curados no Pinecone,
Para que o Comentador tenha contexto verificável e referências bibliográficas reais (FR19, NFR17).

**Acceptance Criteria:**

**Given** que tenho acesso à área "assistant" no Pinecone com documentos curados
**When** executo PineconeClient.query(tema, foco, periodo) em src/construtor/io/pinecone_client.py
**Then** o cliente se conecta ao Pinecone usando PINECONE_API_KEY do environment (NFR7)
**And** a query usa tema + foco como texto de busca
**And** o cliente filtra por metadata.periodo se aplicável
**And** retorna top K documentos relevantes (K configurável, default=5)
**And** cada documento retornado contém: texto, metadata (título, autores, ano, fonte)
**And** o cliente tem timeout configurável (default 5s)
**And** se timeout ocorrer, lança PineconeError com contexto (NFR9)
**And** se a conexão falhar, lança PineconeError com fallback None (NFR9)
**And** fallback None permite geração sem RAG, mas a questão é flagada com "rag_unavailable=True" no SQLite
**And** métricas da query (latência, número de docs retornados) são registradas
**And** logs estruturados registram INFO com tema/foco e número de docs encontrados, WARNING se fallback

### Story 2.5: Implementar Agente Comentador com Revisão Cega

Como Rodrigo,
Eu quero que o Agente Comentador analise a questão SEM conhecer o gabarito e gere comentário estruturado completo,
Para que eu tenha validação real da questão e comentários pedagógicos de qualidade (FR10, FR11, FR20, FR21, FR22, NFR16, NFR17, NFR19, NFR20).

**Acceptance Criteria:**

**Given** que tenho uma questão gerada pelo Criador e contexto RAG do Pinecone
**When** executo ComentadorAgent.review_question(criador_output, rag_context) em src/construtor/agents/comentador.py
**Then** o agente carrega o prompt de prompts/comentador.md
**And** o prompt NÃO inclui a resposta_correta (revisão cega) (FR10)
**And** o prompt inclui o contexto RAG com documentos do Pinecone
**And** o prompt instrui a análise completa da questão e escolha da alternativa considerada correta
**And** o prompt instrui a geração de comentário em 5 seções: Introdução, Visão Específica, Comentário Alternativa A, Comentário Alternativa B, Comentário Alternativa C, Comentário Alternativa D, Visão do Aprovado
**And** o prompt restringe referências a fontes permitidas por período/tema (FR20)
**And** o prompt instrui a filtrar ultraespecificidades e manter relevância clínica (FR22)
**And** o prompt instrui terminologia médica em português brasileiro e contexto SUS (NFR20)
**And** o agente usa LLMProvider com JSON mode para gerar ComentadorOutput
**And** ComentadorOutput contém: resposta_declarada (A/B/C/D), comentario_introducao, comentario_visao_especifica, comentario_alt_a, comentario_alt_b, comentario_alt_c, comentario_alt_d, comentario_visao_aprovado, referencia_bibliografica
**And** cada alternativa errada tem justificativa educacional no comentário (NFR19)
**And** a referência bibliográfica é verificável e vem do contexto RAG (NFR17, FR21)
**And** se RAG estiver indisponível, referência_bibliografica = "Fonte não disponível (RAG offline)" e questão é flagada
**And** métricas da chamada são registradas via MetricsCollector
**And** logs estruturados registram INFO com question_id, resposta_declarada, concordância (se comparado com gabarito depois)

### Story 2.6: Implementar Agente Validador Árbitro

Como Rodrigo,
Eu quero que o Agente Validador compare o gabarito do Criador com a resposta do Comentador e forneça feedback estruturado,
Para que questões ambíguas sejam detectadas e rejeitadas com feedback claro para retry (FR12, FR13, NFR15).

**Acceptance Criteria:**

**Given** que tenho CriadorOutput e ComentadorOutput
**When** executo ValidadorAgent.validate(criador_output, comentador_output) em src/construtor/agents/validador.py
**Then** o agente carrega o prompt de prompts/validador.md
**And** o prompt inclui ambos outputs completos (gabarito + resposta declarada)
**And** o prompt instrui a comparar resposta_correta (Criador) com resposta_declarada (Comentador)
**And** o prompt define critérios de qualidade: enunciado claro, distratores plausíveis, gabarito indiscutível, comentário completo, nível adequado
**And** o agente usa LLMProvider com JSON mode para gerar ValidadorOutput
**And** ValidadorOutput contém: decisao ("aprovada" ou "rejeitada"), concordancia (boolean), feedback_estruturado (FeedbackEstruturado)
**And** FeedbackEstruturado contém campos: enunciado_ambiguo (boolean), distratores_fracos (boolean), gabarito_questionavel (boolean), comentario_incompleto (boolean), fora_do_nivel (boolean), observacoes (str)
**And** se concordancia=True e qualidade OK, decisao="aprovada"
**And** se concordancia=False (discordância), decisao="rejeitada" com feedback detalhado (FR12, FR13)
**And** se concordancia=True mas qualidade insuficiente, decisao="rejeitada" com feedback
**And** taxa de aprovação na primeira rodada deve tender a ≥85% após calibração (NFR15)
**And** métricas da chamada são registradas via MetricsCollector
**And** logs estruturados registram INFO com question_id, decisao, concordancia, categorias de erro

### Story 2.7: Implementar Sistema de Retry com Feedback Estruturado

Como Rodrigo,
Eu quero que questões rejeitadas sejam reenviadas ao Criador com feedback do Validador até aprovação ou limite de rodadas,
Para que o sistema melhore automaticamente as questões sem intervenção manual (FR14, FR15, NFR14).

**Acceptance Criteria:**

**Given** que uma questão foi rejeitada pelo Validador
**When** executo RetryManager.handle_retry(subfoco_input, feedback_estruturado, rodada_atual) em src/construtor/pipeline/retry.py
**Then** o sistema verifica se rodada_atual < MAX_RETRIES (configurável, default=3)
**And** se ainda há retries disponíveis, reenviar ao CriadorAgent com feedback_estruturado no prompt
**And** o prompt do Criador no retry inclui o FeedbackEstruturado como contexto de melhoria
**And** o Criador gera nova versão da questão considerando o feedback
**And** a nova questão passa novamente por Comentador → Validador
**And** métricas registram que esta é rodada N para esta questão
**And** custo incremental de retries é rastreado separadamente (NFR23)
**And** se após MAX_RETRIES (default=3) a questão não for aprovada, decisao_final="failed"
**And** questões com status="failed" vão para fila de revisão humana (FR15)
**And** SQLite salva status="failed" e feedback_final para revisão posterior
**And** falha em questão individual NÃO interrompe o batch (NFR14)
**And** logs estruturados registram WARNING para retry, ERROR para failed após limite
**And** logs incluem question_id, foco, rodada, categorias de erro

### Story 2.8: Implementar Orquestrador do Pipeline Multi-Agente

Como Rodrigo,
Eu quero um orquestrador que execute o fluxo completo Criador → Comentador → Validador com retry automático,
Para que uma questão seja processada end-to-end com governança multi-agente completa (integração de FR4-FR15).

**Acceptance Criteria:**

**Given** que tenho todos os agentes implementados (Criador, Comentador, Validador) e componentes (Balancer, PineconeClient, RetryManager)
**When** executo PipelineOrchestrator.process_question(subfoco_input) em src/construtor/pipeline/orchestrator.py
**Then** o orquestrador segue o fluxo: 1) Sortear posição correta via StatisticalBalancer
**And** 2) Gerar questão via CriadorAgent
**And** 3) Consultar contexto RAG via PineconeClient
**And** 4) Analisar via ComentadorAgent (revisão cega)
**And** 5) Validar via ValidadorAgent
**And** se aprovada: salvar QuestionRecord no SQLite com status='approved'
**And** se rejeitada: acionar RetryManager para nova rodada (max 3)
**And** se falhar após retries: salvar com status='failed' para revisão humana (FR15)
**And** todas as chamadas são async usando asyncio
**And** todas as chamadas passam pelo Semaphore de concorrência (NFR3)
**And** métricas completas por questão são salvas: modelo usado, tokens totais, custo total, rodadas, tempo total, concordância, decisão final
**And** se LLM provider falhar, tentar fallback para outro provider (NFR8)
**And** se parsing falhar em qualquer agente, tratar como OutputParsingError e fazer retry
**And** logs estruturados registram cada etapa com question_id e foco como contexto
**And** o orquestrador retorna QuestionResult(status, question_record, metrics)

---

## Epic 3: Produção em Massa com Checkpoints

Rodrigo pode disparar produção em massa de milhares de questões, com checkpoints a cada 10 focos, detecção automática de erros sistêmicos vs pontuais, recuperação em caso de falha, e exportação do Excel final.

### Story 3.1: Implementar Processador de Batch para Produção em Massa

Como Rodrigo,
Eu quero processar centenas de focos em batch gerando milhares de questões,
Para que eu consiga produzir ~8.000 questões no prazo com processamento paralelo eficiente (FR38, NFR1, NFR2, NFR3).

**Acceptance Criteria:**

**Given** que tenho uma lista de FocoInput do Excel de input
**When** executo BatchProcessor.process_all(focos_list) em src/construtor/pipeline/batch_processor.py
**Then** o processador gera sub-focos (batch de 50) para cada foco
**And** para cada sub-foco, aciona PipelineOrchestrator.process_question() de forma assíncrona
**And** usa asyncio.gather() com chunks para paralelizar sem saturar APIs
**And** respeita o Semaphore de concorrência configurado (default=5, configurável) (NFR3)
**And** implementa backoff exponencial com jitter para rate limits (NFR3)
**And** o processamento pode rodar continuamente por horas sem degradação ou memory leaks (NFR2)
**And** latência média por questão completa (3 agentes) é monitorada (NFR1)
**And** progresso é exibido no console: "Processando foco X/Y — Questões: aprovadas/rejeitadas/failed"
**And** métricas agregadas são atualizadas em tempo real (taxa de aprovação, custo acumulado, latência média)
**And** cada batch de sub-focos é persistido no SQLite antes do processamento
**And** se um sub-foco falhar, continua processando os demais (NFR14)
**And** logs estruturados registram INFO para início/fim de cada foco, com estatísticas do batch

### Story 3.2: Implementar Sistema de Checkpoints a Cada 10 Focos

Como Rodrigo,
Eu quero checkpoints automáticos a cada 10 focos processados, com amostra de 5 questões para validação humana,
Para que eu possa validar qualidade periodicamente e intervir antes de processar milhares de questões ruins (FR16, FR18).

**Acceptance Criteria:**

**Given** que estou processando um batch de focos
**When** completo 10 focos, o sistema aciona CheckpointManager.create_checkpoint() em src/construtor/pipeline/checkpoint.py
**Then** o checkpoint coleta estatísticas do bloco de 10 focos: total geradas, aprovadas, rejeitadas, failed, taxa de aprovação, concordância média, custo total
**And** o checkpoint seleciona aleatoriamente 5 questões aprovadas do bloco para amostra
**And** as 5 questões são salvas na tabela `checkpoints` com checkpoint_id, foco_range (ex: "Focos 1-10"), sample_question_ids (array de IDs)
**And** o sistema PAUSA o processamento e aguarda aprovação humana
**And** Rodrigo visualiza as 5 questões (enunciado + alternativas + comentário) via interface
**And** Rodrigo pode: [A] Aprovar e Continuar, [R] Rejeitar e Ajustar Parâmetros, [V] Ver Métricas Detalhadas
**And** se Rodrigo aprova [A], o processamento retoma do foco 11
**And** se Rodrigo rejeita [R], o sistema permite ajustar modelo, temperatura, prompts (FR18)
**And** após ajuste, Rodrigo pode optar por: [C] Reprocessar os 10 focos, [S] Seguir com novos parâmetros (descarta os 10)
**And** checkpoint_id e decisão (approved/adjusted) são salvos no SQLite
**And** logs estruturados registram INFO para checkpoint criado, com estatísticas e decisão do usuário

### Story 3.3: Implementar Detecção de Erros Sistêmicos vs Pontuais

Como Rodrigo,
Eu quero que o sistema diferencie automaticamente erro pontual (refaz questão) de erro sistêmico (3+ falhas → ajusta parâmetro),
Para que problemas estruturais sejam detectados precocemente e não propaguem (FR17).

**Acceptance Criteria:**

**Given** que estou processando um batch de sub-focos
**When** uma questão falha (status='failed' após retries), o sistema analisa via CheckpointManager.analyze_errors()
**Then** o sistema conta falhas consecutivas no bloco atual (últimos 10 sub-focos processados)
**And** se 1-2 falhas pontuais: registra como erro_pontual, continua processando
**And** se 3+ falhas com MESMO padrão de erro (ex: 3+ "enunciado_ambiguo"): classifica como erro_sistêmico
**And** erro sistêmico aciona pausa automática do pipeline com alerta: "ERRO SISTÊMICO DETECTADO: [categoria] em 3+ questões"
**And** o sistema apresenta análise: categoria de erro predominante, focos afetados, sugestões de ajuste
**And** Rodrigo pode: [A] Ajustar Parâmetros, [I] Ignorar e Continuar, [R] Reprocessar Lote
**And** se ajusta parâmetros [A], o sistema marca o bloco para reprocessamento
**And** métricas de erro sistêmico vs pontual são rastreadas separadamente
**And** logs estruturados registram CRITICAL para erro sistêmico com detalhamento
**And** dashboard exibe incidentes pontuais e sistêmicos em seções separadas (FR32)

### Story 3.4: Implementar Persistência e Recuperação de Progresso

Como Rodrigo,
Eu quero que o progresso seja salvo continuamente e recuperável após crash ou interrupção,
Para que eu nunca perca trabalho e possa retomar exatamente de onde parei (FR24, NFR11, NFR12, NFR13).

**Acceptance Criteria:**

**Given** que estou processando um batch de milhares de questões
**When** o sistema salva progresso a cada batch (10 focos ou configurável)
**Then** o SQLite persiste: batch_state (foco_atual, sub_foco_atual, total_processados), todas as questões geradas (status, métricas), checkpoints criados, balancer_state
**And** todas as escritas são atômicas usando transações SQLite (NFR12)
**And** se o sistema crashar, nenhum dado do SQLite é corrompido (NFR12)
**And** ao reiniciar, BatchProcessor.resume() carrega o último batch_state
**And** o sistema retoma exatamente do próximo sub-foco não processado (NFR11)
**And** questões já aprovadas/failed não são reprocessadas
**And** o balanceador de posições retoma com os contadores corretos
**And** métricas acumuladas (custo, tokens, latência média) são preservadas
**And** logs estruturados registram INFO ao salvar progresso: "Checkpoint salvo — Foco X/Y, Questões: Z aprovadas"
**And** logs registram INFO ao retomar: "Retomando do Foco X — Questões já processadas: Y"
**And** erros durante persistência são logados com contexto completo (question_id, foco, modelo, rodada) (NFR13)

### Story 3.5: Implementar Controles de Iniciar/Pausar/Retomar Processamento

Como Rodrigo,
Eu quero iniciar, pausar e retomar o processamento em massa a qualquer momento,
Para que eu tenha controle total sobre a execução do pipeline (FR38).

**Acceptance Criteria:**

**Given** que o BatchProcessor está implementado
**When** executo o comando `uv run python -m construtor --start input.xlsx` no terminal
**Then** o sistema carrega focos do Excel, valida, e inicia processamento em massa
**And** a qualquer momento, posso pausar com Ctrl+C (SIGINT) ou comando `--pause`
**And** ao pausar, o sistema finaliza o sub-foco atual (não interrompe no meio) e salva estado
**And** logs registram INFO: "Pausa solicitada — finalizando sub-foco atual..."
**And** após pausa, posso retomar com `uv run python -m construtor --resume`
**And** o sistema carrega batch_state do SQLite e retoma do próximo sub-foco
**And** posso forçar reinício do zero com `uv run python -m construtor --restart` (apaga batch_state, mantém questões já aprovadas)
**And** posso verificar status atual com `uv run python -m construtor --status`
**And** comando --status exibe: foco atual, progresso (X/Y), questões (aprovadas/rejeitadas/failed), custo acumulado, tempo decorrido, tempo estimado restante
**And** se tento iniciar enquanto já está rodando, o sistema exibe erro: "Pipeline já em execução"
**And** logs estruturados registram INFO para start/pause/resume/restart com timestamp

### Story 3.6: Implementar Exportação Final de Excel Completo

Como Rodrigo,
Eu quero exportar o Excel final com todas as questões aprovadas após a produção em massa,
Para que eu possa entregar o arquivo estruturado à equipe de importação (FR25).

**Acceptance Criteria:**

**Given** que completei o processamento em massa (todos os focos processados)
**When** executo BatchProcessor.finalize() ou comando `uv run python -m construtor --export`
**Then** o sistema chama ExcelWriter.export_to_excel("output/questoes_finais.xlsx")
**And** o Excel contém TODAS as questões com status='approved' do SQLite
**And** questões estão ordenadas por: tema, foco, sub_foco
**And** todas as 26 colunas estão preenchidas corretamente
**And** o sistema valida que 0% das questões têm referência_bibliografica faltando ou fake (NFR17)
**And** o sistema valida que balanceamento de posição correta está entre 20-30% por letra (NFR18)
**And** o sistema gera relatório final: total de questões, taxa de aprovação global, custo total, tempo total, questões failed (para revisão humana)
**And** relatório final é salvo em output/relatorio_final.txt
**And** se há questões com status='failed', gera Excel separado output/questoes_revisar.xlsx
**And** logs estruturados registram INFO: "Exportação concluída — X questões aprovadas em output/questoes_finais.xlsx"
**And** logs registram WARNING se há questões failed: "Y questões para revisão humana em output/questoes_revisar.xlsx"

---

## Epic 4: Dashboard de Métricas e Configuração

Rodrigo pode monitorar o pipeline em tempo real via Streamlit — taxa de aprovação, custo, concordância, comparativo entre modelos, visualização de checkpoints, log de incidentes — e configurar todos os parâmetros (modelo, temperatura, retries, batch size, prompts).

### Story 4.1: Implementar Entry Point do Dashboard Streamlit

Como Rodrigo,
Eu quero um dashboard Streamlit funcional que conecta ao SQLite e exibe dados do pipeline,
Para que eu tenha uma interface visual para monitorar e configurar o sistema.

**Acceptance Criteria:**

**Given** que o SQLite está configurado com as tabelas necessárias
**When** executo `uv run streamlit run src/construtor/dashboard/app.py`
**Then** o dashboard Streamlit inicia na porta padrão (8501)
**And** o app.py carrega PipelineConfig do environment
**And** o app.py conecta ao SQLite em output/pipeline_state.db
**And** a navegação lateral exibe menu com 5 páginas: Overview, Métricas, Comparativo de Modelos, Checkpoint View, Log de Incidentes
**And** a página inicial (Overview) é carregada por padrão
**And** o título principal exibe: "Construtor de Questões — Dashboard de Monitoramento"
**And** se o SQLite não existir, exibe mensagem: "Nenhum dado disponível. Execute o pipeline primeiro."
**And** o dashboard atualiza automaticamente a cada 5 segundos (configurável via st.rerun())
**And** todos os componentes usam tema padrão do Streamlit com layout "wide"
**And** logs estruturados registram INFO quando dashboard é iniciado

### Story 4.2: Implementar Página de Overview

Como Rodrigo,
Eu quero ver progresso total, questões geradas/aprovadas/rejeitadas/failed, e estatísticas gerais,
Para que eu tenha visão geral do estado do pipeline (FR31).

**Acceptance Criteria:**

**Given** que o dashboard está rodando
**When** acesso a página Overview em src/construtor/dashboard/pages/overview.py
**Then** exibe header: "Visão Geral do Pipeline"
**And** exibe métricas principais em 4 colunas: Total Geradas, Aprovadas, Rejeitadas, Failed
**And** cada métrica mostra número absoluto e percentual (ex: "6.543 aprovadas (85%)")
**And** exibe barra de progresso: "Foco X de Y (Z%)"
**And** exibe tempo decorrido e tempo estimado restante
**And** exibe custo acumulado total em USD (calculado das métricas)
**And** exibe gráfico de linha: "Questões Aprovadas por Foco" (eixo X: foco, eixo Y: count)
**And** exibe gráfico de pizza: "Distribuição de Status" (aprovadas/rejeitadas/failed)
**And** exibe tabela de últimas 10 questões processadas com: ID, Foco, Status, Modelo, Custo, Rodadas
**And** dados são lidos do SQLite (tabelas questions, metrics, batch_state)
**And** se pipeline não está rodando, exibe banner: "Pipeline pausado/concluído"
**And** botão "Atualizar Dados" força reload manual

### Story 4.3: Implementar Página de Métricas em Tempo Real

Como Rodrigo,
Eu quero visualizar taxa de aprovação, custo acumulado, concordância e latência em tempo real,
Para que eu possa monitorar qualidade e performance do pipeline (FR27, FR28, FR29, NFR21, NFR24).

**Acceptance Criteria:**

**Given** que o dashboard está rodando
**When** acesso a página Métricas em src/construtor/dashboard/pages/metrics.py
**Then** exibe header: "Métricas em Tempo Real"
**And** exibe 4 KPIs principais:
  - Taxa de Aprovação 1ª Rodada: X% (meta: ≥85%) com indicador verde/vermelho
  - Custo Acumulado: $X.XX USD
  - Taxa de Concordância Comentador: Y% (concordância gabarito vs resposta_declarada)
  - Latência Média por Questão: Z segundos
**And** exibe gráfico de linha: "Taxa de Aprovação ao Longo do Tempo" (eixo X: timestamp, eixo Y: taxa %)
**And** exibe gráfico de linha: "Custo Acumulado" (eixo X: número de questões, eixo Y: custo USD)
**And** exibe gráfico de barra: "Custo por Modelo LLM" (compara custo médio por questão entre OpenAI/Anthropic)
**And** exibe gráfico de linha: "Latência Média por Agente" (3 linhas: Criador, Comentador, Validador)
**And** exibe projeção de custo total: "Custo estimado para X questões restantes: $Y.YY" (NFR24)
**And** todos os dados vêm das tabelas metrics e questions do SQLite
**And** métricas atualizam automaticamente a cada 5 segundos

### Story 4.4: Implementar Página de Comparativo de Modelos

Como Rodrigo,
Eu quero comparar qualidade, custo e velocidade entre modelos de LLM testados,
Para que eu possa tomar decisão informada sobre qual modelo usar (FR30, NFR22).

**Acceptance Criteria:**

**Given** que o dashboard está rodando e há questões geradas por múltiplos modelos
**When** acesso a página Comparativo de Modelos em src/construtor/dashboard/pages/model_comparison.py
**Then** exibe header: "Comparativo entre Modelos LLM"
**And** exibe tabela comparativa com colunas: Modelo, Questões Geradas, Taxa Aprovação, Custo Médio/Questão, Latência Média, Taxa Concordância
**And** cada linha representa um modelo testado (ex: gpt-4o, claude-sonnet-4.5)
**And** colunas têm formatação: Taxa % em verde/amarelo/vermelho, Custo em USD, Latência em segundos
**And** destaca em negrito o modelo com melhor relação qualidade/custo
**And** exibe gráfico scatter: eixo X = Custo Médio, eixo Y = Taxa Aprovação (cada ponto = modelo)
**And** exibe gráfico de barras agrupadas: "Latência por Agente e Modelo" (3 barras por modelo: Criador, Comentador, Validador)
**And** exibe seção "Recomendação": análise automática do melhor modelo baseado em qualidade ≥85% e menor custo
**And** dados vêm da agregação de metrics e questions agrupados por modelo_llm
**And** botão "Exportar Comparativo CSV" baixa tabela comparativa

### Story 4.5: Implementar Página de Checkpoint View

Como Rodrigo,
Eu quero visualizar checkpoints com amostras de questões para validação humana,
Para que eu possa aprovar/rejeitar qualidade antes de continuar (FR16, FR18).

**Acceptance Criteria:**

**Given** que o dashboard está rodando e há checkpoints salvos
**When** acesso a página Checkpoint View em src/construtor/dashboard/pages/checkpoint_view.py
**Then** exibe header: "Checkpoints de Validação"
**And** exibe lista de checkpoints com: ID, Foco Range, Data/Hora, Status (pending/approved/rejected), Taxa Aprovação do Bloco
**And** checkpoints pendentes aparecem destacados no topo
**And** ao clicar em um checkpoint, expande detalhes:
  - Estatísticas do bloco: total geradas, aprovadas, rejeitadas, failed, custo
  - Amostra de 5 questões aprovadas (full display: enunciado, 4 alternativas, resposta correta, comentário completo)
**And** cada questão da amostra exibe em formato legível: seções do comentário colapsáveis/expansíveis
**And** se checkpoint está pending, exibe botões: [Aprovar e Continuar] [Rejeitar e Ajustar]
**And** ao clicar [Rejeitar e Ajustar], redireciona para Sidebar de Configuração
**And** após aprovação, status muda para "approved" e timestamp é registrado
**And** dados vêm das tabelas checkpoints e questions (join por sample_question_ids)
**And** filtro permite visualizar: Todos, Pendentes, Aprovados, Rejeitados

### Story 4.6: Implementar Página de Log de Incidentes

Como Rodrigo,
Eu quero ver log de incidentes separando erros pontuais de sistêmicos,
Para que eu possa identificar problemas e agir rapidamente (FR32, FR17).

**Acceptance Criteria:**

**Given** que o dashboard está rodando e há questões failed
**When** acesso a página Log de Incidentes em src/construtor/dashboard/pages/incidents.py
**Then** exibe header: "Log de Incidentes"
**And** exibe 2 tabs: "Erros Pontuais" e "Erros Sistêmicos"
**And** tab "Erros Pontuais" mostra tabela: Question ID, Foco, Categorias de Erro (checkboxes: enunciado_ambiguo, distratores_fracos, etc.), Rodadas Tentadas, Timestamp
**And** tab "Erros Sistêmicos" mostra alertas críticos: Data/Hora, Categoria Predominante, Número de Falhas, Focos Afetados, Ação Tomada (ajustado/ignorado/reprocessado)
**And** cada incidente sistêmico exibe análise: "3+ questões falharam por [categoria] nos focos X-Y"
**And** filtros disponíveis: Data, Categoria de Erro, Foco
**And** exibe gráfico de barras: "Erros por Categoria" (conta ocorrências de cada tipo de erro)
**And** exibe timeline: "Incidentes Sistêmicos ao Longo do Tempo"
**And** dados vêm de questions com status='failed' e tabela incidents (se existir)
**And** botão "Exportar Incidentes CSV" baixa log completo
**And** erros pontuais destacados em amarelo, sistêmicos em vermelho

### Story 4.7: Implementar Sidebar de Configuração

Como Rodrigo,
Eu quero configurar modelo LLM, temperatura, retries, batch size e editar prompts via interface,
Para que eu possa ajustar parâmetros sem tocar no código (FR33, FR34, FR35, FR36, FR37).

**Acceptance Criteria:**

**Given** que o dashboard está rodando
**When** abro o sidebar de configuração em src/construtor/dashboard/components/sidebar.py
**Then** exibe seção "Configuração do Pipeline"
**And** exibe selectbox: "Modelo LLM" com opções: gpt-4o, gpt-4o-mini, claude-sonnet-4.5, claude-haiku-4.5 (FR33)
**And** exibe slider: "Temperatura" de 0.0 a 1.0 com step 0.1, default 0.7 (FR34)
**And** exibe number input: "Limite de Retries" de 1 a 5, default 3 (FR35)
**And** exibe number input: "Batch Size (sub-focos por foco)" de 10 a 100, default 50 (FR36)
**And** exibe number input: "Intervalo de Checkpoints (focos)" de 5 a 20, default 10 (FR36)
**And** exibe number input: "Concorrência (Semaphore)" de 1 a 10, default 5
**And** exibe seção "Editar Prompts": (FR37)
  - Selectbox para escolher: Criador, Comentador, Validador, SubFocoGenerator
  - Text area com conteúdo do prompt carregado de prompts/[agente].md
  - Botão "Salvar Prompt" atualiza o arquivo .md
**And** todas as configurações são salvas em PipelineConfig ao clicar "Aplicar Configurações"
**And** mudanças de config só aplicam no próximo batch (não afetam processamento em andamento)
**And** exibe warning: "Configurações serão aplicadas no próximo batch"
**And** logs estruturados registram INFO quando configuração é alterada com valores antigos e novos
