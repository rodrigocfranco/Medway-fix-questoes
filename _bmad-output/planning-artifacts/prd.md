---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
inputDocuments: ['_bmad-output/brainstorming/brainstorming-session-2026-02-06.md']
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 1
  projectDocs: 0
workflowType: 'prd'
classification:
  projectType: 'developer_tool_data_pipeline'
  domain: 'edtech_healthcare'
  complexity: 'medium'
  projectContext: 'greenfield'
---

# Product Requirements Document — Construtor de Questões

**Autor:** Rodrigo Franco
**Data:** 2026-02-07

## Resumo Executivo

### Visão do Produto

O Construtor de Questões é um pipeline multi-agente em Python que gera em massa questões médicas de alta qualidade para alunos de 1º ao 4º ano de medicina no Brasil. O sistema recebe um Excel estruturado com temas e focos, processa cada item através de três agentes de IA com papéis distintos (Criador, Comentador cego, Validador árbitro), e produz um Excel final com questões completas, comentários pedagógicos estruturados e referências bibliográficas verificáveis.

### Diferencial

Quatro inovações distinguem este sistema de geradores de conteúdo educacional convencionais:

1. **Revisão Cega Multi-Agente** — O Comentador analisa a questão sem conhecer o gabarito e declara sua própria resposta. Discordância = sinal de questão ambígua ou gabarito errado. Transforma o pipeline de "geração + checagem" em "geração + teste real + arbitragem".
2. **Checkpoint Híbrido** — Diferencia erro pontual (refaz questão) de erro sistêmico (3+ falhas → ajusta parâmetro + refaz lote). Evita tanto parar tudo quanto ignorar falhas.
3. **Sorteio Prévio da Alternativa Correta** — Posição (A/B/C/D) sorteada com balanceamento estatístico ANTES da geração. Elimina viés de construção.
4. **Arquitetura de Governança** — Três agentes com separação de responsabilidades, feedback estruturado por categorias de erro e limite de rodadas. Checks and balances, não cadeia sequencial.

### Público-Alvo

Rodrigo Franco — produtor de conteúdo educacional médico. Único usuário do sistema. O Excel final é entregue a uma equipe separada para importação na plataforma de ensino.

### Escopo

Pipeline de geração + Excel de saída + painel de métricas (Streamlit). A plataforma onde alunos consomem as questões está fora do escopo.

## Critérios de Sucesso

### Sucesso do Usuário

- Excel final com questões bem estruturadas, enunciados precisos, alternativas coerentes ao nível de dificuldade
- Comentários completos em todas as questões (Introdução → Visão Específica → Alternativa por alternativa → Visão do Aprovado)
- Referências bibliográficas 100% reais e verificáveis
- Painel de métricas funcional para avaliar qualidade, custo, concordância e comparar modelos de LLM
- Controle via checkpoints a cada 10 focos com amostra para validação humana
- Ajuste de parâmetros do pipeline com base nos dados do painel

### Sucesso do Negócio

- ~8.000 questões geradas e validadas até **14 de fevereiro de 2026**
- Excel estruturado pronto para entrega à equipe de importação
- Cobertura completa dos temas e focos da planilha de input (1º ao 4º ano)
- Balanceamento estatístico: posição da correta (A/B/C/D), níveis de dificuldade (Bloom), tipos de enunciado
- Custo de produção otimizado — melhor relação qualidade/custo entre modelos testados

### Sucesso Técnico

- Taxa de aprovação do Validador ≥ 85% na primeira rodada
- Pipeline multi-agente estável com retry automático (máximo 2-3 rodadas)
- Checkpoint híbrido funcional (pontual vs sistêmico)
- Máxima qualidade com menor custo possível
- Painel de métricas: latência, custo em tokens, taxa de aprovação, concordância, comparativo entre modelos

### Resultados Mensuráveis

| Métrica | Target |
|---------|--------|
| Questões geradas | ~8.000 |
| Taxa aprovação 1ª rodada | ≥ 85% |
| Referências bibliográficas falsas | 0% |
| Comentários completos | 100% |
| Prazo final | 14/02/2026 |
| Balanceamento posição correta | ~25% cada (A/B/C/D) |
| Cobertura de focos do input | 100% |

