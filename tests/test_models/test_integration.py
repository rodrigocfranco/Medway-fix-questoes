"""Integration tests validating model contracts across pipeline workflow.

This module tests the complete workflow chain:
CriadorOutput → ComentadorOutput → ValidadorOutput → QuestionRecord

Validates that models compose correctly and field mappings work end-to-end.
"""

import pytest

from construtor.models import (
    ComentadorOutput,
    CriadorOutput,
    FeedbackEstruturado,
    QuestionRecord,
    ValidadorOutput,
)


def test_complete_workflow_approved_question():
    """Test complete workflow from Criador to QuestionRecord for approved question.

    This validates the entire pipeline:
    1. Criador generates question
    2. Comentador reviews blindly and agrees with answer
    3. Validador approves based on agreement
    4. All data combines into QuestionRecord
    """
    # Step 1: Criador generates a question
    criador_output = CriadorOutput(
        enunciado="Qual é a principal função do fígado no metabolismo de lipídios?",
        alternativa_a="Produção de bile para emulsificação de gorduras",
        alternativa_b="Armazenamento de triglicerídeos",
        alternativa_c="Síntese de lipoproteínas de alta densidade (HDL)",
        alternativa_d="Absorção de vitaminas lipossolúveis",
        resposta_correta="A",
        objetivo_educacional="Identificar a função hepática no metabolismo lipídico",
        nivel_dificuldade=1,
        tipo_enunciado="conceitual",
    )

    # Step 2: Comentador reviews blindly (agrees with gabarito)
    comentador_output = ComentadorOutput(
        resposta_declarada="A",  # Agrees with Criador's answer
        comentario_introducao="O fígado desempenha papel central no metabolismo de lipídios.",
        comentario_visao_especifica="A bile é essencial para a digestão e absorção de gorduras.",
        comentario_alt_a="Correto! A bile produzida pelo fígado emulsifica gorduras, facilitando a ação das lipases.",
        comentario_alt_b="Incorreto. O armazenamento é função secundária, não a principal.",
        comentario_alt_c="Incorreto. A síntese de HDL é importante, mas não é a função primária.",
        comentario_alt_d="Incorreto. A absorção ocorre no intestino, não no fígado.",
        comentario_visao_aprovado="Questão clara e pedagogicamente adequada para o nível 1.",
        referencia_bibliografica="Guyton & Hall, Tratado de Fisiologia Médica, 13ª ed., Cap. 70",
    )

    # Step 3: Validador approves (concordancia = True, no errors)
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=False,
        distratores_fracos=False,
        gabarito_questionavel=False,
        comentario_incompleto=False,
        fora_do_nivel=False,
    )

    validador_output = ValidadorOutput(
        decisao="aprovada",
        concordancia=True,  # Comentador agreed with gabarito
        feedback_estruturado=feedback,
    )

    # Step 4: Combine all into QuestionRecord
    question_record = QuestionRecord(
        # Base metadata
        tema="Gastroenterologia",
        foco="Fígado",
        sub_foco="Metabolismo de Lipídios",
        periodo="2º ano",
        # From CriadorOutput
        nivel_dificuldade=criador_output.nivel_dificuldade,
        tipo_enunciado=criador_output.tipo_enunciado,
        enunciado=criador_output.enunciado,
        alternativa_a=criador_output.alternativa_a,
        alternativa_b=criador_output.alternativa_b,
        alternativa_c=criador_output.alternativa_c,
        alternativa_d=criador_output.alternativa_d,
        resposta_correta=criador_output.resposta_correta,
        objetivo_educacional=criador_output.objetivo_educacional,
        # From ComentadorOutput
        comentario_introducao=comentador_output.comentario_introducao,
        comentario_visao_especifica=comentador_output.comentario_visao_especifica,
        comentario_alt_a=comentador_output.comentario_alt_a,
        comentario_alt_b=comentador_output.comentario_alt_b,
        comentario_alt_c=comentador_output.comentario_alt_c,
        comentario_alt_d=comentador_output.comentario_alt_d,
        comentario_visao_aprovado=comentador_output.comentario_visao_aprovado,
        referencia_bibliografica=comentador_output.referencia_bibliografica,
        # Metadata
        modelo_llm="gpt-4",
        rodadas_validacao=1,
        concordancia_comentador=validador_output.concordancia,
    )

    # Validate the complete record
    assert question_record.resposta_correta == "A"
    assert question_record.concordancia_comentador is True
    assert question_record.nivel_dificuldade == 1
    assert "lipídios" in question_record.enunciado.lower()
    assert "bile" in question_record.alternativa_a.lower()
    assert "Guyton" in question_record.referencia_bibliografica


