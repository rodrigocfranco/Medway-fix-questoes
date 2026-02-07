# Story 1.2: Criar Modelos Pydantic de Dados

Status: done

## Story

Como Rodrigo,
Eu quero ter todos os modelos Pydantic definidos para estruturar os dados do sistema,
Para que todas as trocas de dados entre componentes sejam validadas e type-safe.

## Acceptance Criteria

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

## Tasks / Subtasks

### Task 1: Implementar models/question.py (AC: #1, #2)
- [x] Criar classe CriadorOutput com BaseModel
  - [x] Adicionar model_config = ConfigDict(strict=True)
  - [x] Implementar campos: enunciado (str), alternativa_a/b/c/d (str)
  - [x] Implementar resposta_correta com Literal["A", "B", "C", "D"]
  - [x] Implementar objetivo_educacional (str)
  - [x] Implementar nivel_dificuldade com Literal[1, 2, 3]
  - [x] Implementar tipo_enunciado (str)
  - [x] Adicionar Field() com descriptions nos campos principais
- [x] Criar classe QuestionRecord com todas as 26 colunas
  - [x] Campos base: tema, foco, sub_foco, periodo (str)
  - [x] Campos da questão: nivel_dificuldade, tipo_enunciado, enunciado
  - [x] Alternativas: alternativa_a, alternativa_b, alternativa_c, alternativa_d
  - [x] Gabarito: resposta_correta (Literal["A","B","C","D"])
  - [x] Objetivo: objetivo_educacional (str)
  - [x] Comentários: comentario_introducao, comentario_visao_especifica
  - [x] Comentários por alternativa: comentario_alt_a/b/c/d
  - [x] Comentário final: comentario_visao_aprovado
  - [x] Referências: referencia_bibliografica, suporte_imagem, fonte_imagem
  - [x] Metadados: modelo_llm, rodadas_validacao, concordancia_comentador

### Task 2: Implementar models/feedback.py (AC: #3, #4)
- [x] Criar classe ComentadorOutput
  - [x] Adicionar model_config = ConfigDict(strict=True)
  - [x] Campo resposta_declarada com Literal["A", "B", "C", "D"]
  - [x] Campos de comentário estruturado (7 seções)
  - [x] Campo referencia_bibliografica (str)
- [x] Criar classe ValidadorOutput
  - [x] Campo decisao com Literal["aprovada", "rejeitada"]
  - [x] Campo concordancia (bool)
  - [x] Campo feedback_estruturado (nested FeedbackEstruturado)
- [x] Criar classe FeedbackEstruturado
  - [x] Campo enunciado_ambiguo (bool)
  - [x] Campo distratores_fracos (bool)
  - [x] Campo gabarito_questionavel (bool)
  - [x] Campo comentario_incompleto (bool)
  - [x] Campo fora_do_nivel (bool)
  - [x] Campo observacoes (str | None)

### Task 3: Implementar models/pipeline.py (AC: #5)
- [x] Criar classe BatchState
  - [x] Campo foco_atual (str)
  - [x] Campo sub_foco_atual (int)
  - [x] Campo total_processados (int)
  - [x] Campo timestamp (str com ISO 8601)
- [x] Criar classe CheckpointResult
  - [x] Campo checkpoint_id (str)
  - [x] Campo foco_range (str, ex: "Focos 1-10")
  - [x] Campo total_geradas (int)
  - [x] Campo aprovadas (int)
  - [x] Campo rejeitadas (int)
  - [x] Campo failed (int)
  - [x] Campo taxa_aprovacao (float)
  - [x] Campo concordancia_media (float)
  - [x] Campo custo_total (float)
  - [x] Campo sample_question_ids (list[int])
- [x] Criar classe RetryContext
  - [x] Campo rodada_atual (int)
  - [x] Campo feedback_estruturado (FeedbackEstruturado)
  - [x] Campo question_id (int | None)

### Task 4: Implementar models/metrics.py (AC: #6)
- [x] Criar classe QuestionMetrics
  - [x] Campo modelo (str)
  - [x] Campo tokens (int)
  - [x] Campo custo (float)
  - [x] Campo rodadas (int)
  - [x] Campo tempo (float, em segundos)
  - [x] Campo decisao (str)
  - [x] Campo timestamp (str)
- [x] Criar classe BatchMetrics
  - [x] Campo total_questoes (int)
  - [x] Campo aprovadas (int)
  - [x] Campo rejeitadas (int)
  - [x] Campo failed (int)
  - [x] Campo custo_total (float)
  - [x] Campo tempo_total (float)
  - [x] Campo taxa_aprovacao (float)
- [x] Criar classe ModelComparison
  - [x] Campo modelo (str)
  - [x] Campo questoes_geradas (int)
  - [x] Campo taxa_aprovacao (float)
  - [x] Campo custo_medio (float)
  - [x] Campo latencia_media (float)
  - [x] Campo taxa_concordancia (float)

### Task 5: Configurar __init__.py para exports (AC: #7, #8, #9)
- [x] Importar e exportar todos os modelos de question.py
- [x] Importar e exportar todos os modelos de feedback.py
- [x] Importar e exportar todos os modelos de pipeline.py
- [x] Importar e exportar todos os modelos de metrics.py
- [x] Adicionar __all__ list com todos os modelos exportados

### Task 6: Criar testes básicos
- [x] Criar tests/test_models/test_question.py
  - [x] Testar CriadorOutput com dados válidos
  - [x] Testar CriadorOutput com dados inválidos (strict mode)
  - [x] Testar QuestionRecord com 26 colunas válidas
- [x] Criar tests/test_models/test_feedback.py
  - [x] Testar FeedbackEstruturado com booleans
  - [x] Testar ValidadorOutput com nested model
