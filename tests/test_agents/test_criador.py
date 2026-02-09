"""Tests for CriadorAgent."""

from unittest.mock import AsyncMock, patch

import pytest

from construtor.agents.criador import CriadorAgent
from construtor.config.exceptions import OutputParsingError
from construtor.models.question import CriadorOutput, SubFocoInput


@pytest.fixture
def mock_config(monkeypatch: pytest.MonkeyPatch):
    """PipelineConfig with all necessary fields."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("PINECONE_API_KEY", "pc-test-key")
    monkeypatch.setenv("PINECONE_INDEX_HOST", "test-index.pinecone.io")

    # Reset settings singleton
    import construtor.config.settings as settings_module

    settings_module._settings = None

    from construtor.config.settings import PipelineConfig

    return PipelineConfig(_env_file=None)


@pytest.fixture
def mock_provider():
    """Mock LLMProvider that returns CriadorOutput."""
    provider = AsyncMock()
    output = CriadorOutput(
        enunciado="Paciente de 65 anos com dispneia aos esforços. Exame: estertores bibasais, B3. Qual diagnóstico?",
        alternativa_a="Pneumonia",
        alternativa_b="Insuficiência cardíaca",
        alternativa_c="DPOC",
        alternativa_d="Embolia pulmonar",
        resposta_correta="B",
        objetivo_educacional="Identificar sinais clínicos de insuficiência cardíaca descompensada",
        nivel_dificuldade=2,
        tipo_enunciado="caso clínico",
    )
    provider.generate.return_value = {
        "content": output,
        "tokens_used": 850,
        "cost": 0.0127,
        "latency": 1.85,
    }
    return provider


@pytest.fixture
def sample_subfoco():
    """SubFocoInput de exemplo."""
    return SubFocoInput(
        tema="Cardiologia",
        foco="Insuficiência Cardíaca",
        sub_foco="Diagnóstico clínico de IC descompensada",
        periodo="3º ano",
    )


# ============================================================================
# Model Validation Tests (1 test)
# ============================================================================


def test_criador_output_model_has_all_required_fields():
    """Test that CriadorOutput model has all fields required by AC #7."""
    from construtor.models.question import CriadorOutput
    import inspect

    # Get all fields from the model
    model_fields = CriadorOutput.model_fields

    # Required fields from AC #7
    required_fields = {
        "enunciado",
        "alternativa_a",
        "alternativa_b",
        "alternativa_c",
        "alternativa_d",
        "resposta_correta",
        "objetivo_educacional",
        "nivel_dificuldade",
        "tipo_enunciado",
    }

    # Verify all required fields exist
    actual_fields = set(model_fields.keys())
    assert required_fields == actual_fields, (
        f"CriadorOutput missing fields. "
        f"Expected: {required_fields}, Got: {actual_fields}, "
        f"Missing: {required_fields - actual_fields}, "
        f"Extra: {actual_fields - required_fields}"
    )

    # Verify strict mode is enabled (from architecture requirements)
    assert CriadorOutput.model_config.get("strict") is True, (
        "CriadorOutput must use ConfigDict(strict=True) per architecture"
    )


# ============================================================================
# Prompt File Validation Tests (1 test)
# ============================================================================


def test_criador_prompt_file_exists_and_has_all_placeholders():
    """Test that prompts/criador.md exists and contains all required placeholders."""
    from construtor.config.prompt_loader import load_prompt

    # Load the actual prompt file (not mocked)
    prompt_template = load_prompt("criador")

    # Required placeholders from AC #4
    required_placeholders = [
        "{tema}",
        "{foco}",
        "{sub_foco}",
        "{periodo}",
        "{posicao_correta}",
        "{nivel_dificuldade}",
    ]

    # Verify all placeholders exist in the template
    missing_placeholders = [p for p in required_placeholders if p not in prompt_template]

    assert not missing_placeholders, (
        f"Prompt template missing required placeholders: {missing_placeholders}"
    )

    # Verify template is not empty
    assert len(prompt_template) > 100, "Prompt template seems too short"

    # Verify key sections exist (Bloom's taxonomy, tipos de enunciado)
    assert "Taxonomia de Bloom" in prompt_template or "Bloom" in prompt_template, (
        "Prompt must include Bloom's taxonomy instructions"
    )
    assert "Tipos de Enunciado" in prompt_template or "tipo de enunciado" in prompt_template, (
        "Prompt must include question type selection guidance"
    )


