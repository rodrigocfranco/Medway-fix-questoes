---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: []
session_topic: 'Sistema de geração em massa de questões médicas de alta qualidade para alunos do 1º ao 4º ano de medicina'
session_goals: 'Design do produto/sistema + Lógica de IA/prompts para gerar ~8.000 questões com qualidade máxima e fricção mínima'
selected_approach: 'ai-recommended'
techniques_used: ['Question Storming', 'Morphological Analysis', 'SCAMPER Method']
ideas_generated: ['125+']
session_active: false
workflow_completed: true
context_file: ''
---

# Brainstorming Session Results

**Facilitator:** Rodrigo Franco
**Date:** 2026-02-06

## Session Overview

**Topic:** Sistema de geração em massa de questões médicas de alta qualidade (1º-4º ano de medicina)
**Goals:** Design completo do sistema + Lógica de IA/prompts — ~8.000 questões, qualidade máxima, fricção mínima

### Session Setup

- **Escala:** ~8.000 questões — exige pipeline automatizado
- **Fluxo:** Tema → Foco → Sub-foco (IA ou usuário) → Questão completa → Excel
- **Estrutura da questão:** Enunciado + 4 alternativas (A-D) + Comentários (Introdução → Visão Específica → Alternativa por alternativa → Visão do Aprovado)
- **Princípio:** Qualidade máxima, fricção mínima, geração em massa
- **Escopo:** Design do sistema + Engenharia de prompts

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** Geração em massa de questões médicas com foco em design do sistema + lógica de IA

**Recommended Techniques:**

- **Question Storming:** Definir o espaço do problema — questionar profundamente antes de construir
- **Morphological Analysis:** Mapear sistematicamente TODOS os parâmetros do sistema de geração
- **SCAMPER Method:** Otimizar o pipeline com 7 lentes de inovação sistemática

**AI Rationale:** Sequência de dentro para fora — do problema fundamental → ao mapa completo → ao pipeline otimizado. Técnicas profundas e estruturadas para um projeto de alta complexidade e escala massiva.

## Technique Execution Results

### Question Storming (Fase 1 — Definição do Espaço do Problema)

**Perguntas Geradas:** ~80+
**Dimensões Exploradas:** Pedagogia, Mente da IA, Escala, Estrutura de Dados, Fluxo do Usuário, Arquitetura Técnica

**Insights-Chave:**

1. **Sistema de aprendizagem, não apenas gerador** — O sistema é potencialmente um sistema de aprendizagem estruturada, não apenas um gerador de questões
2. **Tensão pedagógica** — Rigor pedagógico vs. utilidade percebida pelo aluno é uma tensão central a resolver
3. **Input já estruturado** — Planilha Excel com temas/focos já existe, mudando a arquitetura para pipeline batch
4. **Controle de duplicidade** — Rastrear "objetivo educacional" por questão é o desafio técnico mais crítico para evitar repetição em 8.000 questões
5. **Ordem de geração invertida** — Sortear alternativa correta ANTES de gerar a questão é uma decisão de design fundamental
6. **Taxonomia progressiva** — Possibilidade de 3 níveis de dificuldade mapeados à taxonomia de Bloom, com debate sobre apresentação progressiva vs. misturada
7. **Filtro de relevância** — A IA precisa de um mecanismo para evitar questões ultraespecíficas sem valor clínico
8. **Comentários como ferramenta de ensino** — O comentário estruturado (Introdução → Visão Específica → Alternativa por alternativa → Visão do Aprovado) é tão importante quanto a questão
9. **Qualidade dos distratores** — Alternativas erradas devem refletir erros reais que alunos cometem
10. **Escala com memória** — Pipeline precisa de mecanismo de memória/registro para garantir diversidade nas 8.000 questões

### Morphological Analysis (Fase 2 — Mapeamento Sistemático de Parâmetros)

**Matriz Final de 11 Dimensões:**

