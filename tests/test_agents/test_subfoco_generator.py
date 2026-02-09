"""Tests for SubFocoGenerator agent."""

from unittest.mock import AsyncMock, patch

import pytest

from construtor.agents.subfoco_generator import (
    SubFocoBatchResponse,
    SubFocoGenerator,
)
from construtor.config.exceptions import OutputParsingError
from construtor.models.question import FocoInput, SubFocoInput


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
    """Mock LLMProvider that returns SubFocoBatchResponse."""
    provider = AsyncMock()
    sub_focos = [f"Sub-foco específico {i}" for i in range(50)]
    provider.generate.return_value = {
        "content": SubFocoBatchResponse(sub_focos=sub_focos),
        "tokens_used": 1500,
        "cost": 0.015,
        "latency": 2.3,
    }
    return provider


@pytest.fixture
def sample_foco():
    """FocoInput de exemplo."""
    return FocoInput(
        tema="Cardiologia",
        foco="Insuficiência Cardíaca",
        periodo="3º ano",
    )


# ============================================================================
# Initialization Tests
# ============================================================================


def test_initialization_with_provider_and_config(mock_provider, mock_config):
    """Test SubFocoGenerator initializes with provider and config."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="Gere {count} sub-focos para {tema} {foco} {periodo}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)

    assert generator._provider == mock_provider
    assert generator._config == mock_config
    assert generator._prompt_template is not None


def test_initialization_with_nonexistent_prompt(mock_provider, mock_config):
    """Test SubFocoGenerator raises error if prompt file doesn't exist."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        side_effect=FileNotFoundError("Prompt not found"),
    ):
        with pytest.raises(FileNotFoundError):
            SubFocoGenerator(mock_provider, mock_config)


def test_initialization_rejects_zero_count(mock_provider, mock_config, sample_foco):
    """Test generate_batch raises ValueError for count=0."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)

        # Use asyncio.run since we can't use @pytest.mark.asyncio on sync test
        import asyncio

        with pytest.raises(ValueError) as exc_info:
            asyncio.run(generator.generate_batch(sample_foco, count=0))

        assert "count must be positive" in str(exc_info.value)
        assert "got 0" in str(exc_info.value)


def test_initialization_rejects_negative_count(mock_provider, mock_config, sample_foco):
    """Test generate_batch raises ValueError for negative count."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)

        import asyncio

        with pytest.raises(ValueError) as exc_info:
            asyncio.run(generator.generate_batch(sample_foco, count=-5))

        assert "count must be positive" in str(exc_info.value)
        assert "got -5" in str(exc_info.value)