def test_complete_workflow_rejected_question():
    """Test complete workflow for rejected question due to disagreement.

    Validates retry scenario:
    1. Criador generates question
    2. Comentador disagrees with gabarito
    3. Validador rejects with structured feedback
    """
    # Step 1: Criador generates a question (with questionable gabarito)
    criador_output = CriadorOutput(
        enunciado="Qual é o principal hormônio produzido pelo pâncreas endócrino?",
        alternativa_a="Insulina",
        alternativa_b="Glucagon",
        alternativa_c="Somatostatina",
        alternativa_d="Polipeptídeo pancreático",
        resposta_correta="B",  # Debatable - both A and B are valid
        objetivo_educacional="Identificar hormônios pancreáticos",
        nivel_dificuldade=1,
        tipo_enunciado="conceitual",
    )

    # Step 2: Comentador reviews blindly (disagrees - chooses A instead of B)
    comentador_output = ComentadorOutput(
        resposta_declarada="A",  # Disagrees with Criador's "B"
        comentario_introducao="O pâncreas endócrino produz múltiplos hormônios reguladores.",
        comentario_visao_especifica="A insulina é quantitativamente o hormônio mais abundante.",
        comentario_alt_a="Correto! A insulina é produzida pelas células beta em maior quantidade.",
        comentario_alt_b="Também correto, mas em menor quantidade que insulina.",
        comentario_alt_c="Incorreto. Hormônio regulador, mas não o principal.",
        comentario_alt_d="Incorreto. Função menos conhecida.",
        comentario_visao_aprovado="Enunciado ambíguo - 'principal' pode significar quantidade ou importância.",
        referencia_bibliografica="Ganong, Fisiologia Médica, 25ª ed.",
    )

    # Step 3: Validador rejects due to disagreement
    feedback = FeedbackEstruturado(
        enunciado_ambiguo=True,  # "principal" é ambíguo
        distratores_fracos=False,
        gabarito_questionavel=True,  # Both A and B are valid
        comentario_incompleto=False,
        fora_do_nivel=False,
        observacoes='O termo "principal" é ambíguo - pode ser por quantidade ou importância funcional.',
    )

    validador_output = ValidadorOutput(
        decisao="rejeitada",
        concordancia=False,  # Comentador chose A, gabarito was B
        feedback_estruturado=feedback,
    )

    # Validate rejection logic
    assert validador_output.decisao == "rejeitada"
    assert validador_output.concordancia is False
    assert validador_output.feedback_estruturado.enunciado_ambiguo is True
    assert validador_output.feedback_estruturado.gabarito_questionavel is True
    assert "ambíguo" in validador_output.feedback_estruturado.observacoes


def test_field_mapping_criador_to_question_record():
    """Test that all CriadorOutput fields map correctly to QuestionRecord."""
    criador = CriadorOutput(
        enunciado="Test enunciado",
        alternativa_a="Alt A",
        alternativa_b="Alt B",
        alternativa_c="Alt C",
        alternativa_d="Alt D",
        resposta_correta="C",
        objetivo_educacional="Test objetivo",
        nivel_dificuldade=2,
        tipo_enunciado="caso clínico",
    )

    # Create QuestionRecord using Criador fields
    record = QuestionRecord(
        tema="Test",
        foco="Test",
        sub_foco="Test",
        periodo="1º ano",
        # Map from Criador
        nivel_dificuldade=criador.nivel_dificuldade,
        tipo_enunciado=criador.tipo_enunciado,
        enunciado=criador.enunciado,
        alternativa_a=criador.alternativa_a,
        alternativa_b=criador.alternativa_b,
        alternativa_c=criador.alternativa_c,
        alternativa_d=criador.alternativa_d,
        resposta_correta=criador.resposta_correta,
        objetivo_educacional=criador.objetivo_educacional,
        # Dummy values for other fields
        comentario_introducao="C1",
        comentario_visao_especifica="C2",
        comentario_alt_a="C3",
        comentario_alt_b="C4",
        comentario_alt_c="C5",
        comentario_alt_d="C6",
        comentario_visao_aprovado="C7",
        referencia_bibliografica="Ref",
        modelo_llm="gpt-4",
        rodadas_validacao=1,
        concordancia_comentador=True,
    )

    # Validate all mapped fields match
    assert record.nivel_dificuldade == criador.nivel_dificuldade
    assert record.tipo_enunciado == criador.tipo_enunciado
    assert record.enunciado == criador.enunciado
    assert record.alternativa_a == criador.alternativa_a
    assert record.alternativa_b == criador.alternativa_b
    assert record.alternativa_c == criador.alternativa_c
    assert record.alternativa_d == criador.alternativa_d
    assert record.resposta_correta == criador.resposta_correta
    assert record.objetivo_educacional == criador.objetivo_educacional


def test_comentador_resposta_declarada_matches_literal():
    """Test that Comentador's resposta_declarada uses same Literal as CriadorOutput."""
    # Both should accept A, B, C, D
    for letra in ["A", "B", "C", "D"]:
        comentador = ComentadorOutput(
            resposta_declarada=letra,
            comentario_introducao="Intro",
            comentario_visao_especifica="Visão",
            comentario_alt_a="C1",
            comentario_alt_b="C2",
            comentario_alt_c="C3",
            comentario_alt_d="C4",
            comentario_visao_aprovado="Aprovado",
            referencia_bibliografica="Ref",
        )
        assert comentador.resposta_declarada == letra

    # Both should reject E
    with pytest.raises(Exception):  # ValidationError from Pydantic
        ComentadorOutput(
            resposta_declarada="E",
            comentario_introducao="Intro",
            comentario_visao_especifica="Visão",
            comentario_alt_a="C1",
            comentario_alt_b="C2",
            comentario_alt_c="C3",
            comentario_alt_d="C4",
            comentario_visao_aprovado="Aprovado",
            referencia_bibliografica="Ref",
        )
