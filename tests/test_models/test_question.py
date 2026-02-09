"""Tests for question models (FocoInput, SubFocoInput, CriadorOutput, QuestionRecord)."""

import pytest
from pydantic import ValidationError

from construtor.models.question import CriadorOutput, FocoInput, QuestionRecord, SubFocoInput


# ============================================================================
# FocoInput Tests
# ============================================================================


def test_foco_input_valid_data():
    """Test FocoInput accepts valid data."""
    foco = FocoInput(
        tema="Cardiologia",
        foco="Insuficiência Cardíaca",
        periodo="3º ano",
    )

    assert foco.tema == "Cardiologia"
    assert foco.foco == "Insuficiência Cardíaca"
    assert foco.periodo == "3º ano"


def test_foco_input_invalid_periodo():
    """Test FocoInput rejects invalid periodo."""
    with pytest.raises(ValidationError) as exc_info:
        FocoInput(
            tema="Cardiologia",
            foco="Insuficiência Cardíaca",
            periodo="5º ano",  # Invalid! Must be 1º-4º ano
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("periodo",) for error in errors)


def test_foco_input_empty_tema():
    """Test FocoInput rejects empty tema."""
    with pytest.raises(ValidationError) as exc_info:
        FocoInput(
            tema="",  # Empty string
            foco="Insuficiência Cardíaca",
            periodo="3º ano",
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("tema",) for error in errors)


def test_foco_input_whitespace_foco():
    """Test FocoInput rejects whitespace-only foco."""
    with pytest.raises(ValidationError) as exc_info:
        FocoInput(
            tema="Cardiologia",
            foco="   ",  # Whitespace only
            periodo="3º ano",
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("foco",) for error in errors)


def test_foco_input_strict_mode():
    """Test FocoInput strict mode prevents type coercion."""
    with pytest.raises(ValidationError):
        FocoInput(
            tema=123,  # Should be string, not int
            foco="Test",
            periodo="1º ano",
        )


# ============================================================================
# SubFocoInput Tests
# ============================================================================


def test_subfoco_input_valid_data():
    """Test SubFocoInput accepts valid data with all fields."""
    subfoco = SubFocoInput(
        tema="Cardiologia",
        foco="Insuficiência Cardíaca",
        sub_foco="Classificação funcional NYHA da IC",
        periodo="3º ano",
    )

    assert subfoco.tema == "Cardiologia"
    assert subfoco.foco == "Insuficiência Cardíaca"
    assert subfoco.sub_foco == "Classificação funcional NYHA da IC"
    assert subfoco.periodo == "3º ano"


def test_subfoco_input_inherits_periodo_validation():
    """Test SubFocoInput inherits periodo validation from FocoInput."""
    with pytest.raises(ValidationError) as exc_info:
        SubFocoInput(
            tema="Cardiologia",
            foco="Insuficiência Cardíaca",
            sub_foco="Classificação NYHA",
            periodo="5º ano",  # Invalid! Inherited validation from FocoInput
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("periodo",) for error in errors)


def test_subfoco_input_empty_sub_foco():
    """Test SubFocoInput rejects empty sub_foco."""
    with pytest.raises(ValidationError) as exc_info:
        SubFocoInput(
            tema="Cardiologia",
            foco="Insuficiência Cardíaca",
            sub_foco="",  # Empty string - should fail
            periodo="3º ano",
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("sub_foco",) for error in errors)


def test_subfoco_input_whitespace_sub_foco():
    """Test SubFocoInput rejects whitespace-only sub_foco."""
    with pytest.raises(ValidationError) as exc_info:
        SubFocoInput(
            tema="Cardiologia",
            foco="Insuficiência Cardíaca",
            sub_foco="   ",  # Whitespace only - should fail
            periodo="3º ano",
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("sub_foco",) for error in errors)


# ============================================================================
# CriadorOutput Tests
# ============================================================================


def test_criador_output_valid_data():
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
        "tipo_enunciado": "conceitual",
    }

    output = CriadorOutput(**data)

    assert output.enunciado == "Qual é a função principal do fígado?"
    assert output.alternativa_a == "Produzir bile"
    assert output.resposta_correta == "A"
    assert output.nivel_dificuldade == 1
    assert output.tipo_enunciado == "conceitual"


def test_criador_output_invalid_resposta_correta():
    """Test CriadorOutput rejects invalid resposta_correta."""
    data = {
        "enunciado": "Teste",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "E",  # Invalid! Must be A, B, C, or D
        "objetivo_educacional": "Teste",
        "nivel_dificuldade": 1,
        "tipo_enunciado": "conceitual",
    }

    with pytest.raises(ValidationError) as exc_info:
        CriadorOutput(**data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("resposta_correta",) for error in errors)