| # | Parâmetro | Opções/Definição |
|---|-----------|-----------------|
| 1 | Nível de Dificuldade | Nível 1 (Lembrar/Compreender), Nível 2 (Aplicar/Analisar), Nível 3 (Avaliar/Criar) — Taxonomia de Bloom |
| 2 | Tipo de Enunciado | Conceitual direto · Caso clínico · Baseado em imagem (placeholder + referência) · Conduta (próximo passo) · Diagnóstico mais provável · Mecanismo/fisiopatologia · Epidemiologia/bioestatística · Farmacologia comparativa |
| 3 | Origem do Sub-foco | IA gera automaticamente · Usuário define manualmente |
| 4 | Posição da Correta | A/B/C/D (sorteio prévio balanceado) — sorteada ANTES da geração |
| 5 | Lógica dos Distratores | Por natureza cognitiva: N1 (confusão básica/terminológica) · N2 (conceito certo aplicado ao contexto errado) · N3 (julgamento entre opções válidas, "duas parecem certas") |
| 6 | Comentário | Sempre completo: Introdução → Visão Específica → Alt. por Alt. → Visão do Aprovado |
| 7 | Período-Alvo | 1º-4º ano medicina (Brasil) |
| 8 | Referência Bibliográfica | Ciclo básico: livros-texto clássicos (Guyton, Junqueira, Robbins, Netter) · Ciclo clínico: protocolos brasileiros (MS, SUS, sociedades médicas) + literatura clássica |
| 9 | Pipeline Multi-Agente | Agente Criador (gera questão + gabarito) → Agente Comentador (comenta SEM saber a correta, declara sua resposta) → Agente Validador (compara gabarito vs comentário, aprova ou devolve com feedback) |
| 10 | Painel de Métricas | Latência por questão, custo tokens, taxa aprovação, taxa concordância, comparativo entre modelos |
| 11 | Suporte a Imagens | Placeholder no enunciado + coluna URL/HTML + fonte da imagem + indicação para professor inserir |

**Arquitetura Multi-Agente Definida:**

```
Agente Criador → Agente Comentador (revisão cega) → Agente Validador (árbitro)
     ↑                                                        │
     └──────── feedback de correção (se discordância) ◄────────┘
```

- Comentador funciona como "aluno expert fazendo prova às cegas"
- Se comentário aponta para resposta diferente do gabarito → questão ambígua ou gabarito errado
- Validador devolve com feedback estruturado por categorias; após 2-3 rodadas sem aprovação → revisão humana

**Métricas de Teste Inicial:**
- Rodar primeiras 50 questões em múltiplos modelos (GPT-4o, Claude, Gemini)
- Comparar: qualidade, custo, concordância do validador, latência
- Decisão de modelo baseada em dados concretos

### SCAMPER Method (Fase 3 — Otimização do Pipeline)

**Decisões por Lente:**

| Lente | Decisão |
|-------|---------|
| **S — Substitute** | Geração em blocos temáticos (50 sub-focos primeiro, depois questões). Exemplos de estrutura/tom no prompt, nunca de conteúdo — evita repetitividade. |
| **C — Combine** | Sub-foco + objetivo educacional + nível Bloom gerados juntos num único passo. Painel de métricas + log de decisões combinados. RAG com documentos curados alimenta o Comentador + lista de fontes permitidas para evitar referências inexistentes. |
| **A — Adapt** | Teste A/B nas primeiras rodadas (2 versões por questão, Validador escolhe a melhor). Temperatura criativa crescente conforme avança nos sub-focos de um tema. |
| **M — Modify** | Feedback do Validador estruturado por categorias de erro (enunciado ambíguo · distratores fracos · gabarito questionável · comentário incompleto · fora do nível). Classificação de nível é responsabilidade do pipeline; curadoria de proporções acontece no sistema de destino. |
| **P — Put to other uses** | Flashcards extraídos da Visão do Aprovado (2-4 por questão, planilha separada). Material de revisão por tema (agente sintetizador). Banco de questões polêmicas (discordâncias entre agentes como material didático). |
| **E — Eliminate** | IA decide tipo de enunciado automaticamente (baseado em tema + foco + nível). Batch automático com checkpoints a cada 10 focos. Checkpoint híbrido: erro pontual → refaz questão · erro sistêmico → ajusta parâmetro + refaz lote. |
| **R — Reverse** | Inversão Comentador-primeiro (gera comentário antes da questão) mantida no backlog como experimento futuro. |

## Idea Organization and Prioritization

### Organização Temática

**Tema 1: Arquitetura do Pipeline Multi-Agente**

- Pipeline de 3 agentes: Criador → Comentador (revisão cega) → Validador (árbitro)
- Comentador comenta SEM saber a correta e declara sua resposta
- Validador compara gabarito vs análise do Comentador
- Feedback estruturado por categorias de erro na devolução
- Limite de 2-3 rodadas antes de revisão humana
- Batch automático com checkpoints híbridos a cada 10 focos