# ============================================================================
# Initialization Tests (2 tests)
# ============================================================================


def test_initialization_with_provider_and_config(mock_provider, mock_config):
    """Test CriadorAgent initializes with provider and config."""
    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="Gere questão: {tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)

    assert agent._provider == mock_provider
    assert agent._config == mock_config
    assert agent._prompt_template is not None


def test_initialization_with_nonexistent_prompt(mock_provider, mock_config):
    """Test CriadorAgent raises error if prompt file doesn't exist."""
    with patch(
        "construtor.agents.criador.load_prompt",
        side_effect=FileNotFoundError("Prompt not found"),
    ):
        with pytest.raises(FileNotFoundError):
            CriadorAgent(mock_provider, mock_config)


# ============================================================================
# Generation Success Tests (5 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_create_question_returns_criador_output(mock_provider, mock_config, sample_subfoco):
    """Test create_question returns complete CriadorOutput."""
    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="Gere: {tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)
        result = await agent.create_question(sample_subfoco, posicao_correta="B", nivel_dificuldade=2)

    assert isinstance(result, CriadorOutput)
    assert result.enunciado is not None
    assert result.alternativa_a is not None
    assert result.alternativa_b is not None
    assert result.alternativa_c is not None
    assert result.alternativa_d is not None
    assert result.resposta_correta == "B"
    assert result.objetivo_educacional is not None
    assert result.nivel_dificuldade == 2
    assert result.tipo_enunciado is not None


@pytest.mark.asyncio
async def test_create_question_formats_prompt_with_all_variables(
    mock_provider, mock_config, sample_subfoco
):
    """Test create_question formats prompt with all required variables."""
    # Mock provider to return position C
    output_c = CriadorOutput(
        enunciado="Test",
        alternativa_a="A",
        alternativa_b="B",
        alternativa_c="Correta",
        alternativa_d="D",
        resposta_correta="C",
        objetivo_educacional="Obj",
        nivel_dificuldade=3,
        tipo_enunciado="conceitual",
    )
    mock_provider.generate.return_value = {
        "content": output_c,
        "tokens_used": 700,
        "cost": 0.01,
        "latency": 1.5,
    }

    prompt_template = "Tema:{tema}|Foco:{foco}|SubFoco:{sub_foco}|Periodo:{periodo}|Pos:{posicao_correta}|Nivel:{nivel_dificuldade}"

    with patch("construtor.agents.criador.load_prompt", return_value=prompt_template):
        agent = CriadorAgent(mock_provider, mock_config)
        await agent.create_question(sample_subfoco, posicao_correta="C", nivel_dificuldade=3)

    # Verify provider was called with formatted prompt
    mock_provider.generate.assert_called_once()
    call_args = mock_provider.generate.call_args
    prompt_arg = call_args.kwargs["prompt"]

    assert "Tema:Cardiologia" in prompt_arg
    assert "Foco:Insuficiência Cardíaca" in prompt_arg
    assert "SubFoco:Diagnóstico clínico de IC descompensada" in prompt_arg
    assert "Periodo:3º ano" in prompt_arg
    assert "Pos:C" in prompt_arg
    assert "Nivel:3" in prompt_arg


@pytest.mark.asyncio
async def test_create_question_passes_response_model(mock_provider, mock_config, sample_subfoco):
    """Test create_question passes response_model=CriadorOutput to provider."""
    # Mock provider to return position A
    output_a = CriadorOutput(
        enunciado="Test",
        alternativa_a="Correta",
        alternativa_b="B",
        alternativa_c="C",
        alternativa_d="D",
        resposta_correta="A",
        objetivo_educacional="Obj",
        nivel_dificuldade=1,
        tipo_enunciado="conceitual",
    )
    mock_provider.generate.return_value = {
        "content": output_a,
        "tokens_used": 600,
        "cost": 0.009,
        "latency": 1.2,
    }

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)
        await agent.create_question(sample_subfoco, posicao_correta="A", nivel_dificuldade=1)

    # Verify response_model was passed
    mock_provider.generate.assert_called_once()
    call_kwargs = mock_provider.generate.call_args.kwargs
    assert call_kwargs["response_model"] == CriadorOutput