def test_criador_output_strict_mode_no_coercion():
    """Test that strict mode prevents type coercion for nivel_dificuldade."""
    data = {
        "enunciado": "Teste",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "A",
        "objetivo_educacional": "Teste",
        "nivel_dificuldade": "1",  # String instead of int - should fail in strict mode
        "tipo_enunciado": "conceitual",
    }

    with pytest.raises(ValidationError) as exc_info:
        CriadorOutput(**data)

    # Strict mode: no coercion from "1" to 1
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("nivel_dificuldade",) for error in errors)


def test_criador_output_invalid_nivel_dificuldade():
    """Test CriadorOutput rejects nivel_dificuldade outside 1-3."""
    data = {
        "enunciado": "Teste",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "A",
        "objetivo_educacional": "Teste",
        "nivel_dificuldade": 4,  # Invalid! Must be 1, 2, or 3
        "tipo_enunciado": "conceitual",
    }

    with pytest.raises(ValidationError) as exc_info:
        CriadorOutput(**data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("nivel_dificuldade",) for error in errors)


def test_criador_output_json_serialization():
    """Test CriadorOutput can serialize to/from JSON."""
    import json

    original = CriadorOutput(
        enunciado="Teste questão",
        alternativa_a="Opção A",
        alternativa_b="Opção B",
        alternativa_c="Opção C",
        alternativa_d="Opção D",
        resposta_correta="B",
        objetivo_educacional="Testar serialização",
        nivel_dificuldade=2,
        tipo_enunciado="caso clínico",
    )

    # Serialize to JSON
    json_str = original.model_dump_json()

    # Deserialize back
    data = json.loads(json_str)
    reconstructed = CriadorOutput(**data)

    assert reconstructed.enunciado == original.enunciado
    assert reconstructed.resposta_correta == original.resposta_correta
    assert reconstructed.nivel_dificuldade == original.nivel_dificuldade


def test_question_record_valid_all_26_columns():
    """Test QuestionRecord with all 26 required columns."""
    data = {
        # Base fields (4)
        "tema": "Gastroenterologia",
        "foco": "Fígado",
        "sub_foco": "Funções hepáticas",
        "periodo": "2026-01",
        # Question fields from CriadorOutput (7)
        "nivel_dificuldade": 1,
        "tipo_enunciado": "conceitual",
        "enunciado": "Qual é a função principal do fígado?",
        "alternativa_a": "Produzir bile",
        "alternativa_b": "Filtrar sangue",
        "alternativa_c": "Produzir insulina",
        "alternativa_d": "Armazenar vitaminas",
        "resposta_correta": "A",
        "objetivo_educacional": "Identificar funções hepáticas",
        # Comment fields from ComentadorOutput (8)
        "comentario_introducao": "O fígado é um órgão vital...",
        "comentario_visao_especifica": "A produção de bile...",
        "comentario_alt_a": "Correto! O fígado produz bile.",
        "comentario_alt_b": "Incorreto. A filtragem é função dos rins.",
        "comentario_alt_c": "Incorreto. Insulina é produzida pelo pâncreas.",
        "comentario_alt_d": "Parcialmente correto, mas não é a principal função.",
        "comentario_visao_aprovado": "Questão aprovada pela visão geral.",
        "referencia_bibliografica": "Guyton & Hall, Fisiologia Médica, 13ª ed.",
        # Metadata (3)
        "modelo_llm": "gpt-4",
        "rodadas_validacao": 1,
        "concordancia_comentador": True,
    }

    record = QuestionRecord(**data)

    # Verify base fields
    assert record.tema == "Gastroenterologia"
    assert record.foco == "Fígado"
    assert record.sub_foco == "Funções hepáticas"
    assert record.periodo == "2026-01"

    # Verify question fields
    assert record.nivel_dificuldade == 1
    assert record.resposta_correta == "A"

    # Verify comment fields
    assert record.comentario_introducao == "O fígado é um órgão vital..."
    assert record.referencia_bibliografica == "Guyton & Hall, Fisiologia Médica, 13ª ed."

    # Verify metadata
    assert record.modelo_llm == "gpt-4"
    assert record.rodadas_validacao == 1
    assert record.concordancia_comentador is True

    # Verify optional fields default to None
    assert record.suporte_imagem is None
    assert record.fonte_imagem is None