- [x] Criar tests/test_models/test_pipeline.py
  - [x] Testar BatchState serialization
- [x] Criar tests/test_models/test_metrics.py
  - [x] Testar QuestionMetrics com valores numéricos

### Task 7: Validação e qualidade
- [x] Executar `uv run ruff check .` e corrigir warnings
- [x] Executar `uv run ruff format .` para formatação
- [x] Executar `uv run pytest tests/test_models/` e verificar 100% pass
- [x] Verificar que todos os imports funcionam via __init__.py

## Context & Business Value

This is **Story 1.2** - the second foundational story of Epic 1. This story creates ALL Pydantic models that define data contracts across the entire system. These models are the **type-safe foundation** for the multi-agent pipeline.

### Critical Importance

**Why This Story is Critical:**
1. **Type Safety:** All data exchanges between agents validated at runtime
2. **Contract Definition:** Clear interfaces between Criador → Comentador → Validador
3. **Foundation for Remaining Stories:** Stories 1.3-1.8 and ALL of Epics 2-4 depend on these models
4. **Prevents Runtime Errors:** Pydantic strict mode catches type mismatches before they cause failures
5. **Enables JSON Mode:** LLM structured outputs parsed directly to validated models

### Business Impact

- **Quality Assurance:** Strict validation prevents malformed questions from entering the pipeline
- **Cost Control:** QuestionMetrics and ModelComparison models enable cost tracking from day 1
- **Resilience:** BatchState and CheckpointResult models enable crash recovery (NFR11-12)
- **Debugging:** Structured models with clear types make issues easy to diagnose

### Dependencies

**Blocked By:**
- ✅ Story 1.1 (project structure) - COMPLETED

**Blocks:**
- Story 1.3 (LLM provider abstraction) - needs CriadorOutput, ComentadorOutput, ValidadorOutput
- Story 1.4 (SQLite persistence) - needs QuestionRecord, BatchState, CheckpointResult
- All Agent stories (2.1-2.8) - depend on these data contracts
- All Dashboard stories (4.1-4.7) - read from models via SQLite

### Success Metrics

- ✅ All 4 model files created (question.py, feedback.py, pipeline.py, metrics.py)
- ✅ All models use `ConfigDict(strict=True)` for validation
- ✅ 100% test coverage for model validation (valid + invalid cases)
- ✅ `ruff check` passes with zero warnings
- ✅ All models importable via `from construtor.models import *`

## Technical Requirements

### Core Technologies