**Tema 2: Estrutura e Qualidade da Questão**

- 3 níveis de dificuldade mapeados à Taxonomia de Bloom
- 8 tipos de enunciado (IA escolhe automaticamente)
- Posição da correta sorteada ANTES da geração com balanceamento estatístico
- Distratores construídos por natureza cognitiva do nível
- Filtro de relevância clínica (evitar ultraespecificidades)
- Campo "objetivo educacional" por questão para controle de duplicidade

**Tema 3: Comentário Estruturado**

- Estrutura fixa e sempre completa: Introdução → Visão Específica → Alt. por Alt. → Visão do Aprovado
- Gerado pelo Comentador às cegas (revisão cega)
- Cada alternativa errada ensina algo, não apenas diz "está errado"
- Referências bibliográficas obrigatórias de fontes verificáveis
- RAG com documentos médicos curados + fontes consagradas do treinamento da IA
- Regra inviolável: NUNCA gerar referências inexistentes

**Tema 4: Pipeline de Geração em Massa (Batch)**

- Batch automático: sobe Excel completo → processa todos os focos autonomamente
- Checkpoints a cada 10 focos com amostra de 5 questões aleatórias
- Checkpoint híbrido: erro pontual → refaz só a questão · erro sistêmico (3+) → ajusta parâmetro + refaz lote
- Sub-focos gerados em bloco (50 de uma vez) antes de gerar questões
- Temperatura criativa crescente para evitar repetição
- Sub-foco flexível: IA automática ou usuário manual

**Tema 5: Controle de Duplicidade e Qualidade**

- Objetivo educacional como metadado para rastrear cobertura
- IA recebe resumo do que já foi coberto antes de gerar nova questão
- Teste A/B nas primeiras rodadas (2 versões, Validador escolhe)
- Exemplos no prompt apenas de estrutura/tom, nunca conteúdo
- RAG com documentos curados para evitar alucinações

**Tema 6: Referências e Conteúdo Médico**

- Ciclo básico (1º-2º ano): Guyton, Junqueira, Robbins, Netter
- Ciclo clínico (3º-4º ano): Protocolos brasileiros (MS, SUS, sociedades médicas) + Harrison, Cecil
- RAG como fonte primária para o Comentador
- Prioridade para protocolos e diretrizes nacionais brasileiras
- Coluna referencia_bibliografica obrigatória no Excel

**Tema 7: Outputs e Subprodutos (Nice to Have — Fase 2)**

- Flashcards: 2-4 por questão da Visão do Aprovado (~16.000-32.000 cards), planilha separada
- Material de revisão: agente sintetizador agrega introduções por tema → "Guia de Revisão"
- Banco de questões polêmicas: discordâncias entre agentes como material para discussão em sala

**Tema 8: Infraestrutura e Métricas**

- Painel de métricas: latência, custo tokens, taxa aprovação, concordância, comparativo modelos
- Teste inicial: 50 questões × 3 modelos (GPT-4o, Claude, Gemini)
- Log de decisões por questão (modelo, tokens, rodadas, tempo)
- Dados de checkpoint alimentam melhoria contínua

### Conceitos Breakthrough

| Conceito | Por que é inovador |
|----------|-------------------|
| Comentador como revisão cega | Transforma o comentário em teste de qualidade — se o "expert" discorda, a questão é ruim |
| Checkpoint híbrido | Diferencia erro pontual de sistêmico, economizando tokens e garantindo qualidade |
| Flashcards de custo zero | ~16.000-32.000 flashcards gerados como subproduto do pipeline existente |
| Questões polêmicas como material didático | Discordâncias entre agentes se tornam recurso pedagógico para debate em sala |
| Sorteio prévio da correta | Elimina viés de posição na construção da questão |

### Prioritization Results

**Top 3 Prioridades (Essenciais):**

1. **Arquitetura do Pipeline Multi-Agente** — A fundação de tudo
2. **Estrutura e Qualidade da Questão** — Questão ruim = sistema inútil
3. **Comentário Estruturado** — Onde o aluno realmente aprende

**Essencial (suporte):**

- Pipeline de geração em massa (batch automático + checkpoints)
- Controle de duplicidade e qualidade
- Referências e conteúdo médico (RAG + fontes permitidas)
- Infraestrutura e métricas (painel + comparativo de modelos)

**Nice to Have (Fase 2):**

- Flashcards extraídos da Visão do Aprovado
- Material de revisão por tema
- Banco de questões polêmicas