def test_question_record_with_optional_image_fields():
    """Test QuestionRecord with optional image support fields."""
    data = {
        "tema": "Cardiologia",
        "foco": "ECG",
        "sub_foco": "Interpretação",
        "periodo": "2026-01",
        "nivel_dificuldade": 2,
        "tipo_enunciado": "imagem",
        "enunciado": "Analise o ECG apresentado.",
        "alternativa_a": "Fibrilação atrial",
        "alternativa_b": "Flutter atrial",
        "alternativa_c": "Taquicardia sinusal",
        "alternativa_d": "Ritmo sinusal normal",
        "resposta_correta": "A",
        "objetivo_educacional": "Identificar arritmias no ECG",
        "comentario_introducao": "A fibrilação atrial...",
        "comentario_visao_especifica": "No ECG apresentado...",
        "comentario_alt_a": "Correto!",
        "comentario_alt_b": "Incorreto.",
        "comentario_alt_c": "Incorreto.",
        "comentario_alt_d": "Incorreto.",
        "comentario_visao_aprovado": "Aprovado.",
        "referencia_bibliografica": "Fonte médica",
        "suporte_imagem": "ecg_fibrilacao_atrial.png",  # Optional field provided
        "fonte_imagem": "Hospital XYZ",  # Optional field provided
        "modelo_llm": "gpt-4",
        "rodadas_validacao": 1,
        "concordancia_comentador": True,
    }

    record = QuestionRecord(**data)

    assert record.suporte_imagem == "ecg_fibrilacao_atrial.png"
    assert record.fonte_imagem == "Hospital XYZ"


def test_question_record_invalid_resposta_correta():
    """Test QuestionRecord rejects invalid resposta_correta."""
    data = {
        "tema": "Tema",
        "foco": "Foco",
        "sub_foco": "Sub",
        "periodo": "2026-01",
        "nivel_dificuldade": 1,
        "tipo_enunciado": "conceitual",
        "enunciado": "Teste",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "X",  # Invalid!
        "objetivo_educacional": "Teste",
        "comentario_introducao": "C1",
        "comentario_visao_especifica": "C2",
        "comentario_alt_a": "C3",
        "comentario_alt_b": "C4",
        "comentario_alt_c": "C5",
        "comentario_alt_d": "C6",
        "comentario_visao_aprovado": "C7",
        "referencia_bibliografica": "Ref",
        "modelo_llm": "gpt-4",
        "rodadas_validacao": 1,
        "concordancia_comentador": True,
    }

    with pytest.raises(ValidationError) as exc_info:
        QuestionRecord(**data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("resposta_correta",) for error in errors)


def test_question_record_different_llm_models():
    """Test QuestionRecord works with different LLM model names."""
    base_data = {
        "tema": "Cardiologia",
        "foco": "Arritmias",
        "sub_foco": "Fibrilação Atrial",
        "periodo": "3º ano",
        "nivel_dificuldade": 2,
        "tipo_enunciado": "caso clínico",
        "enunciado": "Paciente com FA...",
        "alternativa_a": "A",
        "alternativa_b": "B",
        "alternativa_c": "C",
        "alternativa_d": "D",
        "resposta_correta": "A",
        "objetivo_educacional": "Diagnosticar FA",
        "comentario_introducao": "Intro",
        "comentario_visao_especifica": "Visão",
        "comentario_alt_a": "C1",
        "comentario_alt_b": "C2",
        "comentario_alt_c": "C3",
        "comentario_alt_d": "C4",
        "comentario_visao_aprovado": "Aprovado",
        "referencia_bibliografica": "Ref",
        "rodadas_validacao": 1,
        "concordancia_comentador": True,
    }

    # Test with GPT-4
    record_gpt4 = QuestionRecord(**{**base_data, "modelo_llm": "gpt-4"})
    assert record_gpt4.modelo_llm == "gpt-4"

    # Test with GPT-3.5-turbo
    record_gpt35 = QuestionRecord(**{**base_data, "modelo_llm": "gpt-3.5-turbo"})
    assert record_gpt35.modelo_llm == "gpt-3.5-turbo"

    # Test with Claude Sonnet 4.5
    record_claude = QuestionRecord(**{**base_data, "modelo_llm": "claude-sonnet-4.5"})
    assert record_claude.modelo_llm == "claude-sonnet-4.5"

    # Test with Claude Opus
    record_opus = QuestionRecord(**{**base_data, "modelo_llm": "claude-opus-4"})
    assert record_opus.modelo_llm == "claude-opus-4"