## Escopo do Produto e Roadmap

### Estratégia MVP

**Abordagem:** Problem-solving MVP — o menor sistema funcional que gera questões de qualidade validada em escala, com rastreamento de custos desde o dia 1.

**Princípio:** Pipeline primeiro, interface depois. Métricas/custos capturados desde a primeira questão (log + CSV), migrando para Streamlit quando pronto.

**Recursos:** 1 desenvolvedor + Rodrigo (validação nos checkpoints). Stack Python, sem dependências pesadas.

### Phase 1: MVP — Deadline: 14/02/2026

**Bloco 1: Core Pipeline (Dias 1-3)**

- Pipeline Criador → Comentador (cego) → Validador funcional
- Leitura do Excel de input (temas/focos/períodos)
- Escrita do Excel de output com todas as 26 colunas
- Integração Pinecone RAG no Comentador (área "assistant")
- Sorteio prévio balanceado da alternativa correta
- Lógica de retry com feedback estruturado (max 2-3 rodadas)
- Log estruturado por questão: modelo, tokens, custo, rodadas, tempo, decisão
- Métricas em CSV/log desde a primeira execução

**Bloco 2: Calibração (Dias 3-4)**

- Geração de 30 questões de focos diversos como lote de teste
- Métricas acessíveis (CSV ou terminal): aprovação, concordância, custo
- Teste comparativo com 2-3 modelos (GPT-4o, Claude, Gemini)
- Iteração de prompts com base nos resultados
- Decisão de modelo baseada em dados concretos

**Bloco 3: Escala + Dashboard (Dias 4-7)**

- Batch automático processando todos os focos
- Checkpoints a cada 10 focos com amostra de 5 questões
- Checkpoint híbrido (erro pontual vs sistêmico)
- Persistência de progresso parcial (recuperação em caso de falha)
- Streamlit dashboard: configuração, métricas, comparativo, checkpoint view, log de incidentes

### Phase 2: Growth (Pós-MVP)

- Flashcards extraídos da Visão do Aprovado (~16.000-32.000 cards em planilha separada)
- Material de revisão por tema (agente sintetizador)
- Banco de questões polêmicas (discordâncias entre agentes como material didático)
- Teste A/B automático (2 versões por questão, Validador escolhe)

### Phase 3: Expansão (Futuro)

- Temperatura criativa crescente para diversidade máxima
- Inversão Comentador-primeiro (experimento)
- Expansão para residência/especialização
- Pipeline reutilizável para outras disciplinas

## Jornadas do Usuário

### Jornada 1: Do Input ao Excel Final (Caminho de Sucesso)

**Quem é:** Rodrigo Franco, produtor de conteúdo educacional médico. Precisa entregar ~8.000 questões de alta qualidade para alunos de 1º ao 4º ano de medicina até 14/02/2026. Gerar isso manualmente seria impossível na escala e no prazo.

**Opening Scene:** Rodrigo tem uma planilha Excel com temas e focos organizados por período (1º-4º ano). Abre o sistema, configura os parâmetros iniciais e sobe o Excel de input.

**Rising Action:** O pipeline entra em calibração — gera 30 questões de focos diversos. Rodrigo abre o painel de métricas: taxa de aprovação, custo por questão, concordância entre agentes, comparativo de modelos. Analisa, ajusta prompts, itera. Os números melhoram. Escolhe o modelo com melhor relação qualidade/custo.

**Climax:** Calibração aprovada — taxa acima de 85%, comentários completos, referências reais. Rodrigo dispara a produção em massa. Pipeline roda autonomamente. A cada 10 focos, checkpoint: amostra 5 questões, valida qualidade. Painel mostra progresso em tempo real.

**Resolution:** Pipeline conclui. Excel final com milhares de questões estruturadas, comentários completos, referências verificáveis, balanceamento correto. Entrega para a equipe de importação. Missão cumprida.

### Jornada 2: Quando o Pipeline Tropeça (Recuperação)

**Opening Scene:** Durante produção em massa, um checkpoint revela taxa de aprovação de 60% num bloco de farmacologia comparativa. Distratores fracos e comentários superficiais.