### Quick Wins (Primeiros Passos)

1. Definir estrutura exata das colunas do Excel de output
2. Criar prompt do Agente Criador (primeiro agente do pipeline)
3. Rodar 5-10 questões de teste em 2-3 modelos para dados concretos

## Action Planning

### Prioridade 1: Arquitetura do Pipeline Multi-Agente

**Próximos passos:**

1. Definir os prompts de cada agente (Criador, Comentador, Validador)
2. Definir protocolo de comunicação entre agentes (o que cada um recebe e entrega)
3. Implementar fluxo: input Excel → sub-focos em bloco → geração sequencial → comentário cego → validação
4. Implementar lógica de retry com feedback estruturado + limite de 2-3 rodadas
5. Implementar batch automático com checkpoints a cada 10 focos
6. Implementar checkpoint híbrido (erro pontual vs sistêmico)

### Prioridade 2: Estrutura e Qualidade da Questão

**Próximos passos:**

1. Definir estrutura exata das colunas do Excel de output
2. Definir os 8 tipos de enunciado com exemplos de referência
3. Definir lógica de distratores por nível de dificuldade com exemplos
4. Implementar sorteio prévio balanceado da alternativa correta
5. Implementar filtro de relevância clínica no prompt do Criador
6. Implementar campo "objetivo educacional" para controle de duplicidade

### Prioridade 3: Comentário Estruturado

**Próximos passos:**

1. Definir prompt do Agente Comentador com estrutura fixa
2. Configurar RAG com documentos médicos curados
3. Implementar lista de fontes permitidas (evitar referências inexistentes)
4. Garantir que Comentador declara qual alternativa considera correta
5. Testar qualidade dos comentários em diferentes temas e níveis

### Infraestrutura (Suporte)

**Próximos passos:**

1. Montar painel de métricas (latência, tokens, taxa aprovação, concordância)
2. Rodar teste comparativo: 50 questões × 3 modelos
3. Analisar custo-benefício e escolher modelo(s)
4. Preparar Excel de input com colunas enriquecidas

## Session Summary and Insights

**Conquistas da Sessão:**

- 125+ ideias geradas através de 3 técnicas de brainstorming complementares
- Arquitetura multi-agente com revisão cega definida como design central
- 11 dimensões do sistema mapeadas sistematicamente
- Pipeline de geração em massa desenhado com checkpoints inteligentes
- 5 conceitos breakthrough identificados
- Plano de ação concreto com prioridades claras e quick wins definidos

**Insights da Sessão:**

- O sistema transcende "gerador de questões" — é um **sistema de aprendizagem estruturada** com múltiplas camadas de qualidade
- A **revisão cega do Comentador** é a inovação mais poderosa: transforma o pipeline de "geração + checagem" em "geração + teste real + arbitragem"
- A decisão de **sortear a alternativa correta antes da geração** elimina um viés que poucos sistemas consideram
- O **checkpoint híbrido** resolve o dilema entre "parar para revisar tudo" e "confiar cegamente na IA"
- Os **subprodutos** (flashcards, material de revisão, questões polêmicas) representam valor massivo com custo marginal quase zero

### Creative Facilitation Narrative

A sessão progrediu de forma orgânica do abstrato ao concreto: começamos questionando profundamente o que define qualidade em questões médicas (Question Storming), evoluímos para mapear sistematicamente todas as dimensões do sistema (Morphological Analysis), e finalizamos otimizando o pipeline com 7 lentes de inovação (SCAMPER). O momento de maior breakthrough foi quando Rodrigo propôs a arquitetura multi-agente com revisão cega — uma ideia que transformou o sistema de um simples gerador em um pipeline com checks and balances genuínos. A clareza de Rodrigo sobre o público-alvo (alunos de 1º-4º ano, não residentes) foi fundamental para calibrar corretamente o nível de complexidade e evitar armadilhas como usar provas de residência como benchmark.

### Session Highlights

**Forças Criativas do Rodrigo:** Visão sistêmica, capacidade de identificar riscos antes que se tornem problemas (referências inexistentes, questões ultraespecíficas, calibração para o público errado), pensamento arquitetural robusto
**Momentos Breakthrough:** Arquitetura multi-agente com revisão cega, checkpoint híbrido, sorteio prévio da correta
**Fluxo de Energia:** Crescente ao longo da sessão — começou focado em pedagogia e escalou para design de sistema completo com métricas e infraestrutura
