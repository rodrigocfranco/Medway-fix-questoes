"""Tests for pipeline models (BatchState, CheckpointResult, RetryContext)."""

import pytest
from pydantic import ValidationError

from construtor.models.feedback import FeedbackEstruturado
from construtor.models.pipeline import BatchState, CheckpointResult, RetryContext


def test_batch_state_valid_data():
    """Test BatchState with valid pipeline state data."""
    state = BatchState(
        foco_atual="Fígado",
        sub_foco_atual=3,
        total_processados=25,
        timestamp="2026-02-07T10:30:00Z",
    )

    assert state.foco_atual == "Fígado"
    assert state.sub_foco_atual == 3
    assert state.total_processados == 25
    assert state.timestamp == "2026-02-07T10:30:00Z"


def test_batch_state_strict_mode_no_coercion():
    """Test BatchState strict mode prevents int to str coercion."""
    with pytest.raises(ValidationError) as exc_info:
        BatchState(
            foco_atual="Fígado",
            sub_foco_atual="3",  # String instead of int - should fail
            total_processados=25,
            timestamp="2026-02-07T10:30:00Z",
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("sub_foco_atual",) for error in errors)


def test_batch_state_json_serialization():
    """Test BatchState can serialize to/from JSON."""
    import json

    original = BatchState(
        foco_atual="Cardiologia",
        sub_foco_atual=5,
        total_processados=50,
        timestamp="2026-02-07T15:45:00Z",
    )

    json_str = original.model_dump_json()
    data = json.loads(json_str)
    reconstructed = BatchState(**data)

    assert reconstructed.foco_atual == original.foco_atual
    assert reconstructed.sub_foco_atual == original.sub_foco_atual
    assert reconstructed.total_processados == original.total_processados


def test_checkpoint_result_valid_data():
    """Test CheckpointResult with valid checkpoint metrics."""
    result = CheckpointResult(
        checkpoint_id="checkpoint_001",
        foco_range="Focos 1-10",
        total_geradas=100,
        aprovadas=85,
        rejeitadas=12,
        failed=3,
        taxa_aprovacao=0.85,
        concordancia_media=0.92,
        custo_total=12.50,
        sample_question_ids=[1, 15, 32, 47, 89],
    )

    assert result.checkpoint_id == "checkpoint_001"
    assert result.foco_range == "Focos 1-10"
    assert result.total_geradas == 100
    assert result.aprovadas == 85
    assert result.rejeitadas == 12
    assert result.failed == 3
    assert result.taxa_aprovacao == 0.85
    assert result.concordancia_media == 0.92
    assert result.custo_total == 12.50
    assert result.sample_question_ids == [1, 15, 32, 47, 89]


def test_checkpoint_result_strict_mode_float_validation():
    """Test CheckpointResult strict mode validates float types."""
    with pytest.raises(ValidationError) as exc_info:
        CheckpointResult(
            checkpoint_id="checkpoint_002",
            foco_range="Focos 11-20",
            total_geradas=100,
            aprovadas=80,
            rejeitadas=15,
            failed=5,
            taxa_aprovacao="0.80",  # String instead of float - should fail
            concordancia_media=0.90,
            custo_total=15.00,
            sample_question_ids=[1, 2, 3],
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("taxa_aprovacao",) for error in errors)


def test_checkpoint_result_list_type_validation():
    """Test CheckpointResult validates list[int] for sample_question_ids."""
    result = CheckpointResult(
        checkpoint_id="checkpoint_003",
        foco_range="Focos 21-30",
        total_geradas=95,
        aprovadas=88,
        rejeitadas=5,
        failed=2,
        taxa_aprovacao=0.926,
        concordancia_media=0.95,
        custo_total=18.75,
        sample_question_ids=[10, 25, 40, 55, 70, 85],  # Valid list[int]
    )

    assert len(result.sample_question_ids) == 6
    assert all(isinstance(id, int) for id in result.sample_question_ids)


def test_retry_context_valid_with_feedback():
    """Test RetryContext with structured feedback."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="Enunciado precisa ser mais específico.",
    )

    context = RetryContext(
        rodada_atual=2,
        feedback_estruturado=feedback,
        question_id=42,
    )

    assert context.rodada_atual == 2
    assert context.feedback_estruturado.enunciado_ambiguo is True
    assert context.feedback_estruturado.observacoes == "Enunciado precisa ser mais específico."
    assert context.question_id == 42


def test_retry_context_optional_question_id():
    """Test RetryContext with optional question_id field."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=False,
        distratores_fracos=True,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
    )

    # Without question_id
    context_without_id = RetryContext(
        rodada_atual=1,
        feedback_estruturado=feedback,
    )

    assert context_without_id.question_id is None

    # With question_id
    context_with_id = RetryContext(
        rodada_atual=1,
        feedback_estruturado=feedback,
        question_id=123,
    )

    assert context_with_id.question_id == 123


def test_retry_context_strict_mode_int_validation():
    """Test RetryContext strict mode prevents string to int coercion."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=False,
        distratores_fracos=False,
        gabarito_questionavel=True,
        comentario_incompleto=False,
        fora_do_nivel=False,
    )

    with pytest.raises(ValidationError) as exc_info:
        RetryContext(
            rodada_atual="3",  # String instead of int - should fail
            feedback_estruturado=feedback,
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("rodada_atual",) for error in errors)


def test_retry_context_nested_feedback_validation():
    """Test RetryContext validates nested FeedbackEstruturado with strict mode."""
    # Invalid nested feedback (string instead of bool)
    with pytest.raises(ValidationError):
        RetryContext(
            rodada_atual=1,
            feedback_estruturado={
                "enunciado_ambiguo": "true",  # Invalid! Should be bool
                "distratores_fracos": False,
                "gabarito_questionavel": False,
                "comentario_incompleto": False,
                "fora_do_nivel": False,
            },
        )