**Rising Action:** Rodrigo consulta o painel. Erro **sistêmico** (3+ falhas no mesmo padrão). O checkpoint híbrido sinaliza o tipo de erro. Rodrigo analisa as amostras e entende que o tema exige mais contexto.

**Climax:** Ajusta parâmetros para este bloco temático — refina prompt, adiciona contexto. Sistema refaz o lote com novos parâmetros.

**Resolution:** Lote reprocessado volta acima de 85%. Painel registra incidente, ajuste e resultado. Produção retoma normalmente. Excel final sem resquícios do tropeço.

### Mapeamento Jornadas → Capacidades

| Capacidade | Origem |
|------------|--------|
| Upload de Excel de input | Jornada 1 — Setup |
| Configuração de parâmetros | Jornada 1 — Setup |
| Geração de lote de teste (calibração) | Jornada 1 — Calibração |
| Painel de métricas | Jornada 1 & 2 — Monitoramento |
| Comparativo entre modelos de LLM | Jornada 1 — Calibração |
| Ajuste de parâmetros/prompts | Jornada 1 & 2 — Iteração |
| Produção em massa batch | Jornada 1 — Produção |
| Checkpoints com amostragem | Jornada 1 & 2 — Validação |
| Checkpoint híbrido | Jornada 2 — Recuperação |
| Reprocessamento de lote | Jornada 2 — Recuperação |
| Excel estruturado de output | Jornada 1 — Entrega |
| Log de decisões e incidentes | Jornada 2 — Rastreabilidade |

## Requisitos de Domínio

### Precisão de Conteúdo Médico

- Toda informação médica deve ser factualmente correta e atualizada
- Condutas clínicas seguem protocolos brasileiros vigentes (MS, SUS, sociedades médicas) — nunca protocolos internacionais que conflitem com a prática no Brasil
- Ciclo básico (1º-2º ano): literatura consagrada (Guyton, Junqueira, Robbins, Netter)
- Ciclo clínico (3º-4º ano): protocolos brasileiros + literatura clássica (Harrison, Cecil)
- Filtro de relevância clínica: evitar ultraespecificidades sem valor para o aluno

### Referências Bibliográficas

- Regra inviolável: NUNCA gerar referências inexistentes
- RAG com documentos curados como fonte primária para o Comentador
- Lista de fontes permitidas por período/tema para restringir o espaço de referências
- Cada questão com referência verificável na coluna correspondente do Excel

### Contexto Educacional Brasileiro

- Calibração de dificuldade por período: 1º-2º ano (ciclo básico) vs 3º-4º ano (ciclo clínico)
- Taxonomia de Bloom aplicada aos 3 níveis de dificuldade
- Conteúdo alinhado à realidade do SUS e da prática médica brasileira
- Terminologia médica em português brasileiro

### Mitigação de Riscos da IA

- Pipeline multi-agente com revisão cega como controle primário de qualidade
- Checkpoint híbrido para detectar erros sistêmicos antes da propagação
- Controle de duplicidade via objetivo educacional por questão
- Temperatura criativa gerenciada para evitar repetição sem sacrificar qualidade
- Distratores refletem erros cognitivos reais de alunos, não alternativas absurdas
- Monitoramento contínuo via painel de métricas para detectar degradação

## Inovação e Padrões Inéditos

### Áreas de Inovação

**1. Revisão Cega Multi-Agente** — Comentador analisa sem conhecer o gabarito e declara sua resposta. Discordância = questão ambígua ou gabarito errado. Pipeline transformado em "geração + teste real + arbitragem".

**2. Checkpoint Híbrido** — Erro pontual (refaz questão) vs sistêmico (3+ falhas → ajusta parâmetro + refaz lote). Nem paranoia nem negligência.

**3. Sorteio Prévio da Alternativa Correta** — Posição (A/B/C/D) sorteada com balanceamento ANTES da geração. Elimina viés de construção.

**4. Arquitetura de Governança** — Três agentes com separação de responsabilidades, feedback por categorias de erro, limite de rodadas. Checks and balances.

### Abordagem de Validação

