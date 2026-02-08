# Story 1.6: Implementar Escritor de Excel de Output

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

Como Rodrigo,
Eu quero exportar questões aprovadas para um Excel com as 26 colunas estruturadas,
Para que eu possa entregar o arquivo final à equipe de importação (FR23, FR25).

## Acceptance Criteria

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

## Tasks / Subtasks

### Task 1: Design ExcelWriter Class Structure (AC: All)
- [x] Create ExcelWriter class in src/construtor/io/excel_writer.py
- [x] Define COLUMN_ORDER constant with all 26 columns in correct sequence
- [x] Implement export_to_excel(output_path: str, limit: Optional[int] = None) method
- [x] Add type hints on all public methods
- [x] Add comprehensive docstring with Args/Returns/Raises

### Task 2: Implement SQLite Data Loading (AC: #1)
- [x] Connect to SQLite database (output/pipeline_state.db)
- [x] Query questions table with WHERE status='approved'
- [x] Handle optional LIMIT parameter for partial exports (testing/debugging)
- [x] Convert SQLite rows to DataFrame with proper column mapping
- [x] Handle empty result set (no approved questions yet)
- [x] Log INFO with count of questions loaded

### Task 3: Create DataFrame with Correct Structure (AC: #2)
- [x] Map QuestionRecord fields to 26 Excel columns
- [x] Ensure column order matches COLUMN_ORDER constant
- [x] Handle NULL/None values appropriately (empty strings for display)
- [x] Verify all 26 columns are present
- [x] Handle data type conversion (INT to STR for periodo, nivel_dificuldade)
- [x] Log DEBUG with DataFrame shape and columns

### Task 4: Implement Atomic File Writing (AC: #3, #7)
- [x] Generate temporary file path (output_path + '.tmp')
- [x] Write DataFrame to temporary Excel file using openpyxl engine
- [x] Apply basic formatting (bold headers, auto-width columns)
- [x] Verify temporary file was created successfully
- [x] Atomically rename temp file to final output_path (os.replace)
- [x] Handle cleanup of temp file if error occurs
- [x] Log INFO when atomic write succeeds

### Task 5: Apply Excel Formatting (AC: #3)
- [x] Use openpyxl directly for formatting after pandas write
- [x] Make header row bold (font.bold = True)
- [x] Set column widths based on content (auto-width or fixed reasonable widths)
- [x] Optionally freeze header row for better UX
- [x] Handle formatting errors gracefully (log WARNING, continue)

### Task 6: Implement Directory Creation (AC: #4)
- [x] Use pathlib.Path to parse output_path
- [x] Check if parent directory exists
- [x] Create parent directories with Path.mkdir(parents=True, exist_ok=True)
- [x] Log INFO when directory is created
- [x] Handle permission errors with clear OSError message

### Task 7: Implement Comprehensive Error Handling (AC: #5, #6)
- [x] Catch sqlite3.Error and raise OSError with context
- [x] Catch pandas/openpyxl exceptions and raise OSError
- [x] Catch PermissionError for file writing and raise OSError
- [x] Ensure temp file is deleted on error (try/finally or context manager)
- [x] Include output_path, question_count, and error details in all exceptions
- [x] Log ERROR before raising exceptions (using logging.exception)

### Task 8: Implement Structured Logging (AC: #6)
- [x] Import logging and create logger = logging.getLogger(__name__)
- [x] Log INFO: "Loading approved questions from SQLite"
- [x] Log INFO: "Loaded {count} approved questions"
- [x] Log INFO: "Writing Excel to {output_path}"
- [x] Log INFO: "Successfully exported {count} questions to {output_path}"
- [x] Log ERROR: Detailed error messages with context
- [x] Log WARNING: If zero questions approved (nothing to export)

### Task 9: Create Comprehensive Tests
- [x] Create tests/test_io/test_excel_writer.py
- [x] Test successful export with sample approved questions
- [x] Test atomic write (temp file created and renamed)
- [x] Test directory creation when parent doesn't exist
- [x] Test error when SQLite database doesn't exist
- [x] Test error when no approved questions (empty export)
- [x] Test column order matches expected 26 columns
- [x] Test header formatting (bold)
- [x] Test OSError raised on write failure
- [x] Create fixtures for sample QuestionRecord data
- [x] Test export with LIMIT parameter (partial export)

### Task 10: Quality Validation
- [x] Run `uv run ruff check src/construtor/io/` and fix all warnings
- [x] Run `uv run ruff format src/construtor/io/` for formatting
- [x] Run `uv run pytest tests/test_io/test_excel_writer.py` and verify 100% pass
- [x] Verify imports: `from construtor.io import ExcelWriter`
- [x] Check snake_case naming throughout
- [x] Verify type hints on all public methods
- [x] Verify docstrings with Args/Returns/Raises
- [x] Test end-to-end: create sample data in SQLite → export → verify Excel

## Dev Notes

### Context & Business Value

Esta é a **Story 1.6** - a sexta história do Epic 1. Esta story cria o **escritor de Excel de output** que permite Rodrigo exportar as questões aprovadas para um arquivo Excel estruturado com as 26 colunas necessárias para a equipe de importação na plataforma de ensino.

### Importância Crítica

**Por que esta Story é CRÍTICA:**
1. **Entrega Final do Produto:** O Excel de output É o produto final do pipeline - sem ele, não há como entregar as ~8.000 questões geradas
2. **Conformidade com Stakeholder:** A equipe de importação espera exatamente 26 colunas em ordem específica - qualquer desvio quebra a integração
3. **Resiliência Obrigatória (NFR12):** Escrita atômica previne corrupção de arquivo em crash - crítico para produção em massa que roda por horas
4. **Fundação para Epic 3:** Stories 3.1-3.6 (batch processing) dependem de escrita parcial confiável do Excel
5. **Conformidade FR23, FR25:** Requisitos funcionais fundamentais do produto

**ERROS COMUNS A PREVENIR:**
- ❌ **Ordem de colunas errada** → Equipe de importação recebe dados desalinhados, importação falha
- ❌ **Escrita não-atômica** → Crash durante escrita corrompe arquivo, perda de horas de processamento
- ❌ **Não criar diretórios** → Script falha na primeira execução se pasta output/ não existe
- ❌ **Não tratar status NULL** → Questões 'pending'/'rejected' vazam para Excel final
- ❌ **Formatação faltando** → Excel sem headers em negrito dificulta validação visual humana
- ❌ **Não logar quantidade exportada** → Impossível validar que todas as questões aprovadas foram incluídas
- ❌ **Não mapear campos corretamente** → Colunas do SQLite (snake_case) vs Excel (português) requerem mapeamento explícito