@pytest.mark.asyncio
async def test_create_question_with_custom_difficulty_level(mock_provider, mock_config, sample_subfoco):
    """Test create_question with nivel_dificuldade=3."""
    # Mock provider to return nivel_dificuldade=3
    output_nivel_3 = CriadorOutput(
        enunciado="Caso complexo...",
        alternativa_a="Opção A",
        alternativa_b="Opção B",
        alternativa_c="Opção C",
        alternativa_d="Opção D",
        resposta_correta="A",
        objetivo_educacional="Avaliar tomada de decisão complexa",
        nivel_dificuldade=3,
        tipo_enunciado="raciocínio diagnóstico",
    )
    mock_provider.generate.return_value = {
        "content": output_nivel_3,
        "tokens_used": 900,
        "cost": 0.0135,
        "latency": 2.1,
    }

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)
        result = await agent.create_question(sample_subfoco, posicao_correta="A", nivel_dificuldade=3)

    assert result.nivel_dificuldade == 3
    assert result.resposta_correta == "A"


@pytest.mark.asyncio
async def test_create_question_with_different_positions(mock_provider, mock_config, sample_subfoco):
    """Test create_question with different posicao_correta values (A, B, C, D)."""
    positions = ["A", "B", "C", "D"]

    for pos in positions:
        # Create new mock for each position
        output = CriadorOutput(
            enunciado="Enunciado de teste",
            alternativa_a="Alt A",
            alternativa_b="Alt B",
            alternativa_c="Alt C",
            alternativa_d="Alt D",
            resposta_correta=pos,
            objetivo_educacional="Objetivo de teste",
            nivel_dificuldade=2,
            tipo_enunciado="conceitual",
        )
        mock_provider.generate.return_value = {
            "content": output,
            "tokens_used": 700,
            "cost": 0.01,
            "latency": 1.5,
        }

        with patch(
            "construtor.agents.criador.load_prompt",
            return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
        ):
            agent = CriadorAgent(mock_provider, mock_config)
            result = await agent.create_question(sample_subfoco, posicao_correta=pos)

        assert result.resposta_correta == pos, f"Failed for position {pos}"


# ============================================================================
# Validation and Error Tests (5 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_position_validation_failure(mock_provider, mock_config, sample_subfoco):
    """Test OutputParsingError when LLM returns wrong position."""
    # Mock returns "A" but we expect "B"
    wrong_output = CriadorOutput(
        enunciado="Enunciado",
        alternativa_a="Correta (mas na posição errada)",
        alternativa_b="Errada",
        alternativa_c="Errada",
        alternativa_d="Errada",
        resposta_correta="A",  # Wrong! Expected B
        objetivo_educacional="Objetivo",
        nivel_dificuldade=2,
        tipo_enunciado="conceitual",
    )
    mock_provider.generate.return_value = {
        "content": wrong_output,
        "tokens_used": 600,
        "cost": 0.009,
        "latency": 1.2,
    }

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)

        with pytest.raises(OutputParsingError) as exc_info:
            await agent.create_question(sample_subfoco, posicao_correta="B", nivel_dificuldade=2)

        # Validate error message and context
        error_msg = str(exc_info.value)
        assert "expected B" in error_msg
        assert "got A" in error_msg


@pytest.mark.asyncio
async def test_llm_generation_failure_propagates_error(mock_provider, mock_config, sample_subfoco):
    """Test OutputParsingError is raised when LLM generation fails."""
    # Mock provider raises an exception
    mock_provider.generate.side_effect = RuntimeError("LLM API error")

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)

        with pytest.raises(OutputParsingError) as exc_info:
            await agent.create_question(sample_subfoco, posicao_correta="B")

        # Verify error was wrapped
        assert "Failed to generate question" in str(exc_info.value)


