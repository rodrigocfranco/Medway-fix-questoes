"""Tests for feedback models (FeedbackEstruturado, ComentadorOutput, ValidadorOutput)."""

import pytest
from pydantic import ValidationError

from construtor.models.feedback import (
    ComentadorOutput,
    FeedbackEstruturado,
    ValidadorOutput,
)


def test_feedback_estruturado_all_false_valid():
    """Test FeedbackEstruturado with all boolean fields False."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=False,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
    )

    assert feedback.enunciado_ambiguo is False
    assert feedback.distratores_fracos is False
    assert feedback.gabarito_questionavel is False
    assert feedback.comentario_incompleto is False
    assert feedback.fora_do_nivel is False
    assert feedback.observacoes is None  # Optional field defaults to None


def test_feedback_estruturado_with_observacoes():
    """Test FeedbackEstruturado with optional observacoes field."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="Enunciado usa terminologia ambígua sobre metabolismo hepático.",
    )

    assert feedback.enunciado_ambiguo is True
    assert feedback.observacoes == "Enunciado usa terminologia ambígua sobre metabolismo hepático."


def test_feedback_estruturado_strict_mode_no_coercion():
    """Test that strict mode prevents bool coercion from strings."""
    with pytest.raises(ValidationError) as exc_info:
        FeedbackEstruturado(
            enunciado_ambiguo="true",  # String instead of bool - should fail
            distratores_fracos=False,
            gabarito_questionavel=False,
            comentario_incompleto=False,
            fora_do_nivel=False,
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("enunciado_ambiguo",) for error in errors)


def test_comentador_output_valid_data():
    """Test ComentadorOutput with valid blind review data."""
    data = {
        "resposta_declarada": "B",
        "comentario_introducao": "A questão aborda metabolismo hepático...",
        "comentario_visao_especifica": "A bile é produzida no fígado...",
        "comentario_alt_a": "Incorreto. Esta não é a função primária.",
        "comentario_alt_b": "Correto! O fígado produz bile para digestão de lipídios.",
        "comentario_alt_c": "Incorreto. Insulina é função do pâncreas.",
        "comentario_alt_d": "Incorreto. Filtragem é função renal.",
        "comentario_visao_aprovado": "Questão aprovada. Boa qualidade pedagógica.",
        "referencia_bibliografica": "Guyton & Hall, Tratado de Fisiologia Médica, 13ª ed.",
    }

    output = ComentadorOutput(**data)

    assert output.resposta_declarada == "B"
    assert output.comentario_introducao == "A questão aborda metabolismo hepático..."
    assert output.referencia_bibliografica == "Guyton & Hall, Tratado de Fisiologia Médica, 13ª ed."


def test_comentador_output_invalid_resposta_declarada():
    """Test ComentadorOutput rejects invalid resposta_declarada."""
    data = {
        "resposta_declarada": "E",  # Invalid! Must be A, B, C, or D
        "comentario_introducao": "Intro",
        "comentario_visao_especifica": "Visão",
        "comentario_alt_a": "Alt A",
        "comentario_alt_b": "Alt B",
        "comentario_alt_c": "Alt C",
        "comentario_alt_d": "Alt D",
        "comentario_visao_aprovado": "Aprovado",
        "referencia_bibliografica": "Ref",
    }

    with pytest.raises(ValidationError) as exc_info:
        ComentadorOutput(**data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("resposta_declarada",) for error in errors)


def test_comentador_output_all_required_fields():
    """Test that ComentadorOutput requires all 9 fields."""
    # Missing comentario_visao_aprovado
    incomplete_data = {
        "resposta_declarada": "A",
        "comentario_introducao": "Intro",
        "comentario_visao_especifica": "Visão",
        "comentario_alt_a": "Alt A",
        "comentario_alt_b": "Alt B",
        "comentario_alt_c": "Alt C",
        "comentario_alt_d": "Alt D",
        # Missing: comentario_visao_aprovado
        "referencia_bibliografica": "Ref",
    }

    with pytest.raises(ValidationError) as exc_info:
        ComentadorOutput(**incomplete_data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("comentario_visao_aprovado",) for error in errors)


def test_validador_output_aprovada_with_concordancia():
    """Test ValidadorOutput with approved decision and agreement."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=False,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
    )

    validador = ValidadorOutput(
        decisao="aprovada",
        concordancia=True,
        feedback_estruturado=feedback,
    )

    assert validador.decisao == "aprovada"
    assert validador.concordancia is True
    assert validador.feedback_estruturado.enunciado_ambiguo is False


def test_validador_output_rejeitada_sem_concordancia():
    """Test ValidadorOutput with rejected decision and no agreement."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=True,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="Enunciado ambíguo e distratores muito óbvios.",
    )

    validador = ValidadorOutput(
        decisao="rejeitada",
        concordancia=False,
        feedback_estruturado=feedback,
    )

    assert validador.decisao == "rejeitada"
    assert validador.concordancia is False
    assert validador.feedback_estruturado.enunciado_ambiguo is True
    assert validador.feedback_estruturado.distratores_fracos is True
    assert validador.feedback_estruturado.observacoes == "Enunciado ambíguo e distratores muito óbvios."


def test_validador_output_invalid_decisao():
    """Test ValidadorOutput rejects invalid decisao values."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=False,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
    )

    with pytest.raises(ValidationError) as exc_info:
        ValidadorOutput(
            decisao="pendente",  # Invalid! Must be "aprovada" or "rejeitada"
            concordancia=True,
            feedback_estruturado=feedback,
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("decisao",) for error in errors)


def test_validador_output_nested_model_validation():
    """Test that nested FeedbackEstruturado also validates with strict mode."""
    # Create invalid nested feedback (string instead of bool)
    with pytest.raises(ValidationError):
        ValidadorOutput(
            decisao="aprovada",
            concordancia=True,
            feedback_estruturado={
                "enunciado_ambiguo": "false",  # Invalid! Should be bool
                "distratores_fracos": False,
                "gabarito_questionavel": False,
                "comentario_incompleto": False,
                "fora_do_nivel": False,
            },
        )


def test_validador_output_json_serialization():
    """Test ValidadorOutput can serialize to/from JSON with nested model."""
    import json

    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=True,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="Duas questões identificadas.",
    )

    original = ValidadorOutput(
        decisao="rejeitada",
        concordancia=False,
        feedback_estruturado=feedback,
    )

    # Serialize to JSON
    json_str = original.model_dump_json()

    # Deserialize back
    data = json.loads(json_str)
    reconstructed = ValidadorOutput(**data)

    assert reconstructed.decisao == original.decisao
    assert reconstructed.concordancia == original.concordancia
    assert reconstructed.feedback_estruturado.enunciado_ambiguo is True
    assert reconstructed.feedback_estruturado.observacoes == "Duas questões identificadas."


def test_feedback_estruturado_empty_string_observacoes():
    """Test FeedbackEstruturado accepts empty string for observacoes."""
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes="",  # Empty string should be valid
    )

    assert feedback.observacoes == ""
    assert feedback.enunciado_ambiguo is True