### Impacto no Negócio

- **Prazo Garantido:** Atomic writes previnem reprocessamento por corrupção (deadline 14/02/2026 é apertado)
- **Integração Garantida:** 26 colunas na ordem correta garantem que equipe de importação pode processar sem ajustes manuais
- **Qualidade Assegurada:** Somente questões 'approved' exportadas garante Excel final sem drafts ou rejeitadas
- **Experiência do Desenvolvedor:** Logs claros ("Exported 8.432 questions to output/final.xlsx") permitem validação rápida

### Dependências

**Bloqueado Por:**
- ✅ Story 1.1 (estrutura do projeto) - COMPLETADA
- ✅ Story 1.2 (modelos Pydantic) - COMPLETADA - Fornece QuestionRecord model
- ✅ Story 1.4 (SQLite persistence) - COMPLETADA - Fornece tabela questions
- ✅ Story 1.5 (Excel Reader) - COMPLETADA - Estabelece padrão pandas/openpyxl

**Bloqueia:**
- Story 2.8 (Pipeline Orchestrator) - precisa salvar questões aprovadas via ExcelWriter
- Story 3.1 (Batch Processor) - precisa exportar parcialmente durante processamento
- Story 3.6 (Exportação Final) - usa ExcelWriter para gerar Excel final
- Todo o Epic 3 - produção em massa depende de escrita confiável

### Métricas de Sucesso

- ✅ Excel válido com 26 colunas gerado a partir de SQLite com questões aprovadas
- ✅ Coluna order matches: tema, foco, sub_foco, periodo, nivel_dificuldade, ... (26 total)
- ✅ Escrita atômica validada: arquivo .tmp criado → renamed atomically
- ✅ Diretórios criados automaticamente se não existem
- ✅ IOError com contexto claro se escrita falhar
- ✅ Logs INFO estruturados: "Exported X questions to path/to/file.xlsx"
- ✅ Headers em negrito (formatação básica aplicada)
- ✅ Zero questões com status != 'approved' no Excel final
- ✅ `ruff check` passa com zero warnings
- ✅ 100% cobertura de testes (mínimo 11 tests)

## Technical Requirements

### Core Technologies

