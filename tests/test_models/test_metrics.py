"""Tests for metrics models (QuestionMetrics, BatchMetrics, ModelComparison)."""

import pytest
from pydantic import ValidationError

from construtor.models.metrics import BatchMetrics, ModelComparison, QuestionMetrics


def test_question_metrics_valid_data():
    """Test QuestionMetrics with valid per-question metrics."""
    metrics = QuestionMetrics(
        modelo="gpt-4",
        tokens=1250,
        custo=0.0375,
        rodadas=1,
        tempo=2.5,
        decisao="aprovada",
        timestamp="2026-02-07T10:30:00Z",
    )

    assert metrics.modelo == "gpt-4"
    assert metrics.tokens == 1250
    assert metrics.custo == 0.0375
    assert metrics.rodadas == 1
    assert metrics.tempo == 2.5
    assert metrics.decisao == "aprovada"
    assert metrics.timestamp == "2026-02-07T10:30:00Z"


def test_question_metrics_strict_mode_no_int_coercion():
    """Test QuestionMetrics strict mode prevents string to int coercion."""
    with pytest.raises(ValidationError) as exc_info:
        QuestionMetrics(
            modelo="gpt-4",
            tokens="1250",  # String instead of int - should fail
            custo=0.0375,
            rodadas=1,
            tempo=2.5,
            decisao="aprovada",
            timestamp="2026-02-07T10:30:00Z",
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("tokens",) for error in errors)


def test_question_metrics_strict_mode_allows_int_to_float():
    """Test QuestionMetrics strict mode allows int to float coercion (lossless)."""
    # In Pydantic strict mode, int -> float is allowed because it's lossless
    metrics = QuestionMetrics(
        modelo="gpt-4",
        tokens=1250,
        custo=0.0375,
        rodadas=1,
        tempo=2,  # Int is accepted and converted to float (2.0)
        decisao="aprovada",
        timestamp="2026-02-07T10:30:00Z",
    )

    # Verify int was converted to float
    assert metrics.tempo == 2.0
    assert isinstance(metrics.tempo, float)


def test_question_metrics_multiple_rounds():
    """Test QuestionMetrics with multiple validation rounds."""
    metrics = QuestionMetrics(
        modelo="gpt-3.5-turbo",
        tokens=2500,
        custo=0.005,
        rodadas=3,  # Multiple retry rounds
        tempo=8.7,
        decisao="aprovada",
        timestamp="2026-02-07T11:00:00Z",
    )

    assert metrics.rodadas == 3
    assert metrics.decisao == "aprovada"


def test_batch_metrics_valid_data():
    """Test BatchMetrics with valid batch-level aggregation."""
    metrics = BatchMetrics(
        total_questoes=100,
        aprovadas=85,
        rejeitadas=12,
        failed=3,
        custo_total=125.50,
        tempo_total=450.5,
        taxa_aprovacao=0.85,
    )

    assert metrics.total_questoes == 100
    assert metrics.aprovadas == 85
    assert metrics.rejeitadas == 12
    assert metrics.failed == 3
    assert metrics.custo_total == 125.50
    assert metrics.tempo_total == 450.5
    assert metrics.taxa_aprovacao == 0.85


def test_batch_metrics_zero_approvals():
    """Test BatchMetrics with zero approvals scenario."""
    metrics = BatchMetrics(
        total_questoes=50,
        aprovadas=0,
        rejeitadas=45,
        failed=5,
        custo_total=50.0,
        tempo_total=200.0,
        taxa_aprovacao=0.0,
    )

    assert metrics.aprovadas == 0
    assert metrics.taxa_aprovacao == 0.0


def test_batch_metrics_strict_mode_validation():
    """Test BatchMetrics strict mode prevents type coercion."""
    with pytest.raises(ValidationError) as exc_info:
        BatchMetrics(
            total_questoes="100",  # String instead of int - should fail
            aprovadas=85,
            rejeitadas=12,
            failed=3,
            custo_total=125.50,
            tempo_total=450.5,
            taxa_aprovacao=0.85,
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("total_questoes",) for error in errors)


def test_batch_metrics_json_serialization():
    """Test BatchMetrics can serialize to/from JSON."""
    import json

    original = BatchMetrics(
        total_questoes=200,
        aprovadas=180,
        rejeitadas=15,
        failed=5,
        custo_total=250.75,
        tempo_total=800.0,
        taxa_aprovacao=0.90,
    )

    json_str = original.model_dump_json()
    data = json.loads(json_str)
    reconstructed = BatchMetrics(**data)

    assert reconstructed.total_questoes == original.total_questoes
    assert reconstructed.custo_total == original.custo_total


def test_model_comparison_valid_data():
    """Test ModelComparison with valid model performance data."""
    comparison = ModelComparison(
        modelo="gpt-4",
        questoes_geradas=500,
        taxa_aprovacao=0.92,
        custo_medio=0.045,
        latencia_media=3.2,
        taxa_concordancia=0.95,
    )

    assert comparison.modelo == "gpt-4"
    assert comparison.questoes_geradas == 500
    assert comparison.taxa_aprovacao == 0.92
    assert comparison.custo_medio == 0.045
    assert comparison.latencia_media == 3.2
    assert comparison.taxa_concordancia == 0.95


def test_model_comparison_multiple_models():
    """Test ModelComparison can represent different models."""
    gpt4_metrics = ModelComparison(
        modelo="gpt-4",
        questoes_geradas=500,
        taxa_aprovacao=0.92,
        custo_medio=0.045,
        latencia_media=3.2,
        taxa_concordancia=0.95,
    )

    gpt35_metrics = ModelComparison(
        modelo="gpt-3.5-turbo",
        questoes_geradas=500,
        taxa_aprovacao=0.78,
        custo_medio=0.002,
        latencia_media=1.5,
        taxa_concordancia=0.82,
    )

    claude_metrics = ModelComparison(
        modelo="claude-sonnet-4.5",
        questoes_geradas=500,
        taxa_aprovacao=0.94,
        custo_medio=0.015,
        latencia_media=2.8,
        taxa_concordancia=0.96,
    )

    # Verify different model comparisons
    assert gpt4_metrics.taxa_aprovacao > gpt35_metrics.taxa_aprovacao
    assert gpt35_metrics.custo_medio < gpt4_metrics.custo_medio
    assert claude_metrics.taxa_concordancia > gpt35_metrics.taxa_concordancia


def test_model_comparison_strict_mode_validation():
    """Test ModelComparison strict mode prevents type coercion."""
    with pytest.raises(ValidationError) as exc_info:
        ModelComparison(
            modelo="gpt-4",
            questoes_geradas=500,
            taxa_aprovacao="0.92",  # String instead of float - should fail
            custo_medio=0.045,
            latencia_media=3.2,
            taxa_concordancia=0.95,
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("taxa_aprovacao",) for error in errors)


def test_model_comparison_all_float_fields():
    """Test that all rate/cost/latency fields accept floats."""
    comparison = ModelComparison(
        modelo="test-model",
        questoes_geradas=100,
        taxa_aprovacao=0.999,
        custo_medio=0.0001,
        latencia_media=0.5,
        taxa_concordancia=1.0,
    )

    # Verify all floats are preserved
    assert isinstance(comparison.taxa_aprovacao, float)
    assert isinstance(comparison.custo_medio, float)
    assert isinstance(comparison.latencia_media, float)
    assert isinstance(comparison.taxa_concordancia, float)
