# Construtor de Questões

Multi-agent pipeline for medical question generation using AI.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

3. Run tests:
```bash
uv run pytest
```

4. Run linter:
```bash
uv run ruff check .
```

## Project Structure

- `src/construtor/` - Main application code
  - `models/` - Pydantic data models
  - `agents/` - AI agents (Criador, Comentador, Validador)
  - `providers/` - LLM provider abstractions
  - `pipeline/` - Pipeline orchestration
  - `io/` - Input/Output (Excel, Pinecone)
  - `metrics/` - Metrics collection
  - `config/` - Configuration management
  - `dashboard/` - Streamlit dashboard
- `tests/` - Test suite
- `prompts/` - Agent prompt templates
- `data/` - Input Excel files (gitignored)
- `output/` - Output Excel files (gitignored)

## Requirements

- Python 3.11+
- OpenAI API key
- Anthropic API key
- Pinecone API key
