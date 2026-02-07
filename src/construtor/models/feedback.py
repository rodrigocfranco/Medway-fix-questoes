"""Feedback models for Comentador and Validador agents."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FeedbackEstruturado(BaseModel):
    """Structured error categories for question validation feedback.

    This model categorizes validation issues into specific boolean flags
    that indicate different types of problems with a question. Used by
    the Validador agent to provide structured rejection feedback.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    enunciado_ambiguo: bool = Field(
        default=False,
        description="Enunciado confuso ou ambíguo",
    )
    distratores_fracos: bool = Field(
        default=False,
        description="Alternativas incorretas óbvias demais",
    )
    gabarito_questionavel: bool = Field(
        default=False,
        description="Resposta correta discutível ou controversa",
    )
    comentario_incompleto: bool = Field(
        default=False,
        description="Comentário não cobre todas as seções esperadas",
    )
    fora_do_nivel: bool = Field(
        default=False,
        description="Dificuldade não corresponde ao nível especificado",
    )
    observacoes: str | None = Field(
        default=None,
        description="Detalhes adicionais sobre os problemas identificados",
    )


class ComentadorOutput(BaseModel):
    """Output from blind review commentator agent (Comentador).

    This model represents the structured output from the Comentador agent,
    which performs blind review of questions without seeing the correct answer,
    then provides comprehensive comments for all alternatives and declares
    which alternative it believes is correct.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    resposta_declarada: Literal["A", "B", "C", "D"] = Field(
        ...,
        description="Alternativa que o comentador considera correta (revisão cega)",
    )
    comentario_introducao: str
    comentario_visao_especifica: str
    comentario_alt_a: str
    comentario_alt_b: str
    comentario_alt_c: str
    comentario_alt_d: str
    comentario_visao_aprovado: str
    referencia_bibliografica: str = Field(
        ...,
        description="Fonte bibliográfica verificável obtida do Pinecone RAG",
    )


class ValidadorOutput(BaseModel):
    """Output from validator agent (Validador).

    This model represents the validation decision combining the Criador's
    output with the Comentador's blind review. It includes the approval/rejection
    decision, whether the commentator agreed with the correct answer, and
    structured feedback explaining any issues found.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    decisao: Literal["aprovada", "rejeitada"] = Field(
        ...,
        description="Decisão de aprovação ou rejeição da questão",
    )
    concordancia: bool = Field(
        ...,
        description="Se o comentador concordou com a resposta correta declarada",
    )
    feedback_estruturado: FeedbackEstruturado = Field(
        ...,
        description="Categorias estruturadas de erro identificados",
    )