# ============================================================================
# Successful Generation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_generate_batch_returns_subfoco_list(
    mock_provider, mock_config, sample_foco
):
    """Test generate_batch returns list[SubFocoInput] with 50 items."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="Gere {count} sub-focos para {tema} {foco} {periodo}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(sample_foco)

    assert len(result) == 50
    assert all(isinstance(sf, SubFocoInput) for sf in result)
    assert all(sf.tema == "Cardiologia" for sf in result)
    assert all(sf.foco == "Insuficiência Cardíaca" for sf in result)
    assert all(sf.periodo == "3º ano" for sf in result)


@pytest.mark.asyncio
async def test_generate_batch_formats_prompt_correctly(
    mock_provider, mock_config, sample_foco
):
    """Test generate_batch formats prompt with correct variables."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="Tema: {tema}, Foco: {foco}, Periodo: {periodo}, Count: {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        await generator.generate_batch(sample_foco, count=50)

    # Verify provider was called with formatted prompt
    mock_provider.generate.assert_called_once()
    call_args = mock_provider.generate.call_args
    prompt = call_args.kwargs["prompt"]

    assert "Tema: Cardiologia" in prompt
    assert "Foco: Insuficiência Cardíaca" in prompt
    assert "Periodo: 3º ano" in prompt
    assert "Count: 50" in prompt


@pytest.mark.asyncio
async def test_generate_batch_passes_response_model(
    mock_provider, mock_config, sample_foco
):
    """Test generate_batch passes response_model=SubFocoBatchResponse to provider."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        await generator.generate_batch(sample_foco)

    call_args = mock_provider.generate.call_args
    assert call_args.kwargs["response_model"] == SubFocoBatchResponse


@pytest.mark.asyncio
async def test_generate_batch_uses_config_model_and_temperature(
    mock_provider, mock_config, sample_foco
):
    """Test generate_batch uses model and temperature from config."""
    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        await generator.generate_batch(sample_foco)

    call_args = mock_provider.generate.call_args
    assert call_args.kwargs["model"] == mock_config.default_model
    assert call_args.kwargs["temperature"] == mock_config.temperature


@pytest.mark.asyncio
async def test_generate_batch_with_custom_count(
    mock_provider, mock_config, sample_foco
):
    """Test generate_batch with custom count parameter."""
    # Mock provider returns 10 sub-focos
    mock_provider.generate.return_value = {
        "content": SubFocoBatchResponse(
            sub_focos=[f"Sub-foco {i}" for i in range(10)]
        ),
        "tokens_used": 500,
        "cost": 0.005,
        "latency": 1.0,
    }

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(sample_foco, count=10)

    assert len(result) == 10


@pytest.mark.asyncio
async def test_generate_batch_with_different_periodos(mock_provider, mock_config):
    """Test generate_batch works with different academic periods."""
    periodos = ["1º ano", "2º ano", "3º ano", "4º ano"]

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)

        for periodo in periodos:
            foco = FocoInput(
                tema="Cardiologia", foco="Insuficiência Cardíaca", periodo=periodo
            )
            result = await generator.generate_batch(foco)

            assert all(sf.periodo == periodo for sf in result)


# ============================================================================
# Validation and Retry Tests
# ============================================================================


@pytest.mark.asyncio
async def test_retry_on_insufficient_count(mock_provider, mock_config, sample_foco):
    """Test retry when LLM returns fewer sub-focos than requested."""
    # First call: 30 sub-focos (insufficient)
    # Second call: 50 sub-focos (success)
    mock_provider.generate.side_effect = [
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(30)]
            ),
            "tokens_used": 800,
            "cost": 0.008,
            "latency": 1.5,
        },
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(50)]
            ),
            "tokens_used": 1500,
            "cost": 0.015,
            "latency": 2.3,
        },
    ]

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(sample_foco)

    assert len(result) == 50
    assert mock_provider.generate.call_count == 2


@pytest.mark.asyncio
async def test_deduplication_triggers_retry(mock_provider, mock_config, sample_foco):
    """Test that duplicate sub-focos are removed and trigger retry if needed."""
    # First call: 50 items but with duplicates (only 30 unique)
    # Second call: 50 unique items
    duplicated_list = [f"sf-{i % 30}" for i in range(50)]  # Only 30 unique
    mock_provider.generate.side_effect = [
        {
            "content": SubFocoBatchResponse(sub_focos=duplicated_list),
            "tokens_used": 800,
            "cost": 0.008,
            "latency": 1.5,
        },
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(50)]
            ),
            "tokens_used": 1500,
            "cost": 0.015,
            "latency": 2.3,
        },
    ]

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(sample_foco)

    assert len(result) == 50
    assert mock_provider.generate.call_count == 2


@pytest.mark.asyncio
async def test_empty_subfoco_filtered_triggers_retry(
    mock_provider, mock_config, sample_foco
):
    """Test that empty/whitespace sub-focos are filtered and trigger retry."""
    # First call: 50 items but some are empty/whitespace (only 30 valid)
    # Second call: 50 valid items
    invalid_list = [f"sf-{i}" if i < 30 else "" for i in range(50)]
    mock_provider.generate.side_effect = [
        {
            "content": SubFocoBatchResponse(sub_focos=invalid_list),
            "tokens_used": 800,
            "cost": 0.008,
            "latency": 1.5,
        },
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(50)]
            ),
            "tokens_used": 1500,
            "cost": 0.015,
            "latency": 2.3,
        },
    ]

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(sample_foco)

    assert len(result) == 50
    assert mock_provider.generate.call_count == 2


@pytest.mark.asyncio
async def test_whitespace_only_subfoco_filtered(
    mock_provider, mock_config, sample_foco
):
    """Test that whitespace-only sub-focos are filtered."""
    # Mix of valid, empty, and whitespace-only
    mixed_list = [
        f"sf-{i}" if i < 30 else ("   " if i % 2 == 0 else "") for i in range(50)
    ]
    mock_provider.generate.side_effect = [
        {
            "content": SubFocoBatchResponse(sub_focos=mixed_list),
            "tokens_used": 800,
            "cost": 0.008,
            "latency": 1.5,
        },
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(50)]
            ),
            "tokens_used": 1500,
            "cost": 0.015,
            "latency": 2.3,
        },
    ]

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(sample_foco)

    # Should succeed on second attempt
    assert len(result) == 50
    assert mock_provider.generate.call_count == 2


@pytest.mark.asyncio
async def test_output_parsing_error_after_max_retries(
    mock_provider, mock_config, sample_foco
):
    """Test OutputParsingError raised after max retries with insufficient count."""
    # All attempts return insufficient sub-focos
    mock_provider.generate.return_value = {
        "content": SubFocoBatchResponse(sub_focos=[f"sf-{i}" for i in range(30)]),
        "tokens_used": 800,
        "cost": 0.008,
        "latency": 1.5,
    }

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)

        with pytest.raises(OutputParsingError) as exc_info:
            await generator.generate_batch(sample_foco)

        # Verify error message contains context
        error_msg = str(exc_info.value)
        assert "50" in error_msg  # Expected count
        assert "30" in error_msg  # Actual count
        assert "3 attempts" in error_msg  # Max retries + 1

        # Verify 3 attempts were made (1 initial + 2 retries)
        assert mock_provider.generate.call_count == 3


# ============================================================================
# Logging Tests
# ============================================================================


@pytest.mark.asyncio
async def test_logs_info_on_successful_generation(
    mock_provider, mock_config, sample_foco, caplog
):
    """Test that INFO log is generated on successful generation."""
    import logging

    caplog.set_level(logging.INFO)

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        await generator.generate_batch(sample_foco)

    # Verify INFO log contains expected information
    assert any("SubFoco generation" in record.message for record in caplog.records)
    assert any("Insuficiência Cardíaca" in record.message for record in caplog.records)
    assert any("modelo=" in record.message for record in caplog.records)
    assert any("tokens=" in record.message for record in caplog.records)
    assert any("cost=" in record.message for record in caplog.records)
    assert any("latency=" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_logs_warning_on_retry(mock_provider, mock_config, sample_foco, caplog):
    """Test that WARNING log is generated when retry is needed."""
    import logging

    caplog.set_level(logging.WARNING)

    # First call insufficient, second call success
    mock_provider.generate.side_effect = [
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(30)]
            ),
            "tokens_used": 800,
            "cost": 0.008,
            "latency": 1.5,
        },
        {
            "content": SubFocoBatchResponse(
                sub_focos=[f"sf-{i}" for i in range(50)]
            ),
            "tokens_used": 1500,
            "cost": 0.015,
            "latency": 2.3,
        },
    ]

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        await generator.generate_batch(sample_foco)

    # Verify WARNING log for insufficient count
    warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_records) > 0
    assert any("Insufficient sub-focos" in record.message for record in warning_records)
    assert any("expected=50" in record.message for record in warning_records)
    assert any("got=30" in record.message for record in warning_records)


# ============================================================================
# Mapping Tests
# ============================================================================


@pytest.mark.asyncio
async def test_subfoco_input_mapping_preserves_original_data(
    mock_provider, mock_config
):
    """Test that SubFocoInput items preserve original FocoInput data."""
    foco = FocoInput(tema="Neurologia", foco="AVC Isquêmico", periodo="4º ano")

    with patch(
        "construtor.agents.subfoco_generator.load_prompt",
        return_value="{tema} {foco} {periodo} {count}",
    ):
        generator = SubFocoGenerator(mock_provider, mock_config)
        result = await generator.generate_batch(foco)

    # Verify all SubFocoInput items preserve original data
    for sf in result:
        assert sf.tema == "Neurologia"
        assert sf.foco == "AVC Isquêmico"
        assert sf.periodo == "4º ano"
        assert sf.sub_foco.startswith("Sub-foco específico")