- Validação natural durante calibração (30 questões de focos diversos)
- Painel de métricas comprova eficácia: concordância, aprovação, categorias de erro
- Dados do pipeline falam por si — sem validação especial necessária

## Requisitos Técnicos do Pipeline

### Visão Geral

Pipeline de processamento batch multi-agente em Python. Input: Excel com temas/focos. Output: Excel com questões completas, comentários e metadados. Interface: dashboard Streamlit para configuração, monitoramento e métricas.

### Stack Tecnológica

| Componente | Tecnologia | Justificativa |
|------------|-----------|---------------|
| Linguagem | Python 3.11+ | Ecossistema dominante para IA/dados |
| LLM Orchestration | SDKs diretos (openai, anthropic, google-generativeai) | Máximo controle, debugging simples, sem overhead de framework |
| Excel I/O | pandas + openpyxl | Padrão da indústria, leitura/escrita robusta |
| RAG | Pinecone (Assistants API) | Infraestrutura já existente com documentos médicos curados |
| Dashboard | Streamlit | User-friendly, rápido de construir, ideal para dashboards de dados |
| Configuração | Streamlit sidebar | Controles visuais integrados ao painel |

### Arquitetura Multi-Agente

```
Excel Input → Gerador de Sub-focos (batch de 50)
    ↓
Para cada sub-foco:
    ↓
Agente Criador (SDK direto) → Questão + Gabarito
    ↓
Agente Comentador (SDK direto + Pinecone RAG) → Comentário cego + Resposta declarada
    ↓
Agente Validador (SDK direto) → Aprovação ou Feedback estruturado
    ↓                                          ↓
  Aprovada → Excel Output              Rejeitada → Retry (max 2-3x)
                                               ↓
                                        Sem aprovação → Fila revisão humana
```

### Modelo de Dados — Excel de Output

| Coluna | Descrição |
|--------|-----------|
| tema | Tema principal da questão |
| foco | Foco dentro do tema |
| sub_foco | Sub-foco gerado pela IA ou definido manualmente |
| periodo | Período alvo (1º-4º ano) |
| nivel_dificuldade | Nível 1/2/3 (Taxonomia de Bloom) |
| tipo_enunciado | Tipo de enunciado (conceitual, caso clínico, etc.) |
| enunciado | Texto completo do enunciado |
| alternativa_a | Texto da alternativa A |
| alternativa_b | Texto da alternativa B |
| alternativa_c | Texto da alternativa C |
| alternativa_d | Texto da alternativa D |
| resposta_correta | Letra da alternativa correta (A/B/C/D) |
| objetivo_educacional | Objetivo educacional (controle de duplicidade) |
| comentario_introducao | Introdução do comentário |
| comentario_visao_especifica | Visão específica do comentário |
| comentario_alt_a | Comentário sobre alternativa A |
| comentario_alt_b | Comentário sobre alternativa B |
| comentario_alt_c | Comentário sobre alternativa C |
| comentario_alt_d | Comentário sobre alternativa D |
| comentario_visao_aprovado | Visão do Aprovado |
| referencia_bibliografica | Referência bibliográfica verificável |
| suporte_imagem | Placeholder para imagem (se aplicável) |
| fonte_imagem | Fonte/URL da imagem (se aplicável) |
| modelo_llm | Modelo utilizado na geração |
| rodadas_validacao | Número de rodadas até aprovação |
| concordancia_comentador | Comentador concordou com gabarito (sim/não) |

### Integração Pinecone RAG

- Conexão via Pinecone API à área "assistant" existente
- Documentos médicos curados já disponíveis
- Comentador consulta Pinecone para embasar comentários e referências
- Query por tema + foco para recuperar contexto relevante
- Fontes retornadas alimentam a coluna referencia_bibliografica

### Dashboard Streamlit

- **Sidebar de configuração:** Modelo LLM, temperatura, limite de retries, tamanho do batch, intervalo de checkpoints
- **Visão geral:** Progresso total, questões aprovadas/rejeitadas/pendentes
- **Métricas em tempo real:** Taxa de aprovação, custo acumulado, latência média, concordância
- **Comparativo de modelos:** Qualidade, custo e velocidade entre modelos testados
- **Checkpoint view:** Amostra de questões para validação humana
- **Log de incidentes:** Erros pontuais e sistêmicos com ações tomadas