@pytest.mark.asyncio
async def test_output_parsing_error_contains_context(mock_provider, mock_config, sample_subfoco):
    """Test OutputParsingError includes sub_foco, nivel, posicao_esperada context."""
    wrong_output = CriadorOutput(
        enunciado="Test",
        alternativa_a="A",
        alternativa_b="B",
        alternativa_c="C",
        alternativa_d="D",
        resposta_correta="D",  # Expected C
        objetivo_educacional="Obj",
        nivel_dificuldade=1,
        tipo_enunciado="conceitual",
    )
    mock_provider.generate.return_value = {
        "content": wrong_output,
        "tokens_used": 500,
        "cost": 0.008,
        "latency": 1.0,
    }

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)

        with pytest.raises(OutputParsingError) as exc_info:
            await agent.create_question(sample_subfoco, posicao_correta="C", nivel_dificuldade=1)

        # Check error has context attributes (via exception args/kwargs if stored)
        error_msg = str(exc_info.value)
        assert "expected C" in error_msg
        assert "got D" in error_msg


@pytest.mark.asyncio
async def test_invalid_posicao_correta_raises_value_error(mock_provider, mock_config, sample_subfoco):
    """Test ValueError when posicao_correta is not A/B/C/D."""
    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)

        with pytest.raises(ValueError) as exc_info:
            await agent.create_question(sample_subfoco, posicao_correta="E")  # Invalid

        assert "posicao_correta must be A/B/C/D" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_nivel_dificuldade_raises_value_error(mock_provider, mock_config, sample_subfoco):
    """Test ValueError when nivel_dificuldade is not 1-3."""
    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)

        with pytest.raises(ValueError) as exc_info:
            await agent.create_question(sample_subfoco, posicao_correta="A", nivel_dificuldade=4)

        assert "nivel_dificuldade must be 1-3" in str(exc_info.value)


# ============================================================================
# Logging Tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_successful_generation_logs_info(mock_provider, mock_config, sample_subfoco, caplog):
    """Test that successful generation logs INFO with all expected fields."""
    import logging

    caplog.set_level(logging.INFO)

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)
        await agent.create_question(sample_subfoco, posicao_correta="B", nivel_dificuldade=2)

    # Check log was created
    assert len(caplog.records) > 0

    # Find the "Question created" log
    log_messages = [rec.message for rec in caplog.records]
    question_created_logs = [msg for msg in log_messages if "Question created" in msg]
    assert len(question_created_logs) == 1

    log_msg = question_created_logs[0]
    # Verify expected fields in log
    assert "sub_foco=" in log_msg
    assert "nivel=" in log_msg
    assert "tipo=" in log_msg
    assert "posicao=" in log_msg
    assert "modelo=" in log_msg
    assert "tokens=" in log_msg
    assert "cost=" in log_msg
    assert "latency=" in log_msg


@pytest.mark.asyncio
async def test_log_contains_all_expected_fields(mock_provider, mock_config, sample_subfoco, caplog):
    """Test that log contains specific values for all expected fields."""
    import logging

    caplog.set_level(logging.INFO)

    with patch(
        "construtor.agents.criador.load_prompt",
        return_value="{tema} {foco} {sub_foco} {periodo} {posicao_correta} {nivel_dificuldade}",
    ):
        agent = CriadorAgent(mock_provider, mock_config)
        result = await agent.create_question(sample_subfoco, posicao_correta="B", nivel_dificuldade=2)

    log_msg = caplog.records[-1].message

    # Verify specific values
    assert sample_subfoco.sub_foco in log_msg
    assert "nivel=2" in log_msg
    assert result.tipo_enunciado in log_msg
    assert "posicao=B" in log_msg
    assert mock_config.default_model in log_msg
    assert "tokens=850" in log_msg
    assert "cost=0.0127" in log_msg
    assert "latency=" in log_msg