| Technology | Version | Purpose | Documentation |
|-----------|---------|---------|---------------|
| **Pydantic** | v2.x (latest stable) | Data validation & serialization | [Pydantic Docs](https://docs.pydantic.dev/) |
| **Python typing** | 3.11+ stdlib | Type hints (Literal, Optional) | [Python typing](https://docs.python.org/3/library/typing.html) |
| **ConfigDict** | Pydantic v2 | Model configuration (strict mode) | [Config API](https://docs.pydantic.dev/latest/api/config/) |

### Pydantic v2 Strict Mode (2026 Best Practices)

**ConfigDict with strict=True:**

Pydantic v2 strict mode disables implicit type coercion. When enabled on a model, all values must match their type annotations exactly.

```python
from pydantic import BaseModel, ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str  # Only str accepted, no coercion from int/bytes/etc
    age: int   # Only int accepted, no coercion from str
```

**Key Behaviors in Strict Mode:**
- ❌ No implicit coercion: `"123"` will NOT convert to `int`
- ❌ None not allowed for non-Optional fields
- ✅ Exact type match required
- ✅ Validation errors are specific and actionable

**Field-Level Override (if needed):**
```python
from pydantic import Field

class Model(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str  # Strict
    age: int = Field(strict=False)  # Allows coercion for this field only
```

**⚠️ Important:** Strict mode is NOT recursive for nested models. Each nested model must set `strict=True` explicitly.

**Sources:**
- [Pydantic Strict Mode Documentation](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [ConfigDict API Reference](https://docs.pydantic.dev/latest/api/config/)

### Python 3.11 Typing Best Practices

**Literal Types:**
```python
from typing import Literal

# For restricted values (enums)
resposta_correta: Literal["A", "B", "C", "D"]  # Only these 4 values
nivel_dificuldade: Literal[1, 2, 3]  # Only 1, 2, or 3
decisao: Literal["aprovada", "rejeitada"]  # Only these 2 strings
```

**Optional Fields (Pydantic v2 Change):**

⚠️ **IMPORTANT:** In Pydantic v2, `Optional` no longer implies a default of `None`. You MUST provide an explicit default.

```python
from typing import Optional

# ❌ WRONG in Pydantic v2 - No default provided
class Model(BaseModel):
    optional_field: Optional[str]  # Will raise validation error if not provided

# ✅ CORRECT in Pydantic v2
class Model(BaseModel):
    optional_field: Optional[str] = None  # Explicit default required
```

**Required vs Optional Pattern:**
```python
# Required field - NO default
nome: str

# Required with description
nome: str = Field(..., description="Nome completo")

# Optional with None default
observacoes: Optional[str] = None

# Optional with custom default
temperatura: float = 0.7
```

**Sources:**
- [Pydantic Fields Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [Python Types Best Practices](https://fastapi.tiangolo.com/python-types/)

### Field() Function Usage

**When to Use Field():**
1. ✅ Adding descriptions for documentation
2. ✅ Adding validation constraints (min_length, max_length, ge, le)
3. ✅ Explicitly marking required fields with `...`
4. ✅ Adding examples for OpenAPI/JSON schema

**Examples:**
```python
from pydantic import Field

# Description for clarity
enunciado: str = Field(..., description="Texto completo do enunciado da questão")

# Constraints
temperatura: float = Field(default=0.7, ge=0.0, le=1.0, description="Temperature 0-1")

# Optional with description
feedback: Optional[str] = Field(default=None, description="Feedback opcional do validador")

# Required without Field() - also valid
alternativa_a: str  # Simpler when no description needed
```

### Model Organization Requirements

**File Structure:**
```
src/construtor/models/
├── __init__.py          # Exports all models
├── question.py          # CriadorOutput, QuestionRecord
├── feedback.py          # ComentadorOutput, ValidadorOutput, FeedbackEstruturado
├── pipeline.py          # BatchState, CheckpointResult, RetryContext
└── metrics.py           # QuestionMetrics, BatchMetrics, ModelComparison
```

**Import Pattern in __init__.py:**
```python
# src/construtor/models/__init__.py
from .question import CriadorOutput, QuestionRecord
from .feedback import ComentadorOutput, ValidadorOutput, FeedbackEstruturado
from .pipeline import BatchState, CheckpointResult, RetryContext
from .metrics import QuestionMetrics, BatchMetrics, ModelComparison

__all__ = [
    # question.py
    "CriadorOutput",
    "QuestionRecord",
    # feedback.py
    "ComentadorOutput",
    "ValidadorOutput",
    "FeedbackEstruturado",
    # pipeline.py
    "BatchState",
    "CheckpointResult",
    "RetryContext",
    # metrics.py
    "QuestionMetrics",
    "BatchMetrics",
    "ModelComparison",
]
```

### JSON Serialization

**Parsing JSON to Models:**
```python
import json
from construtor.models import CriadorOutput

# From LLM JSON response
json_string = llm_response.content
data = json.loads(json_string)

try:
    criador_output = CriadorOutput(**data)  # Automatic validation
except ValidationError as e:
    # Structured error with field-level details
    logger.error(f"Validation failed: {e.errors()}")
    # Implement retry logic
```

**Model to JSON:**
```python
# Pydantic v2 method
json_string = criador_output.model_dump_json()

# Or as dict
data_dict = criador_output.model_dump()
```

### Validation Error Handling

```python
from pydantic import ValidationError

try:
    model = CriadorOutput(**data)
except ValidationError as e:
    # e.errors() returns list of dicts with:
    # - loc: tuple of field path
    # - msg: error message
    # - type: error type code
    for error in e.errors():
        field = error['loc'][0]
        message = error['msg']
        logger.error(f"Field '{field}': {message}")

## Architecture Compliance

### Naming Conventions (CRITICAL - Must Follow Exactly)

**Source:** [Architecture Doc - Implementation Patterns](../../_bmad-output/planning-artifacts/architecture.md#naming-patterns)

| Element | Convention | Examples | Language |
|---------|-----------|----------|----------|
| **Classes** | PascalCase | `CriadorOutput`, `QuestionRecord`, `FeedbackEstruturado` | English |
| **Functions/Methods** | snake_case | `generate_question()`, `validate_output()` | English |
| **Variables** | snake_case | `question_count`, `approval_rate` | English |
| **Pydantic Fields** | snake_case | ALL fields use snake_case | Mixed* |
| **Constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TEMPERATURE` | English |

**\*Mixed Language Rule for Pydantic Fields:**

🇧🇷 **Portuguese** - Medical/Domain/Excel fields:
- `enunciado` (not "statement")
- `alternativa_a`, `alternativa_b`, `alternativa_c`, `alternativa_d`
- `resposta_correta` (not "correct_answer")
- `objetivo_educacional`
- `nivel_dificuldade`
- `tipo_enunciado`
- `comentario_introducao`, `comentario_visao_especifica`
- `comentario_alt_a`, `comentario_alt_b`, `comentario_alt_c`, `comentario_alt_d`
- `comentario_visao_aprovado`
- `referencia_bibliografica`
- `suporte_imagem`, `fonte_imagem`

🇺🇸 **English** - Technical/Infrastructure fields:
- `model_config`
- `timestamp`
- `question_id`
- `batch_size`
- `checkpoint_id`
- `tokens`, `cost`, `latency`

### Mandatory Pydantic Pattern

**Source:** [Architecture Doc - Structure Patterns](../../_bmad-output/planning-artifacts/architecture.md#structure-patterns)

**EVERY Pydantic model MUST follow this exact template:**

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional

class ModelName(BaseModel):
    """Brief description of what this model represents."""

    # MANDATORY: Strict validation
    model_config = ConfigDict(strict=True)

    # Required fields - no default or use ... with Field()
    required_field: str
    another_required: int = Field(..., description="Clear description")

    # Optional fields - MUST have explicit default
    optional_field: Optional[str] = None
    optional_with_desc: Optional[int] = Field(default=None, description="Optional field")

    # Literal types for restricted values
    restricted: Literal["value1", "value2", "value3"]
```

**Checklist for Every Model:**
- [ ] Inherits from `BaseModel`
- [ ] Has `model_config = ConfigDict(strict=True)`
- [ ] Required fields have no default OR use `Field(...)`
- [ ] Optional fields use `Optional[T]` with explicit default
- [ ] Literal types for enums/restricted values
- [ ] Field names follow Portuguese/English convention
- [ ] Docstring explains model purpose

### Model Contracts (Protocol Between Agents)

**Source:** [Architecture Doc - Communication Patterns](../../_bmad-output/planning-artifacts/architecture.md#protocolo-de-comunicação-entre-agentes)

These models define contracts between pipeline stages:

```
FocoInput → SubFocoGenerator → SubFocoInput
    ↓
SubFocoInput + posição_correta → CriadorAgent → CriadorOutput
    ↓
CriadorOutput + RAG context → ComentadorAgent → ComentadorOutput
    ↓
CriadorOutput + ComentadorOutput → ValidadorAgent → ValidadorOutput
    ↓
    → If aprovada: QuestionRecord → SQLite
    → If rejeitada: FeedbackEstruturado → RetryManager → back to Criador
```

**Contract Rules:**
1. ✅ Agents ONLY communicate via Pydantic models (never bare dicts)
2. ✅ Output of Agent N = Input of Agent N+1
3. ✅ All validation happens at model boundaries
4. ✅ Parse failures trigger retry logic

### Anti-Patterns (STRICTLY FORBIDDEN)

**Source:** [Architecture Doc - Anti-Patterns](../../_bmad-output/planning-artifacts/architecture.md#anti-patterns-proibidos)

```python
# ❌ ANTI-PATTERN 1: Bare dict returns
def generate_question() -> dict:
    return {"enunciado": "...", "alternativa_a": "..."}

# ✅ CORRECT: Pydantic model return
def generate_question() -> CriadorOutput:
    return CriadorOutput(enunciado="...", alternativa_a="...")

# ❌ ANTI-PATTERN 2: Optional without default (Pydantic v2)
class Model(BaseModel):
    optional_field: Optional[str]  # Missing default!

# ✅ CORRECT: Optional with explicit default
class Model(BaseModel):
    optional_field: Optional[str] = None

# ❌ ANTI-PATTERN 3: English domain fields
class Model(BaseModel):
    statement: str  # Wrong! Should be "enunciado"
    correct_answer: str  # Wrong! Should be "resposta_correta"

# ✅ CORRECT: Portuguese domain fields
class Model(BaseModel):
    enunciado: str
    resposta_correta: str
```

### Required Models by Module

#### models/question.py

**CriadorOutput** - Output from question creator agent
```python
class CriadorOutput(BaseModel):
    model_config = ConfigDict(strict=True)

    enunciado: str = Field(..., description="Texto completo do enunciado")
    alternativa_a: str = Field(..., description="Primeira alternativa")
    alternativa_b: str = Field(..., description="Segunda alternativa")
    alternativa_c: str = Field(..., description="Terceira alternativa")
    alternativa_d: str = Field(..., description="Quarta alternativa")
    resposta_correta: Literal["A", "B", "C", "D"] = Field(..., description="Letra da resposta correta")
    objetivo_educacional: str = Field(..., description="Objetivo pedagógico")
    nivel_dificuldade: Literal[1, 2, 3] = Field(..., description="1=fácil, 2=médio, 3=difícil")
    tipo_enunciado: str = Field(..., description="Tipo: conceitual, caso clínico, etc.")
```

**QuestionRecord** - Complete question with 26 columns for Excel export
```python
class QuestionRecord(BaseModel):
    model_config = ConfigDict(strict=True)

    # Base fields
    tema: str
    foco: str
    sub_foco: str
    periodo: str

    # Question fields (from CriadorOutput)
    nivel_dificuldade: Literal[1, 2, 3]
    tipo_enunciado: str
    enunciado: str
    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str
    resposta_correta: Literal["A", "B", "C", "D"]
    objetivo_educacional: str

    # Comment fields (from ComentadorOutput)
    comentario_introducao: str
    comentario_visao_especifica: str
    comentario_alt_a: str
    comentario_alt_b: str
    comentario_alt_c: str
    comentario_alt_d: str
    comentario_visao_aprovado: str
    referencia_bibliografica: str

    # Image support (optional)
    suporte_imagem: Optional[str] = None
    fonte_imagem: Optional[str] = None

    # Metadata
    modelo_llm: str
    rodadas_validacao: int
    concordancia_comentador: bool
```

#### models/feedback.py

**ComentadorOutput** - Blind review output
```python
class ComentadorOutput(BaseModel):
    model_config = ConfigDict(strict=True)

    resposta_declarada: Literal["A", "B", "C", "D"] = Field(
        ..., description="Alternativa que o comentador considera correta (revisão cega)"
    )
    comentario_introducao: str
    comentario_visao_especifica: str
    comentario_alt_a: str
    comentario_alt_b: str
    comentario_alt_c: str
    comentario_alt_d: str
    comentario_visao_aprovado: str
    referencia_bibliografica: str = Field(..., description="Fonte verificável do Pinecone")
```

**FeedbackEstruturado** - Structured error categories
```python
class FeedbackEstruturado(BaseModel):
    model_config = ConfigDict(strict=True)

    enunciado_ambiguo: bool = Field(default=False, description="Enunciado confuso ou ambíguo")
    distratores_fracos: bool = Field(default=False, description="Alternativas incorretas óbvias")
    gabarito_questionavel: bool = Field(default=False, description="Resposta correta discutível")
    comentario_incompleto: bool = Field(default=False, description="Comentário não cobre todas seções")
    fora_do_nivel: bool = Field(default=False, description="Dificuldade não corresponde ao nível")
    observacoes: Optional[str] = Field(default=None, description="Detalhes adicionais do problema")
```

**ValidadorOutput** - Validation decision
```python
class ValidadorOutput(BaseModel):
    model_config = ConfigDict(strict=True)

    decisao: Literal["aprovada", "rejeitada"] = Field(..., description="Aprovação ou rejeição")
    concordancia: bool = Field(..., description="Comentador concordou com gabarito?")
    feedback_estruturado: FeedbackEstruturado = Field(..., description="Categorias de erro")
```

#### models/pipeline.py

**BatchState** - Pipeline progress state
```python
class BatchState(BaseModel):
    model_config = ConfigDict(strict=True)

    foco_atual: str
    sub_foco_atual: int
    total_processados: int
    timestamp: str  # ISO 8601 format
```

**CheckpointResult** - Checkpoint validation data
```python
class CheckpointResult(BaseModel):
    model_config = ConfigDict(strict=True)

    checkpoint_id: str
    foco_range: str  # e.g., "Focos 1-10"
    total_geradas: int
    aprovadas: int
    rejeitadas: int
    failed: int
    taxa_aprovacao: float
    concordancia_media: float
    custo_total: float
    sample_question_ids: list[int]
```

**RetryContext** - Retry state
```python
class RetryContext(BaseModel):
    model_config = ConfigDict(strict=True)

    rodada_atual: int
    feedback_estruturado: FeedbackEstruturado
    question_id: Optional[int] = None
```

#### models/metrics.py

**QuestionMetrics** - Per-question metrics
```python
class QuestionMetrics(BaseModel):
    model_config = ConfigDict(strict=True)

    modelo: str
    tokens: int
    custo: float
    rodadas: int
    tempo: float  # seconds
    decisao: str
    timestamp: str
```

**BatchMetrics** - Batch-level aggregation
```python
class BatchMetrics(BaseModel):
    model_config = ConfigDict(strict=True)

    total_questoes: int
    aprovadas: int
    rejeitadas: int
    failed: int
    custo_total: float
    tempo_total: float
    taxa_aprovacao: float
```

**ModelComparison** - Model performance comparison
```python
class ModelComparison(BaseModel):
    model_config = ConfigDict(strict=True)

    modelo: str
    questoes_geradas: int
    taxa_aprovacao: float
    custo_medio: float
    latencia_media: float
    taxa_concordancia: float

## Testing Requirements

### Story 1.2 Testing Scope

**Goal:** Verify that all Pydantic models validate correctly with both valid and invalid data.

**Test Structure:**
```
tests/test_models/
├── __init__.py
├── test_question.py      # CriadorOutput, QuestionRecord
├── test_feedback.py      # ComentadorOutput, ValidadorOutput, FeedbackEstruturado
├── test_pipeline.py      # BatchState, CheckpointResult, RetryContext
└── test_metrics.py       # QuestionMetrics, BatchMetrics, ModelComparison
```

### Test Patterns

#### Pattern 1: Valid Data Test
```python
import pytest
from construtor.models import CriadorOutput

def test_criador_output_valid():
    """Test CriadorOutput accepts valid data."""
    data = {
        "enunciado": "Qual é a função principal do fígado?",
        "alternativa_a": "Produzir bile",
        "alternativa_b": "Filtrar sangue",
        "alternativa_c": "Produzir insulina",
        "alternativa_d": "Armazenar vitaminas",
        "resposta_correta": "A",
        "objetivo_educacional": "Identificar funções hepáticas",
        "nivel_dificuldade": 1,
        "tipo_enunciado": "conceitual"
    }

    output = CriadorOutput(**data)

    assert output.enunciado == "Qual é a função principal do fígado?"
    assert output.resposta_correta == "A"
    assert output.nivel_dificuldade == 1
```

#### Pattern 2: Invalid Data Test (Strict Mode)
```python
def test_criador_output_invalid_resposta_correta():
    """Test CriadorOutput rejects invalid resposta_correta."""
    data = {
        "enunciado": "Teste",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "E",  # ❌ Invalid! Must be A, B, C, or D
        "objetivo_educacional": "Teste",
        "nivel_dificuldade": 1,
        "tipo_enunciado": "conceitual"
    }

    with pytest.raises(ValidationError) as exc_info:
        CriadorOutput(**data)

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('resposta_correta',) for error in errors)
```

#### Pattern 3: Strict Mode Type Coercion Test
```python
def test_criador_output_strict_mode_no_coercion():
    """Test that strict mode prevents type coercion."""
    data = {
        "enunciado": "Teste",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "A",
        "objetivo_educacional": "Teste",
        "nivel_dificuldade": "1",  # ❌ String instead of int
        "tipo_enunciado": "conceitual"
    }

    with pytest.raises(ValidationError) as exc_info:
        CriadorOutput(**data)

    # Strict mode: no coercion from "1" to 1
    errors = exc_info.value.errors()
    assert any(error['loc'] == ('nivel_dificuldade',) for error in errors)
```

#### Pattern 4: Optional Field Test
```python
def test_feedback_estruturado_optional_observacoes():
    """Test that optional fields work with None default."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False
        # observacoes not provided - should default to None
    )

    assert feedback.observacoes is None

    # Also test with explicit value
    feedback_with_obs = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="Enunciado usa terminologia ambígua"
    )

    assert feedback_with_obs.observacoes == "Enunciado usa terminologia ambígua"
```

#### Pattern 5: Nested Model Test
```python
def test_validador_output_with_nested_feedback():
    """Test ValidadorOutput with nested FeedbackEstruturado."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="Teste"
    )

    validador = ValidadorOutput(
        decisao="rejeitada",
        concordancia=False,
        feedback_estruturado=feedback
    )

    assert validador.decisao == "rejeitada"
    assert validador.feedback_estruturado.enunciado_ambiguo is True
```

#### Pattern 6: Model Serialization Test
```python
def test_criador_output_json_serialization():
    """Test model can serialize to/from JSON."""
    original = CriadorOutput(
        enunciado="Teste",
        alternativa_a="A",
        alternativa_b="B",
        alternativa_c="C",
        alternativa_d="D",
        resposta_correta="A",
        objetivo_educacional="Teste",
        nivel_dificuldade=1,
        tipo_enunciado="conceitual"
    )

    # Serialize to JSON
    json_str = original.model_dump_json()

    # Deserialize back
    import json
    data = json.loads(json_str)
    reconstructed = CriadorOutput(**data)

    assert reconstructed.enunciado == original.enunciado
    assert reconstructed.resposta_correta == original.resposta_correta
```

### Test Coverage Requirements

**Minimum Coverage per Model:**
- ✅ 1 test with fully valid data
- ✅ 1 test with invalid Literal value
- ✅ 1 test for strict mode (no type coercion)
- ✅ 1 test for Optional fields (if model has any)
- ✅ 1 test for nested models (if applicable)

**Total Expected Tests:**
- test_question.py: ~6 tests (CriadorOutput + QuestionRecord)
- test_feedback.py: ~8 tests (3 models with nested)
- test_pipeline.py: ~6 tests (3 models)
- test_metrics.py: ~6 tests (3 models)
- **Total: ~26 tests minimum**

### Running Tests

```bash
# Run all model tests
uv run pytest tests/test_models/ -v

# Run specific test file
uv run pytest tests/test_models/test_question.py -v

# Run with coverage
uv run pytest tests/test_models/ --cov=src/construtor/models --cov-report=term-missing

# Expected output: 100% coverage on models/ (all classes tested)
```

### Test Success Criteria

- [ ] All tests pass with pytest
- [ ] No validation warnings or errors
- [ ] Coverage ≥ 95% on models/
- [ ] All Literal types tested with invalid values
- [ ] All Optional fields tested with None
- [ ] Strict mode behavior verified (no coercion)

## Dev Notes

### Implementation Sequence

**Recommended Order:**
1. **models/question.py** - Foundation for agent contracts
   - Start with CriadorOutput (smallest, core contract)
   - Then QuestionRecord (all 26 columns)
2. **models/feedback.py** - Agent communication
   - FeedbackEstruturado (no dependencies)
   - ComentadorOutput (uses FeedbackEstruturado in tests)
   - ValidadorOutput (nests FeedbackEstruturado)
3. **models/pipeline.py** - State management
   - BatchState (simple)
   - RetryContext (uses FeedbackEstruturado)
   - CheckpointResult (most complex)
4. **models/metrics.py** - Analytics
   - QuestionMetrics (simple)
   - BatchMetrics (simple)
   - ModelComparison (simple)
5. **models/__init__.py** - Exports
6. **tests/test_models/** - Validation tests

### Common Pitfalls to Avoid

❌ **Don't:** Forget `model_config = ConfigDict(strict=True)` (will break validation)
❌ **Don't:** Use `Optional[str]` without `= None` default (Pydantic v2 change)
❌ **Don't:** Mix English/Portuguese incorrectly (enunciado NOT statement)
❌ **Don't:** Return bare dicts instead of models
❌ **Don't:** Skip tests for invalid data (strict mode must be verified)
❌ **Don't:** Use string literals like `"aprovada"` without Literal type
❌ **Don't:** Add logic to models (keep them pure data structures)

✅ **Do:** Use Literal for all restricted values
✅ **Do:** Add Field(description="...") for complex fields
✅ **Do:** Test both valid and invalid data for each model
✅ **Do:** Keep models in separate files by domain
✅ **Do:** Export all models via __init__.py
✅ **Do:** Follow Portuguese/English naming exactly
✅ **Do:** Verify strict mode prevents coercion

### Key Architecture Patterns to Follow

**Pattern 1: Strict Validation Everywhere**
```python
# Every model starts with this
model_config = ConfigDict(strict=True)
```

**Pattern 2: Clear Required vs Optional**
```python
# Required
campo_obrigatorio: str

# Optional (MUST have default)
campo_opcional: Optional[str] = None
```

**Pattern 3: Literal for Enums**
```python
# Not just str - use Literal!
resposta_correta: Literal["A", "B", "C", "D"]
decisao: Literal["aprovada", "rejeitada"]
```

**Pattern 4: Portuguese Domain, English Tech**
```python
# Domain fields - Portuguese
enunciado: str
resposta_correta: Literal["A", "B", "C", "D"]

# Tech fields - English
timestamp: str
question_id: int
```

### Previous Story Intelligence (Story 1.1)

**Key Learnings from Story 1.1 Implementation:**

✅ **Project Structure Established:**
- `src/construtor/models/` exists with `__init__.py`
- `tests/test_models/` ready for tests
- Pydantic dependency already installed (latest stable)
- Ruff configured (line-length=120, target-version="py311")

✅ **Development Tools Working:**
- `uv run ruff check .` - linting command ready
- `uv run ruff format .` - formatting command ready
- `uv run pytest` - test discovery working
- Python 3.11.14 active in virtual environment

✅ **Code Conventions Confirmed:**
- PEP 8 compliance enforced via ruff
- snake_case for functions/variables/fields
- PascalCase for classes
- .gitignore protects .env and data/

✅ **Git Workflow Established:**
- Commits use conventional format: `feat: description`
- Co-Authored-By tag for Claude collaboration
- Story completion triggers sprint-status update

✅ **Security Patterns:**
- No hardcoded secrets
- .env.example provides template
- Sensitive folders in .gitignore

**Files Created in Story 1.1:**
- src/construtor/models/__init__.py (empty, ready for exports)
- tests/test_models/__init__.py (empty, ready for tests)
- pyproject.toml (dependencies + ruff config)
- .env.example (API key templates)
- .gitignore (security patterns)

**Story 1.1 Git Commit Analysis:**
- Commit: c04c303 "feat: inicializar projeto com estrutura base completa"
- All 8 module directories created
- All dependencies installed without conflicts
- Ruff configuration validated
- Testing structure verified with pytest

**Blockers Resolved in Story 1.1:**
- ✅ uv 0.10.0 installed on system
- ✅ Python 3.11.14 installed and configured
- ✅ Virtual environment created automatically by uv
- ✅ All dependencies resolved (57 production + 5 dev packages)

### File References for Implementation

**Templates to Reference:**
- [Architecture - Pydantic Pattern](../../_bmad-output/planning-artifacts/architecture.md#structure-patterns) - Line 276-293
- [Architecture - Naming Conventions](../../_bmad-output/planning-artifacts/architecture.md#naming-patterns) - Line 246-269
- [Architecture - Anti-Patterns](../../_bmad-output/planning-artifacts/architecture.md#anti-patterns-proibidos) - Line 390-409

**Related Stories:**
- [Story 1.1 - Project Initialization](./1-1-inicializar-projeto-e-estrutura-base.md) - Completed
- [Epic 1 Overview](../../_bmad-output/planning-artifacts/epics.md#epic-1-fundação-do-projeto-e-infraestrutura-core)
- [PRD - Data Model](../../_bmad-output/planning-artifacts/prd.md#modelo-de-dados--excel-de-output)

### Success Criteria Checklist

Before marking story complete:

**Code Quality:**
- [ ] All 4 model files created (question.py, feedback.py, pipeline.py, metrics.py)
- [ ] All models have `ConfigDict(strict=True)`
- [ ] All models follow Portuguese/English naming convention
- [ ] All Optional fields have explicit defaults
- [ ] All restricted values use Literal types
- [ ] models/__init__.py exports all models

**Testing:**
- [ ] Test files exist for all 4 modules
- [ ] All models tested with valid data
- [ ] All models tested with invalid data (strict mode)
- [ ] All Optional fields tested
- [ ] All nested models tested
- [ ] pytest passes all tests (26+ tests expected)

**Code Standards:**
- [ ] `uv run ruff check .` passes with 0 warnings
- [ ] `uv run ruff format .` applies consistent style
- [ ] All imports work via `from construtor.models import *`
- [ ] No bare dict returns anywhere
- [ ] No hardcoded values (use Literal)

**Documentation:**
- [ ] All complex fields have Field(description="...")
- [ ] Each model has docstring
- [ ] __all__ list complete in __init__.py

**Ready for Next Story:**
- [ ] Story 1.3 (LLM abstraction) can import CriadorOutput, ComentadorOutput, ValidadorOutput
- [ ] Story 1.4 (SQLite) can import QuestionRecord, BatchState, CheckpointResult
- [ ] All future agent stories have data contracts defined

## Latest Tech Information (2026)

### Pydantic v2 ConfigDict Strict Mode

**Source Research (Feb 2026):**

Based on the latest Pydantic documentation, `ConfigDict` with `strict=True` provides fine-grained control over validation behavior:

**Key Findings:**

1. **Global Strict Mode:**
   - Set `model_config = ConfigDict(strict=True)` on the model
   - Disables ALL implicit type coercion
   - Applies to all fields by default

2. **Field-Level Override:**
   - Individual fields can override with `Field(strict=False)`
   - Useful for mixing strict and lenient validation
   - Example: strict model with one coercive field

3. **Non-Recursive Behavior:**
   - ⚠️ **IMPORTANT:** Strict mode is NOT recursive to nested models
   - Each nested Pydantic model must set `strict=True` explicitly
   - For our project: FeedbackEstruturado nested in ValidadorOutput
   - **Action:** Both models must have `ConfigDict(strict=True)`

4. **Pydantic v2.11+ Features:**
   - `validate_by_alias` setting for more control
   - Not needed for our use case (internal models)

**Implementation Impact:**
```python
# Parent model - strict
class ValidadorOutput(BaseModel):
    model_config = ConfigDict(strict=True)
    feedback_estruturado: FeedbackEstruturado

# Nested model - MUST ALSO be strict
class FeedbackEstruturado(BaseModel):
    model_config = ConfigDict(strict=True)  # ← Required!
    enunciado_ambiguo: bool
```

**Sources:**
- [Pydantic Strict Mode Documentation](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [ConfigDict API Reference](https://docs.pydantic.dev/latest/api/config/)

### Python 3.11 Typing & Optional Changes

**Key Pydantic v2 Migration Point:**

**Pydantic v1 Behavior (OLD):**
```python
# In v1, this had implicit default of None
class Model(BaseModel):
    optional_field: Optional[str]  # Automatically defaulted to None
```

**Pydantic v2 Behavior (CURRENT):**
```python
# In v2, MUST provide explicit default
class Model(BaseModel):
    optional_field: Optional[str] = None  # ← Explicit default required!
```

**Why This Matters:**
- Breaking change from v1 to v2
- Our project uses Pydantic v2 (latest stable)
- All Optional fields MUST have explicit defaults
- Forgetting `= None` causes validation errors

**TypedDict Support (Python 3.11+):**
- `typing.Required` for selective required fields in TypedDict
- Not applicable to our Pydantic models
- Mentioned for completeness

**Sources:**
- [Pydantic Fields Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [Python Types Best Practices](https://fastapi.tiangolo.com/python-types/)

### Literal Types Best Practices

**Union Discriminators with Literal:**

Pydantic v2 supports discriminated unions using Literal types:

```python
from typing import Union, Literal
from pydantic import Field

class ApprovedResult(BaseModel):
    status: Literal["aprovada"]
    # ... approved-specific fields

class RejectedResult(BaseModel):
    status: Literal["rejeitada"]
    # ... rejected-specific fields

# Discriminated union
Result = Union[ApprovedResult, RejectedResult]
# Set discriminator
result: Result = Field(discriminator='status')
```

**For Our Project:**
- ValidadorOutput uses Literal["aprovada", "rejeitada"]
- Simple flat model - no discriminated union needed
- Literal provides validation without union complexity

**Sources:**
- [Standard Library Types - Pydantic](https://docs.pydantic.dev/latest/api/standard_library_types/)

## Project Structure Notes

### Alignment with Architecture

**100% Compliant with Architecture Document:**
- ✅ Follows [src/ layout](../../_bmad-output/planning-artifacts/architecture.md#complete-project-directory-structure)
- ✅ Uses [Pydantic patterns](../../_bmad-output/planning-artifacts/architecture.md#structure-patterns)
- ✅ Implements [naming conventions](../../_bmad-output/planning-artifacts/architecture.md#naming-patterns)
- ✅ Avoids [anti-patterns](../../_bmad-output/planning-artifacts/architecture.md#anti-patterns-proibidos)
- ✅ Enables [agent boundaries](../../_bmad-output/planning-artifacts/architecture.md#architectural-boundaries)

**Critical for Future Stories:**
- Story 1.3 (LLM providers) imports CriadorOutput, ComentadorOutput, ValidadorOutput
- Story 1.4 (SQLite) maps QuestionRecord to database schema
- Stories 2.1-2.8 (agents) use these models as contracts
- Stories 4.1-4.7 (dashboard) read metrics models from SQLite

**Detected Conflicts:** None - fresh implementation matches architecture exactly

### References

**Architecture Documentation:**
- [Complete Project Structure](../../_bmad-output/planning-artifacts/architecture.md#complete-project-directory-structure) - Lines 415-514
- [Pydantic Model Patterns](../../_bmad-output/planning-artifacts/architecture.md#structure-patterns) - Lines 273-293
- [Naming Conventions](../../_bmad-output/planning-artifacts/architecture.md#naming-patterns) - Lines 246-269
- [Communication Patterns](../../_bmad-output/planning-artifacts/architecture.md#communication-patterns) - Lines 187-193

**Requirements Documentation:**
- [PRD - Data Model (26 columns)](../../_bmad-output/planning-artifacts/prd.md#modelo-de-dados--excel-de-output) - Lines 265-293
- [Epics - Story 1.2](../../_bmad-output/planning-artifacts/epics.md#story-12-criar-modelos-pydantic-de-dados) - Lines 215-234

**Related Stories:**
- [Story 1.1 - Project Init](./1-1-inicializar-projeto-e-estrutura-base.md) - Completed (dependency)
- Story 1.3 - LLM Abstraction (blocked by this story)
- Story 1.4 - SQLite Persistence (blocked by this story)

## Dev Agent Record

### Agent Model Used

**Model:** Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
**Date:** 2026-02-07

### Debug Log References

No significant issues encountered. Implementation followed TDD (red-green-refactor) cycle successfully.

**Minor issues resolved:**
- Package installation: Installed in editable mode via `uv pip install -e .` for imports to work
- Ruff linting: Auto-fixed 23 formatting issues (trailing commas, import sorting, Optional→union syntax)
- Test correction: Updated one test expectation to match Pydantic strict mode behavior (int→float coercion is allowed as lossless)

### Completion Notes List

**Implementation Summary:**
- [x] All 4 model files created with 11 total Pydantic models
- [x] All tests passing (41 comprehensive tests across 4 test files)
- [x] Ruff checks passing (0 warnings on src/ code)
- [x] Models importable via __init__.py with alphabetically sorted __all__ list
- [x] Story file updated with actual completion details

**Key Achievements:**
- ✅ 100% strict mode validation (ConfigDict(strict=True)) on all models
- ✅ Modern Python typing (str | None instead of Optional, Literal types for enums)
- ✅ Comprehensive test coverage: valid data, invalid data, strict mode, serialization, nested models
- ✅ Portuguese/English naming convention followed exactly as specified
- ✅ Field descriptions added to all complex fields
- ✅ All 26 columns implemented in QuestionRecord
- ✅ Nested model validation working (FeedbackEstruturado in ValidadorOutput and RetryContext)

**Test Statistics:**
- Total tests: 41
- test_question.py: 8 tests (CriadorOutput + QuestionRecord)
- test_feedback.py: 11 tests (FeedbackEstruturado + ComentadorOutput + ValidadorOutput)
- test_pipeline.py: 10 tests (BatchState + CheckpointResult + RetryContext)
- test_metrics.py: 12 tests (QuestionMetrics + BatchMetrics + ModelComparison)
- All tests pass in 0.04s

### File List

**Files Created:**
- src/construtor/models/question.py (CriadorOutput, QuestionRecord)
- src/construtor/models/feedback.py (FeedbackEstruturado, ComentadorOutput, ValidadorOutput)
- src/construtor/models/pipeline.py (BatchState, CheckpointResult, RetryContext)
- src/construtor/models/metrics.py (QuestionMetrics, BatchMetrics, ModelComparison)
- src/construtor/models/__init__.py (complete exports with __all__)
- tests/test_models/test_question.py (8 tests)
- tests/test_models/test_feedback.py (11 tests)
- tests/test_models/test_pipeline.py (10 tests)
- tests/test_models/test_metrics.py (12 tests)

**Files Modified:**
- _bmad-output/implementation-artifacts/sprint-status.yaml (status: ready-for-dev → in-progress)
- _bmad-output/implementation-artifacts/1-2-criar-modelos-pydantic-de-dados.md (this file - tasks marked complete)

---

**Created:** 2026-02-07
**Epic:** 1 - Fundação do Projeto e Infraestrutura Core
**Priority:** CRITICAL - Blocks Stories 1.3, 1.4 and all agent implementations
**Estimated Effort:** 2-3 hours
```
```