### Considerações de Implementação

- **Batch processing:** Processamento assíncrono com asyncio para paralelizar chamadas API
- **Rate limiting:** Respeitar limites das APIs com backoff exponencial
- **Persistência:** Progresso parcial salvo a cada batch para recuperação em falha
- **Logging:** Log estruturado por questão (modelo, tokens, rodadas, tempo, decisão)
- **Error handling:** Categorização de erros (API timeout, rate limit, parsing, qualidade) com tratamento específico

## Requisitos Funcionais

### 1. Gestão de Input

- **FR1:** Rodrigo pode importar Excel de input contendo temas, focos e períodos
- **FR2:** O sistema valida a estrutura do Excel de input e reporta erros antes do processamento
- **FR3:** Rodrigo pode definir se sub-focos são gerados pela IA ou fornecidos manualmente

### 2. Pipeline de Geração de Questões

- **FR4:** O sistema gera sub-focos em bloco (batch de 50) a partir de um foco
- **FR5:** O Agente Criador gera questão completa (enunciado + 4 alternativas + gabarito + objetivo educacional)
- **FR6:** O sistema sorteia a posição da alternativa correta (A/B/C/D) com balanceamento estatístico antes da geração
- **FR7:** O Agente Criador seleciona automaticamente o tipo de enunciado adequado ao tema, foco e nível
- **FR8:** O sistema aplica 3 níveis de dificuldade mapeados à Taxonomia de Bloom
- **FR9:** O sistema constrói distratores por natureza cognitiva do nível de dificuldade

### 3. Qualidade e Validação

- **FR10:** O Agente Comentador analisa a questão sem conhecer o gabarito e declara qual alternativa considera correta
- **FR11:** O Agente Comentador gera comentário estruturado completo (Introdução → Visão Específica → Alt. por Alt. → Visão do Aprovado)
- **FR12:** O Agente Validador compara gabarito do Criador com resposta do Comentador e emite aprovação ou rejeição
- **FR13:** O Agente Validador fornece feedback por categorias de erro (enunciado ambíguo, distratores fracos, gabarito questionável, comentário incompleto, fora do nível)
- **FR14:** O sistema reenvia questões rejeitadas ao Criador com feedback do Validador (max 2-3 rodadas)
- **FR15:** O sistema encaminha questões sem aprovação após o limite para fila de revisão humana
- **FR16:** O sistema executa checkpoints a cada 10 focos, com amostra de 5 questões para validação humana
- **FR17:** O sistema diferencia erro pontual de erro sistêmico (3+) e aplica ação corretiva adequada
- **FR18:** Rodrigo pode aprovar ou rejeitar checkpoint e ajustar parâmetros antes de reprocessar o lote

### 4. RAG e Referências Bibliográficas

- **FR19:** O Agente Comentador consulta documentos médicos curados no Pinecone (área "assistant")
- **FR20:** O sistema restringe referências a fontes permitidas por período/tema
- **FR21:** O sistema associa referência bibliográfica verificável a cada questão
- **FR22:** O sistema filtra questões com relevância clínica insuficiente ou ultraespecificidades

### 5. Output e Exportação

- **FR23:** O sistema gera Excel de output com todas as 26 colunas do modelo de dados
- **FR24:** O sistema salva progresso parcial para recuperação em caso de falha
- **FR25:** O sistema exporta Excel final pronto para entrega à equipe de importação

### 6. Métricas e Monitoramento

- **FR26:** O sistema registra métricas por questão: modelo, tokens, custo, rodadas, tempo, decisão
- **FR27:** Rodrigo visualiza taxa de aprovação em tempo real
- **FR28:** Rodrigo visualiza custo acumulado em tokens
- **FR29:** Rodrigo visualiza taxa de concordância Comentador vs gabarito
- **FR30:** Rodrigo compara qualidade, custo e velocidade entre modelos de LLM
- **FR31:** Rodrigo visualiza progresso total (geradas/total, aprovadas/rejeitadas/pendentes)
- **FR32:** O sistema registra log de incidentes (erros pontuais e sistêmicos)