| Tecnologia | Versão | Propósito | Documentação |
|-----------|---------|-----------|--------------|
| **pandas** | 3.0.0+ | Criação de DataFrame e escrita Excel | [pandas.DataFrame.to_excel](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html) |
| **openpyxl** | 3.1.5+ | Engine para escrita .xlsx + formatação | [openpyxl Docs](https://openpyxl.readthedocs.io/) |
| **SQLite** | 3.x (stdlib) | Leitura de questões aprovadas | [sqlite3 Docs](https://docs.python.org/3/library/sqlite3.html) |
| **pathlib** | Python 3.11+ stdlib | Manipulação de paths e diretórios | [Pathlib Docs](https://docs.python.org/3/library/pathlib.html) |

### pandas DataFrame.to_excel() Latest Best Practices (2026)

**Basic Usage Pattern:**
```python
import pandas as pd
from pathlib import Path

# Create DataFrame from SQLite query result
df = pd.DataFrame(questions_data, columns=COLUMN_ORDER)

# Write to Excel with openpyxl engine
df.to_excel(
    output_path,
    engine='openpyxl',
    index=False,           # Don't write row numbers
    sheet_name='Questões', # Named sheet (not 'Sheet1')
    freeze_panes=(1, 0),   # Freeze header row (optional)
)
```

**Critical Parameters for Our Use Case:**

1. **engine='openpyxl'** - Explicit backend (pandas 3.0 requires this for .xlsx)
2. **index=False** - Suppress row index column (we want exactly 26 columns)
3. **sheet_name='Questões'** - Descriptive sheet name (not default 'Sheet1')
4. **freeze_panes=(1,0)** - Freeze header row for better UX (optional enhancement)

**Column Order Enforcement:**

Pandas preserves DataFrame column order when writing to Excel. Critical pattern:

```python
# ALWAYS define column order explicitly
COLUMN_ORDER = [
    'tema', 'foco', 'sub_foco', 'periodo', 'nivel_dificuldade',
    'tipo_enunciado', 'enunciado', 'alternativa_a', 'alternativa_b',
    'alternativa_c', 'alternativa_d', 'resposta_correta',
    'objetivo_educacional', 'comentario_introducao',
    'comentario_visao_especifica', 'comentario_alt_a',
    'comentario_alt_b', 'comentario_alt_c', 'comentario_alt_d',
    'comentario_visao_aprovado', 'referencia_bibliografica',
    'suporte_imagem', 'fonte_imagem', 'modelo_llm',
    'rodadas_validacao', 'concordancia_comentador'
]

# Ensure DataFrame columns match order
df = df[COLUMN_ORDER]  # Reorder columns before write
```

### openpyxl 3.1.5+ Integration

**Pandas + openpyxl Two-Step Pattern:**

Story 1.5 (Excel Reader) used pandas alone. Story 1.6 requires **formatting**, which needs openpyxl directly.

```python
from openpyxl import load_workbook
from openpyxl.styles import Font

# Step 1: Write with pandas
df.to_excel(temp_path, engine='openpyxl', index=False)

# Step 2: Format with openpyxl
wb = load_workbook(temp_path)
ws = wb.active

# Make header row bold
for cell in ws[1]:  # First row
    cell.font = Font(bold=True)

# Save formatted workbook
wb.save(temp_path)
wb.close()
```

**Why Two Steps:**
- pandas handles data → Excel conversion efficiently
- openpyxl handles formatting (bold, widths, colors) after write

**Column Width Auto-Adjustment (Optional Enhancement):**

```python
from openpyxl.utils import get_column_letter

for col in ws.columns:
    max_length = 0
    column = col[0].column_letter  # Get column letter (A, B, C, ...)

    for cell in col:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))

    adjusted_width = min(max_length + 2, 50)  # Cap at 50 chars
    ws.column_dimensions[column].width = adjusted_width
```

### Atomic File Writing Pattern (NFR12)

**Critical for Resiliência:**

If script crashes during Excel write, file can be corrupted. Atomic pattern prevents this:

```python
import os
from pathlib import Path

def export_to_excel(self, output_path: str) -> None:
    """Export approved questions to Excel with atomic write."""
    output_file = Path(output_path)
    temp_file = output_file.with_suffix('.tmp')  # foo.xlsx → foo.tmp

    try:
        # Step 1: Write to temporary file
        df.to_excel(temp_file, engine='openpyxl', index=False)

        # Step 2: Format temporary file
        wb = load_workbook(temp_file)
        # ... apply formatting ...
        wb.save(temp_file)
        wb.close()

        # Step 3: Atomic rename (all-or-nothing operation)
        os.replace(temp_file, output_file)  # Atomic on POSIX and Windows

    except Exception:
        # Step 4: Cleanup temp file on error
        if temp_file.exists():
            temp_file.unlink()
        raise
```

**Why os.replace() instead of os.rename():**
- `os.replace()` is atomic on both Linux/macOS and Windows
- `os.rename()` can fail if destination exists on Windows
- `os.replace()` overwrites destination atomically if it exists

### SQLite Query Pattern

**Loading Approved Questions:**

```python
import sqlite3
import pandas as pd

def _load_approved_questions(self, limit: Optional[int] = None) -> pd.DataFrame:
    """Load approved questions from SQLite."""
    conn = sqlite3.connect('output/pipeline_state.db')

    query = "SELECT * FROM questions WHERE status='approved'"
    if limit:
        query += f" LIMIT {limit}"

    df = pd.read_sql_query(query, conn, index_col='id')
    conn.close()

    return df
```

**Column Mapping (SQLite → Excel):**

SQLite table `questions` has same column names as Excel (both in Portuguese), so mapping is direct. No transformation needed:

```python
# COLUMN_ORDER matches both SQLite schema AND Excel headers
# This was intentional design from Story 1.2 (Pydantic models)
```

### Directory Creation Pattern

**Ensure parent directory exists:**

```python
from pathlib import Path

output_file = Path(output_path)
output_file.parent.mkdir(parents=True, exist_ok=True)  # Create if doesn't exist
```

**Why parents=True:**
- Creates all intermediate directories (e.g., `output/batches/final.xlsx` creates both `output/` and `output/batches/`)

**Why exist_ok=True:**
- Doesn't raise error if directory already exists (idempotent)

### Error Handling Patterns

**SQLite Errors:**
```python
import sqlite3

try:
    df = self._load_approved_questions()
except sqlite3.Error as e:
    logger.error(f"Failed to load questions from SQLite: {e}")
    raise IOError(f"Database error: {e}") from e
```

**Pandas/openpyxl Errors:**
```python
try:
    df.to_excel(temp_path, engine='openpyxl', index=False)
except Exception as e:
    logger.error(f"Failed to write Excel to {temp_path}: {e}")
    raise IOError(f"Excel write failed: {e}") from e
```

**Permission Errors:**
```python
try:
    os.replace(temp_file, output_file)
except PermissionError as e:
    logger.error(f"Permission denied writing to {output_file}: {e}")
    raise IOError(f"Cannot write to {output_file}: {e}") from e
```

### Performance Considerations

**For MVP (~8,000 questões):**
- pandas handles 8K rows trivially (<1 second for DataFrame.to_excel)
- openpyxl formatting adds ~1-2 seconds for 8K rows
- Total export time: <5 seconds for full Excel

**No optimization needed** - this is not a performance bottleneck.

**For Future Scale (50K+ questões):**
```python
# If needed: Write in chunks
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    for chunk in pd.read_sql_query(query, conn, chunksize=5000):
        chunk.to_excel(writer, index=False, header=(chunk_num == 0))
```

**For This Story:** Simple full-file write is sufficient.

## Architecture Compliance

### Naming Conventions (CRITICAL - Must Follow Exactly)

**Fonte:** [Architecture Doc - Naming Patterns](../../_bmad-output/planning-artifacts/architecture.md#naming-patterns)

| Elemento | Convenção | Exemplos | Idioma |
|---------|-----------|----------|--------|
| **Módulo/arquivo** | snake_case | `excel_writer.py` | Inglês |
| **Classes** | PascalCase | `ExcelWriter`, `QuestionRecord` | Inglês |
| **Métodos** | snake_case | `export_to_excel()`, `_load_approved_questions()` | Inglês |
| **Variáveis** | snake_case | `output_path`, `df`, `temp_file` | Inglês |
| **Constantes** | UPPER_SNAKE_CASE | `COLUMN_ORDER`, `DEFAULT_SHEET_NAME` | Inglês |
| **Campos Pydantic (domínio)** | snake_case | `tema`, `foco`, `enunciado` | **Português** |

**IMPORTANTE:** Campos do Excel (26 colunas) estão em PORTUGUÊS para consistência com QuestionRecord Pydantic model e expectativa da equipe de importação.

### Mandatory Patterns from Architecture

**Fonte:** [Architecture Doc - Process Patterns](../../_bmad-output/planning-artifacts/architecture.md#process-patterns)

**1. Exception Handling (MUST USE):**
```python
# ✅ CORRECT: Use IOError for file operations
if not output_file.parent.exists():
    output_file.parent.mkdir(parents=True, exist_ok=True)

try:
    df.to_excel(temp_path, engine='openpyxl', index=False)
except Exception as e:
    raise IOError(f"Failed to write Excel: {e}") from e

# ❌ WRONG: Never use bare Exception
if error:
    raise Exception("Error")  # DON'T DO THIS
```

**2. Logging Pattern (MUST FOLLOW):**
```python
import logging
logger = logging.getLogger(__name__)

# ✅ CORRECT: Structured logging with context
logger.info(f"Loading approved questions from SQLite")
logger.info(f"Successfully exported {len(df)} questions to {output_path}")
logger.error(f"Failed to write Excel to {output_path}: {error}")

# ❌ WRONG: No logging or print statements
print("Writing file...")  # DON'T DO THIS
```

**Log Levels:**
- `INFO` - File write started, questions loaded, export successful
- `ERROR` - SQLite query failed, Excel write failed, permission denied
- `WARNING` - No approved questions to export (empty DataFrame)

**3. Type Hints (MANDATORY):**
```python
from pathlib import Path
from typing import Optional
import pandas as pd

# ✅ CORRECT: Full type hints
def export_to_excel(self, output_path: str, limit: Optional[int] = None) -> None:
    """Export approved questions to Excel."""
    pass

def _load_approved_questions(self, limit: Optional[int] = None) -> pd.DataFrame:
    """Load approved questions from SQLite."""
    pass

# ❌ WRONG: No type hints
def export_to_excel(self, output_path):  # DON'T DO THIS
    pass
```

**4. Docstrings (MANDATORY - Google Style):**
```python
def export_to_excel(self, output_path: str, limit: Optional[int] = None) -> None:
    """
    Export approved questions to Excel with atomic write.

    Loads all questions with status='approved' from SQLite, creates a DataFrame
    with 26 columns in correct order, and writes to Excel with formatting.
    Uses atomic write pattern (temp file + rename) to prevent corruption.

    Args:
        output_path: Path to output Excel file (.xlsx format)
        limit: Optional maximum number of questions to export (for testing)

    Raises:
        IOError: If database query fails, Excel write fails, or permission denied
        ValueError: If output_path is not .xlsx extension

    Example:
        >>> writer = ExcelWriter()
        >>> writer.export_to_excel("output/final.xlsx")
        INFO: Successfully exported 8432 questions to output/final.xlsx
    """
```

### Anti-Patterns (STRICTLY FORBIDDEN)

**Fonte:** [Architecture Doc - Anti-Patterns](../../_bmad-output/planning-artifacts/architecture.md#anti-patterns-proibidos)

```python
# ❌ ANTI-PATTERN 1: Non-atomic write
df.to_excel(output_path)  # DON'T DO THIS - can corrupt on crash
# ✅ CORRECT: Atomic write with temp file
df.to_excel(temp_path)
os.replace(temp_path, output_path)


# ❌ ANTI-PATTERN 2: Vague error messages
if error:
    raise IOError("Write failed")  # DON'T DO THIS
# ✅ CORRECT: Specific error messages with context
raise IOError(
    f"Failed to write Excel to {output_path}: {error}. "
    f"Attempted to export {len(df)} questions."
)


# ❌ ANTI-PATTERN 3: Ignoring empty results
df = load_questions()
df.to_excel(output_path)  # DON'T DO THIS - fails silently if df is empty
# ✅ CORRECT: Explicit validation with clear messaging
if df.empty:
    logger.warning("No approved questions found - nothing to export")
    return  # Or raise ValueError depending on requirements


# ❌ ANTI-PATTERN 4: Using print instead of logging
print("Exporting...")  # DON'T DO THIS
# ✅ CORRECT: Structured logging
logger.info(f"Exporting {len(df)} questions to {output_path}")
```

## Library & Framework Requirements

### pandas 3.0.0+ (Latest 2026)

**Installation:** Already in dependencies via Story 1.1

**Key Imports:**
```python
import pandas as pd
from pandas import DataFrame
```

**Critical Features for This Story:**
- `pd.read_sql_query()` - Load SQLite results into DataFrame
- `DataFrame.to_excel()` - Main export function
- `engine='openpyxl'` - MUST specify for .xlsx files
- `index=False` - Suppress row numbers

**Latest Best Practice (2026):**

Pandas 3.0 uses Apache Arrow backend for better performance, openpyxl remains standard for Excel I/O.

```python
# ✅ CORRECT: Explicit engine + suppress index
df.to_excel(output_path, engine='openpyxl', index=False)

# ⚠️ AVOID: Implicit engine (works but not explicit)
df.to_excel(output_path)
```

**Sources:**
- [pandas.DataFrame.to_excel Documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html)

### openpyxl 3.1.5+ (Latest 2026)

**Installation:** Already in dependencies via Story 1.1

**Role:** Backend for pandas.to_excel() + formatting after write

**When to Import openpyxl Directly:**

Story 1.5 used pandas alone. Story 1.6 REQUIRES openpyxl directly for formatting:

```python
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

# Load Excel written by pandas
wb = load_workbook(temp_path)
ws = wb.active

# Apply formatting
for cell in ws[1]:  # Header row
    cell.font = Font(bold=True)

wb.save(temp_path)
wb.close()
```

**Performance (openpyxl 3.1.5):**
- 15-20% faster than 3.0.x
- Better memory efficiency for large files
- Improved error messages for corrupted files

**Sources:**
- [openpyxl Documentation](https://openpyxl.readthedocs.io/en/stable/)
- [Working with Excel Formatting](https://openpyxl.readthedocs.io/en/stable/styles.html)

### SQLite Integration

**Database Location:** `output/pipeline_state.db` (created by Story 1.4)

**Query Pattern:**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('output/pipeline_state.db')
df = pd.read_sql_query(
    "SELECT * FROM questions WHERE status='approved' ORDER BY id",
    conn
)
conn.close()
```

**Expected Schema (from Story 1.4):**

Table `questions` with 26+ columns matching COLUMN_ORDER:
- tema, foco, sub_foco, periodo, nivel_dificuldade, ...
- status (TEXT) - filter by 'approved'
- id (INTEGER PRIMARY KEY) - order by for consistency

### Testing Dependencies

**pytest Fixtures for Excel Testing:**
```python
import pytest
import pandas as pd
import sqlite3
from pathlib import Path

@pytest.fixture
def sample_approved_questions(tmp_path):
    """Create SQLite DB with sample approved questions."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create questions table (subset of columns for test)
    cursor.execute("""
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY,
            tema TEXT,
            foco TEXT,
            sub_foco TEXT,
            periodo TEXT,
            status TEXT
            -- ... additional columns ...
        )
    """)

    # Insert sample data
    cursor.execute("""
        INSERT INTO questions (tema, foco, sub_foco, periodo, status)
        VALUES ('Cardiologia', 'ICC', 'Diagnóstico', '3º ano', 'approved')
    """)
    conn.commit()
    conn.close()

    return db_path

@pytest.fixture
def output_excel_path(tmp_path):
    """Provide temporary path for Excel output."""
    return tmp_path / "output.xlsx"
```

## File Structure Requirements

### Files to Create

```
src/construtor/io/
├── __init__.py                    # Export ExcelWriter
├── excel_reader.py                # ✅ Exists (Story 1.5)
└── excel_writer.py                # ExcelWriter implementation (THIS STORY)

tests/test_io/
├── __init__.py                    # ✅ Exists
├── test_excel_reader.py           # ✅ Exists (Story 1.5)
└── test_excel_writer.py           # Comprehensive tests (11+ tests)
```

### ExcelWriter Public API

```python
from pathlib import Path
from typing import Optional
import pandas as pd

class ExcelWriter:
    """Excel output file writer with atomic write and formatting."""

    COLUMN_ORDER = [
        'tema', 'foco', 'sub_foco', 'periodo', 'nivel_dificuldade',
        'tipo_enunciado', 'enunciado', 'alternativa_a', 'alternativa_b',
        'alternativa_c', 'alternativa_d', 'resposta_correta',
        'objetivo_educacional', 'comentario_introducao',
        'comentario_visao_especifica', 'comentario_alt_a',
        'comentario_alt_b', 'comentario_alt_c', 'comentario_alt_d',
        'comentario_visao_aprovado', 'referencia_bibliografica',
        'suporte_imagem', 'fonte_imagem', 'modelo_llm',
        'rodadas_validacao', 'concordancia_comentador'
    ]

    DEFAULT_SHEET_NAME = "Questões"

    def __init__(self, db_path: str = "output/pipeline_state.db"):
        """
        Initialize ExcelWriter.

        Args:
            db_path: Path to SQLite database
        """
        ...

    def export_to_excel(
        self,
        output_path: str,
        limit: Optional[int] = None
    ) -> None:
        """
        Export approved questions to Excel with atomic write.

        Args:
            output_path: Path to output Excel file (.xlsx)
            limit: Optional max questions to export (for testing/debugging)

        Raises:
            IOError: If database query fails, write fails, or permission denied
            ValueError: If output_path is not .xlsx extension
        """
        ...

    def _load_approved_questions(
        self,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Load approved questions from SQLite."""
        ...

    def _create_output_directory(self, output_path: Path) -> None:
        """Create parent directory if doesn't exist."""
        ...

    def _write_excel_with_formatting(
        self,
        df: pd.DataFrame,
        temp_path: Path
    ) -> None:
        """Write DataFrame to Excel and apply formatting."""
        ...

    def _apply_header_formatting(self, temp_path: Path) -> None:
        """Apply bold formatting to header row."""
        ...
```

## Testing Requirements

### Test Coverage Checklist

**tests/test_io/test_excel_writer.py deve incluir:**

1. **Happy Path Tests (3 tests)**
   - [ ] Test export with sample approved questions
   - [ ] Test all 26 columns present in correct order
   - [ ] Test header row is bold

2. **Atomic Write Tests (2 tests)**
   - [ ] Test temporary file is created during write
   - [ ] Test atomic rename (temp → final)

3. **Directory Creation Tests (2 tests)**
   - [ ] Test parent directory created if doesn't exist
   - [ ] Test nested directory creation (parents=True)

4. **Status Filtering Tests (2 tests)**
   - [ ] Test only 'approved' questions exported
   - [ ] Test 'pending'/'rejected' questions excluded

5. **Error Handling Tests (3 tests)**
   - [ ] Test IOError when SQLite database doesn't exist
   - [ ] Test IOError on write permission denied
   - [ ] Test ValueError for non-.xlsx extension

6. **Edge Cases (3 tests)**
   - [ ] Test export with empty result (no approved questions)
   - [ ] Test export with LIMIT parameter (partial export)
   - [ ] Test cleanup of temp file on write failure

7. **Integration Test (1 test)**
   - [ ] Test end-to-end: SQLite → DataFrame → Excel → verify columns

**Total: ~15 tests mínimo**

### Test Pattern Example

```python
import pytest
from construtor.io import ExcelWriter
import sqlite3
from pathlib import Path
import pandas as pd

def test_export_approved_questions(sample_approved_questions, output_excel_path):
    """Test exporting approved questions to Excel."""
    # Arrange
    writer = ExcelWriter(db_path=str(sample_approved_questions))

    # Act
    writer.export_to_excel(str(output_excel_path))

    # Assert
    assert output_excel_path.exists()
    df = pd.read_excel(output_excel_path, engine='openpyxl')
    assert len(df) == 1  # 1 approved question
    assert 'tema' in df.columns
    assert df['tema'][0] == 'Cardiologia'

def test_atomic_write_creates_temp_file(sample_approved_questions, output_excel_path, mocker):
    """Test atomic write pattern uses temporary file."""
    # Arrange
    writer = ExcelWriter(db_path=str(sample_approved_questions))

    # Mock to capture temp file creation
    original_to_excel = pd.DataFrame.to_excel
    temp_files_created = []

    def mock_to_excel(self, path, **kwargs):
        temp_files_created.append(Path(path))
        return original_to_excel(self, path, **kwargs)

    mocker.patch.object(pd.DataFrame, 'to_excel', mock_to_excel)

    # Act
    writer.export_to_excel(str(output_excel_path))

    # Assert
    assert any(str(p).endswith('.tmp') for p in temp_files_created)
    assert output_excel_path.exists()  # Temp file renamed to final

def test_error_when_database_not_found(output_excel_path):
    """Test IOError when SQLite database doesn't exist."""
    # Arrange
    writer = ExcelWriter(db_path="nonexistent.db")

    # Act & Assert
    with pytest.raises(IOError) as exc_info:
        writer.export_to_excel(str(output_excel_path))

    assert "database" in str(exc_info.value).lower()
```

## Previous Story Intelligence (Story 1.5)

### Principais Aprendizados da Implementação da Story 1.5

**✅ Qualidade de Código Estabelecida:**
- 17 testes criados e 100% passando (Story 1.5 - Excel Reader)
- Zero erros ruff após implementação desde o início
- Pattern de commit message estabelecido com Co-Authored-By tag
- Code review corrections aplicadas antes do commit final

**✅ Patterns Técnicos Validados:**
- pandas 3.0 + openpyxl 3.1.5 funcionam perfeitamente para Excel I/O
- Exception handling com IOError (deve ser usado aqui também)
- Logging estruturado com logger = logging.getLogger(__name__)
- Type hints completos em todos os métodos públicos
- Docstrings no estilo Google (Args/Returns/Raises)

**✅ Arquivos Prontos para Reutilização:**
- `src/construtor/io/excel_reader.py` → ExcelReader class (pattern reference)
- `src/construtor/io/__init__.py` → Export pattern established
- `src/construtor/models/question.py` → FocoInput, QuestionRecord models
- `src/construtor/config/exceptions.py` → ValidationError, OutputParsingError
- `tests/test_io/test_excel_reader.py` → Testing pattern reference
- `.ruff.toml` → Configurado e validado

**✅ Lições Aplicáveis à Story 1.6:**

1. **Pandas + openpyxl Integration:** Story 1.5 usou `pd.read_excel(engine='openpyxl')`. Story 1.6 usa `df.to_excel(engine='openpyxl')` - mesmo pattern
2. **Structured Logging:** logger.info() para sucesso, logger.error() para falhas - aplicar idêntico
3. **Exception Hierarchy:** Story 1.5 usou ValidationError e OutputParsingError. Story 1.6 usa IOError para file operations
4. **ClassVar Annotations:** Necessário para constantes de classe (COLUMN_ORDER, DEFAULT_SHEET_NAME)
5. **File Extension Validation:** Story 1.5 validou .xlsx/.xlsm - Story 1.6 deve validar output_path.endswith('.xlsx')
6. **Comprehensive Tests:** Story 1.5 teve 17 testes - Story 1.6 deve ter ~15 tests
7. **Ruff Early:** Rodar `ruff check` desde o início evita acúmulo de warnings

**✅ Padrões Estabelecidos para Story 1.6:**
- Usar mesmo padrão de testes: pytest fixtures com temp paths
- Seguir mesmo nível de documentação (docstrings completas)
- Aplicar ruff desde o início (não acumular warnings)
- Documentar completion notes durante implementação
- File list deve distinguir CRIADO/MODIFICADO/REUTILIZADO
- Commits com mensagem detalhada + Co-Authored-By tag

**🔗 Conexão Direta com Story 1.6:**
- ExcelWriter espelhará ExcelReader: mesma estrutura de classe, logging pattern, error handling
- COLUMN_ORDER constant (26 columns) mapeará diretamente para QuestionRecord fields
- Testing pattern será idêntico: fixtures, 100% coverage, ruff zero warnings
- Atomic write (temp + rename) será nova técnica não presente em Story 1.5

**⚠️ Atenção Especial:**

Story 1.5 usou pandas ONLY (no direct openpyxl imports). Story 1.6 REQUIRES openpyxl directly for formatting (bold headers). Essa é a principal diferença técnica.

Story 1.5 validou INPUT data. Story 1.6 garante OUTPUT atomicity (NFR12) - escrita atômica é crítica para resiliência.

## Git Intelligence Summary

### Análise dos Commits Recentes

**Commit c1cf70d (Mais Recente - Story 1.5 with corrections):**
```
feat: implementar leitor de Excel de input com validação e code review corrections

Implementa ExcelReader para importar temas, focos e períodos acadêmicos:
- Leitura com pandas 3.0 + openpyxl 3.1.5 engine
- Validação de colunas obrigatórias (case-insensitive, whitespace handling)
- Validação de período acadêmico (apenas 1º-4º ano aceitos)
- Validação de extensão de arquivo (.xlsx/.xlsm apenas)
- Detecção de dados faltantes com números de linha Excel
- Conversão para FocoInput Pydantic models com validação row-level
- 17 testes com 100% coverage (todos passando)

Code review corrections aplicadas:
- Performance optimization: seleção de colunas após normalização
- File extension validation para mensagens de erro mais claras
- Import sorting corrigido (ruff I001)
- Teste adicional para arquivos Excel corrompidos
- Documentação atualizada (File List, line count, BOM clarification)

Qualidade de código:
- Ruff check passa com 0 warnings
- Type hints completos em todos os métodos
- Exception handling com ValidationError/OutputParsingError
- Logging estruturado (INFO/ERROR) conforme arquitetura
- Documentação completa com docstrings Google-style

Story 1.5 completa e aprovada (status: done).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Files Modified in c1cf70d:**
- src/construtor/io/excel_reader.py (CRIADO - 256 lines)
- tests/test_io/test_excel_reader.py (CRIADO - 630+ lines)
- tests/test_io/__init__.py (CRIADO)
- src/construtor/io/__init__.py (MODIFICADO - export ExcelReader)
- src/construtor/models/question.py (MODIFICADO - added FocoInput)
- src/construtor/config/exceptions.py (MODIFICADO - added ValidationError)
- _bmad-output/implementation-artifacts/sprint-status.yaml (MODIFICADO - status done)

**Padrões Identificados:**

1. **Estrutura de Commit:** Mensagem detalhada com seções (Implementa, Code review, Qualidade) + Co-Authored-By
2. **Test Coverage:** 17 testes, 100% passing - benchmark para Story 1.6
3. **Story Updates:** Story markdown file sempre atualizado com status e completion notes
4. **Code Quality:** Ruff check com 0 warnings antes do commit
5. **Documentation:** Completion notes distinguem CRIADO/MODIFICADO/REUTILIZADO

### Insights Acionáveis para Story 1.6

**1. Estrutura de Diretório Já Estabelecida:**
```
src/construtor/io/       ✅ Exists
├── __init__.py          ✅ Exists (export ExcelReader)
├── excel_reader.py      ✅ Exists (Story 1.5)
└── excel_writer.py      ← Story 1.6 vai aqui (CRIADO)

tests/test_io/           ✅ Exists
├── __init__.py          ✅ Exists
├── test_excel_reader.py ✅ Exists (Story 1.5)
└── test_excel_writer.py ← Story 1.6 tests aqui (CRIADO)
```

**2. Pattern de Dependências:**
- Story 1.6 pode importar de `construtor.config.exceptions` (IOError ou custom exception)
- Story 1.6 pode importar de `construtor.models.question` (QuestionRecord)
- Story 1.6 usa mesma tabela `questions` do SQLite (Story 1.4)
- pandas + openpyxl já instalados e validados (Story 1.1, 1.5)

**3. Convenções de Código:**
- Seguir PEP 8 rigorosamente (validado por ruff)
- Docstrings completas em estilo Google
- Type hints em TODOS os métodos públicos
- ClassVar para constantes de classe (COLUMN_ORDER, DEFAULT_SHEET_NAME)

**4. Testing Strategy:**
- Criar tests/test_io/test_excel_writer.py
- Usar pytest fixtures (tmp_path, sample SQLite DB)
- Mínimo 15 testes (baseado em análise de cobertura)
- Validar com `uv run pytest tests/test_io/` antes de commit

**5. Commit Message Template para Story 1.6:**
```
feat: implementar escritor de Excel de output com escrita atômica

Implementa ExcelWriter para exportar questões aprovadas:
- Leitura de questões com status='approved' do SQLite
- Criação de DataFrame com 26 colunas na ordem correta
- Escrita atômica (temp file + rename) para prevenir corrupção (NFR12)
- Formatação básica (headers em negrito) via openpyxl
- Auto-criação de diretórios se não existem
- 15 testes com 100% coverage (todos passando)

Qualidade de código:
- Ruff check passa com 0 warnings
- Type hints completos em todos os métodos
- Exception handling com IOError para file operations
- Logging estruturado (INFO/ERROR) conforme arquitetura
- Documentação completa com docstrings Google-style

Story 1.6 completa e aprovada (status: ready-for-dev).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Latest Tech Information (2026)

### pandas 3.0.0 (Latest Release - Feb 2026)

**Versão Atual:** pandas 3.0.0 with Apache Arrow backend

**Principais Features para Excel I/O:**
- **Apache Arrow Backend:** Melhoria de performance (~30% mais rápido)
- **DataFrame.to_excel() Enhancements:** Melhor error handling, suporte a freeze_panes
- **Improved Memory Efficiency:** Menor uso de RAM para grandes DataFrames

**Critical Parameters for Excel Output (2026):**
```python
df.to_excel(
    output_path,
    engine='openpyxl',     # REQUIRED for .xlsx in pandas 3.0
    index=False,           # Suppress row numbers
    sheet_name='Questões', # Custom sheet name (not 'Sheet1')
    freeze_panes=(1, 0),   # Optional: freeze header row
)
```

**New in pandas 3.0:**
- `freeze_panes` parameter for better UX (freeze header row while scrolling)
- Better error messages when openpyxl is missing
- Automatic dtype inference improvements

**Sources:**
- [pandas 3.0.0 Documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html)
- [What's New in pandas 3.0](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)

### openpyxl 3.1.5 (Latest Stable - 2026)

**Versão Atual:** openpyxl 3.1.5

**Performance Improvements (vs 3.0.x):**
- 15-20% faster write operations
- Better memory efficiency for large files
- Improved error messages for corrupted Excel files

**Latest Formatting Patterns (2026):**

```python
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

wb = load_workbook(temp_path)
ws = wb.active

# Bold headers (REQUIRED for this story)
for cell in ws[1]:
    cell.font = Font(bold=True)

# Optional enhancements (not required for MVP)
for cell in ws[1]:
    cell.alignment = Alignment(horizontal='center')

# Auto-width columns (optional)
for col in ws.columns:
    max_length = max(len(str(cell.value)) for cell in col if cell.value)
    ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)

wb.save(temp_path)
wb.close()
```

**Critical for Story 1.6:**
- Must import openpyxl directly for formatting (pandas alone doesn't format)
- Use `Font(bold=True)` for header row
- Always close workbook after save to prevent file locks

**Sources:**
- [openpyxl 3.1.5 Documentation](https://openpyxl.readthedocs.io/en/stable/)
- [Styling Cells](https://openpyxl.readthedocs.io/en/stable/styles.html)

### Atomic File Operations (os.replace)

**Latest Best Practice (2026):**

`os.replace()` is the recommended atomic rename operation across platforms:

```python
import os
from pathlib import Path

# ✅ CORRECT: Atomic rename (POSIX and Windows)
os.replace(temp_file, output_file)

# ❌ AVOID: os.rename() can fail on Windows if destination exists
os.rename(temp_file, output_file)  # May raise FileExistsError on Windows

# ❌ AVOID: shutil.move() is not atomic
shutil.move(temp_file, output_file)  # Not atomic - can corrupt on crash
```

**Why os.replace():**
- Atomic operation on both Linux/macOS and Windows
- Overwrites destination if exists (no FileExistsError)
- All-or-nothing: either completes fully or fails entirely (no partial writes)
- Critical for NFR12 (crash não corrompe Excel parcial)

**Sources:**
- [Python os.replace Documentation](https://docs.python.org/3/library/os.html#os.replace)
- [Atomic File Operations in Python](https://alexwlchan.net/2019/03/atomic-cross-platform-writes/)

## Project Structure Notes

### Alignment with Unified Project Structure

**100% Compliant with Architecture Document:**
- ✅ Follows [io/ module structure](../../_bmad-output/planning-artifacts/architecture.md#complete-project-directory-structure)
- ✅ Implements [Excel output writing](../../_bmad-output/planning-artifacts/architecture.md#output-e-exportação)
- ✅ Uses [atomic writes for resiliência](../../_bmad-output/planning-artifacts/architecture.md#resiliência)
- ✅ Uses [snake_case naming](../../_bmad-output/planning-artifacts/architecture.md#naming-patterns)
- ✅ Implements [Boundary 3: Pipeline ↔ IO](../../_bmad-output/planning-artifacts/architecture.md#architectural-boundaries)

**Critical for Future Stories:**
- Story 2.8 (Pipeline Orchestrator) chamará ExcelWriter.export_to_excel() para salvar questões aprovadas
- Story 3.1 (Batch Processor) usará export com LIMIT para checkpoints parciais
- Story 3.6 (Exportação Final) usará export sem LIMIT para Excel completo
- Epic 3 inteiro depende de escrita atômica confiável (NFR12)

**Detected Conflicts:** Nenhum - implementação greenfield alinhada com arquitetura

### References

**Architecture Documentation:**
- [IO Module Structure](../../_bmad-output/planning-artifacts/architecture.md#complete-project-directory-structure) - Lines 468-473
- [Atomic Writes Pattern](../../_bmad-output/planning-artifacts/architecture.md#resiliência) - NFR12
- [Boundary 3: Pipeline ↔ IO](../../_bmad-output/planning-artifacts/architecture.md#architectural-boundaries) - Lines 540-545

**Requirements Documentation:**
- [PRD - Output e Exportação](../../_bmad-output/planning-artifacts/prd.md#output-e-exportação) - FR23, FR25
- [Epics - Story 1.6](../../_bmad-output/planning-artifacts/epics.md#story-16-implementar-escritor-de-excel-de-output) - Lines 300-318

**Related Stories:**
- [Story 1.1 - Project Init](./1-1-inicializar-projeto-e-estrutura-base.md) - Completada (dependências instaladas)
- [Story 1.2 - Pydantic Models](./1-2-criar-modelos-pydantic-de-dados.md) - Completada (QuestionRecord com 26 campos)
- [Story 1.4 - SQLite Store](./1-4-configurar-sqlite-para-persistencia-de-estado.md) - Completada (tabela questions)
- [Story 1.5 - Excel Reader](./1-5-implementar-leitor-de-excel-de-input.md) - Completada (padrão pandas/openpyxl)
- Story 2.8 - Pipeline Orchestrator (bloqueada por esta story - usa ExcelWriter)
- Story 3.1 - Batch Processor (bloqueada por esta story - usa export parcial)
- Story 3.6 - Exportação Final (bloqueada por esta story - usa export completo)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

N/A - Implementation completed successfully without major issues

### Completion Notes List

✅ **Task 1-10 Completed (2026-02-07):**
- Created ExcelWriter class with atomic write pattern using temp file + os.replace()
- Implemented SQLite data loading with status='approved' filtering
- Created DataFrame with all 26 columns in correct order matching COLUMN_ORDER constant
- Applied bold header formatting using openpyxl after pandas write
- Implemented automatic directory creation with pathlib.Path.mkdir(parents=True, exist_ok=True)
- Comprehensive error handling with OSError (replaced IOError per ruff UP024)
- Structured logging using logging.exception() for better error context (per ruff TRY400)
- Created 13 comprehensive tests covering happy path, atomic write, directory creation, status filtering, error handling, and edge cases
- All 161 tests passing (13 new + 148 existing) with zero regressions
- Ruff check passes with zero warnings after applying fixes:
  - Added ClassVar annotations for COLUMN_ORDER and DEFAULT_SHEET_NAME (RUF012)
  - Added return type annotation for __init__ (ANN204)
  - Replaced Optional[X] with X | None (UP045)
  - Replaced IOError with OSError (UP024)
  - Replaced logging.error with logging.exception (TRY400)
  - Removed unused exception variable (F841)

**Technical Highlights:**
- Atomic write pattern prevents file corruption on crash (NFR12 compliance)
- COLUMN_ORDER enforces exact 26-column structure for stakeholder integration
- Empty result handling creates Excel with headers only (graceful degradation)
- LIMIT parameter enables partial exports for testing and debugging
- openpyxl 3.1.5 used directly for formatting (pandas alone doesn't format)
- os.replace() used for atomic rename (cross-platform compatible)

**Quality Metrics:**
- 13 tests created, 100% passing
- 161 total tests passing (zero regressions)
- Ruff check: 0 warnings
- Code coverage: Complete for ExcelWriter module
- TDD approach: Tests written before implementation

### Code Review Notes (AI)

✅ **Code Review Completed (2026-02-07):**

Adversarial code review identified and fixed 10 issues:

**CRITICAL/HIGH Issues Fixed (2):**
1. **Double Cleanup Bug (CRITICAL)** - Fixed duplicate temp file cleanup in except+finally blocks that could cause FileNotFoundError. Solution: Removed cleanup from except, kept only in finally block.
2. **Silent Missing Columns (HIGH)** - Added validation to ensure all 26 required columns are present in database. Now raises ValueError with clear message if columns are missing, preventing silent data corruption.

**MEDIUM Issues Fixed (5):**
3. **Docstring IOError→OSError** - Updated docstring to reflect actual OSError exceptions (was incorrectly documented as IOError after UP024 fix).
4. **SQL Injection Prevention** - Converted f-string query to parameterized query with placeholders (?) to prevent SQL injection via limit parameter.
5. **Missing Columns Test** - Added test_error_when_required_column_missing to validate that ValueError is raised when database schema is incomplete.
6. **Column Count Validation Tests** - Added 2 tests (test_column_order_has_exactly_26_columns, test_column_order_has_no_duplicates) to validate COLUMN_ORDER constant integrity.
7. **ValueError Exception Handling** - Added explicit ValueError re-raise to prevent wrapping validation errors as OSError.

**LOW Issues Fixed (1):**
8. **Formatting Failure Logging** - Improved error logging in _apply_header_formatting to use logging.exception() with full stacktrace and clearer message.

**Ruff Warnings Fixed:**
- TRY203: Removed unnecessary except block that only re-raised
- TRY301: Added # noqa: TRY301 for legitimate ValueError raise in try block

**Test Results After Fixes:**
- 16 tests passing (13 original + 3 new validation tests)
- Ruff check: All checks passed!
- Zero regressions in existing functionality

**Files Modified During Review:**
- src/construtor/io/excel_writer.py (7 corrections applied)
- tests/test_io/test_excel_writer.py (3 new tests + 1 fixture update)

### File List

**CREATED:**
- src/construtor/io/excel_writer.py (245 lines) - ExcelWriter class with atomic write
- tests/test_io/test_excel_writer.py (490 lines) - 16 comprehensive tests

**MODIFIED:**
- src/construtor/io/__init__.py (2 lines added) - Export ExcelWriter
- _bmad-output/implementation-artifacts/sprint-status.yaml (1 line) - Status: ready-for-dev → in-progress → review
- _bmad-output/implementation-artifacts/1-6-implementar-escritor-de-excel-de-output.md (Tasks marked complete, Dev Agent Record updated)

**REUTILIZED:**
- src/construtor/models/question.py - QuestionRecord model (26 fields)
- output/pipeline_state.db - SQLite database with questions table
- .ruff.toml - Code quality configuration
- pyproject.toml - Project configuration with pandas/openpyxl dependencies

---

**Created:** 2026-02-07
**Epic:** 1 - Fundação do Projeto e Infraestrutura Core
**Priority:** CRITICAL - Bloqueia Story 2.8, Story 3.1, Story 3.6, todo o Epic 3
**Estimated Effort:** 2-3 horas
```