### 7. Configuração e Controle

- **FR33:** Rodrigo seleciona modelo de LLM
- **FR34:** Rodrigo ajusta temperatura de geração
- **FR35:** Rodrigo define limite de rodadas de retry
- **FR36:** Rodrigo define tamanho do batch e intervalo de checkpoints
- **FR37:** Rodrigo ajusta prompts dos agentes (Criador, Comentador, Validador)
- **FR38:** Rodrigo pode iniciar, pausar e retomar processamento em massa

## Requisitos Não-Funcionais

### Performance

- **NFR1:** Latência média por questão completa (3 agentes) monitorada e otimizada para viabilizar ~8.000 questões no prazo
- **NFR2:** Processamento batch suporta execução contínua por horas sem degradação ou memory leaks
- **NFR3:** Chamadas paralelas (asyncio) respeitam rate limits com backoff exponencial
- **NFR4:** Escrita do Excel não bloqueia o pipeline — salvamentos parciais rápidos

### Segurança

- **NFR5:** API keys armazenadas em variáveis de ambiente ou .env, nunca hardcoded
- **NFR6:** Credenciais nunca commitadas em repositório
- **NFR7:** Acesso ao Pinecone via autenticação segura por API key

### Integração

- **NFR8:** Fallback gracioso quando API de LLM indisponível — modelo alternativo ou pausa
- **NFR9:** Consultas Pinecone com timeout configurável e fallback para geração sem RAG (questão flagada)
- **NFR10:** Parsing robusto com validação de estrutura para mudanças de formato das APIs

### Resiliência

- **NFR11:** Estado de progresso salvo a cada batch — retomada exata do ponto de parada
- **NFR12:** Crash não corrompe Excel parcial — escrita atômica ou arquivo temporário
- **NFR13:** Erros logados com contexto (questão, foco, modelo, rodada) para diagnóstico
- **NFR14:** Falha em questão individual não interrompe batch inteiro

### Qualidade de Conteúdo

- **NFR15:** Taxa de aprovação ≥ 85% na primeira rodada (conforme Critérios de Sucesso)
- **NFR16:** 100% das questões aprovadas com comentário estruturado completo (5 seções)
- **NFR17:** 0% de referências bibliográficas inexistentes
- **NFR18:** Balanceamento da posição correta entre 20-30% para cada letra (A/B/C/D)
- **NFR19:** Cada alternativa errada com justificativa educacional no comentário
- **NFR20:** Terminologia médica em português brasileiro, contexto SUS

### Eficiência de Custo

- **NFR21:** Custo por questão aprovada registrado e monitorável
- **NFR22:** Comparação custo-benefício entre modelos antes da produção em massa
- **NFR23:** Custo incremental de retries rastreado separadamente
- **NFR24:** Dashboard exibe projeção de custo total (custo médio × questões restantes)

## Mitigação de Riscos

### Riscos Técnicos

- *Pipeline não atinge 85% de aprovação:* Calibração com 30 questões existe para iterar e ajustar antes de escalar
- *Pinecone não retorna contexto relevante:* Fallback para geração sem RAG + flag para revisão humana da referência
- *Rate limiting das APIs:* Backoff exponencial + throttling controlado
- *Revisão cega com muita discordância (>15%):* Indica problema nos prompts — ajustar e recalibrar
- *Checkpoint híbrido não diferencia bem:* Fallback para revisão manual do lote completo
- *Sorteio prévio cria viés no prompt:* Ajustar instrução para que posição não influencie construção

### Riscos de Prazo

- *Dashboard não pronto a tempo:* Não bloqueante — pipeline roda com métricas em CSV/log
- *Calibração demora mais que o previsto:* Começar com 1 modelo, expandir comparativo se sobrar tempo
- *Escopo creep:* Growth features proibidas até Excel de 8.000 questões entregue

### Riscos de Custo

- *Custo de tokens explode:* Métricas desde o dia 1 permitem detectar e ajustar antes da produção em massa
- *Modelo caro mas melhor:* Dados do comparativo permitem decisão informada — qualidade máxima com menor custo, não menor custo absoluto
