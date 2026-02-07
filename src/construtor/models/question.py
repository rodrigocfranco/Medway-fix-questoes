"""Question models for Criador agent output and complete question records."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CriadorOutput(BaseModel):
    """Output from question creator agent (Criador).

    This model represents the structured output from the Criador agent,
    containing the question statement, alternatives, correct answer,
    educational objective, difficulty level, and question type.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    # Required fields - Portuguese domain terminology
    enunciado: str = Field(..., description="Texto completo do enunciado da questão")
    alternativa_a: str = Field(..., description="Primeira alternativa")
    alternativa_b: str = Field(..., description="Segunda alternativa")
    alternativa_c: str = Field(..., description="Terceira alternativa")
    alternativa_d: str = Field(..., description="Quarta alternativa")
    resposta_correta: Literal["A", "B", "C", "D"] = Field(
        ...,
        description="Letra da resposta correta",
    )
    objetivo_educacional: str = Field(..., description="Objetivo pedagógico da questão")
    nivel_dificuldade: Literal[1, 2, 3] = Field(
        ...,
        description=(
            "Nível de dificuldade mapeado à Taxonomia de Bloom: "
            "1=Conhecimento/Compreensão (fácil), "
            "2=Aplicação/Análise (médio), "
            "3=Síntese/Avaliação (difícil)"
        ),
    )
    tipo_enunciado: str = Field(
        ...,
        description="Tipo do enunciado: conceitual, caso clínico, etc.",
    )


class QuestionRecord(BaseModel):
    """Complete question record with all 26 columns for Excel export.

    This model represents the final question record that will be exported
    to Excel, combining data from Criador, Comentador, and Validador agents,
    plus metadata and optional image support fields.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    # Base fields (4 columns)
    tema: str = Field(..., description="Tema médico da questão (ex: Gastroenterologia)")
    foco: str = Field(..., description="Foco específico dentro do tema (ex: Fígado)")
    sub_foco: str = Field(..., description="Sub-foco detalhado (ex: Funções hepáticas)")
    periodo: str = Field(..., description="Período do curso médico (1º ano, 2º ano, etc.)")

    # Question fields from CriadorOutput (7 columns)
    nivel_dificuldade: Literal[1, 2, 3] = Field(
        ...,
        description="Nível de dificuldade: 1=fácil, 2=médio, 3=difícil",
    )
    tipo_enunciado: str = Field(
        ...,
        description="Tipo do enunciado: conceitual, caso clínico, etc.",
    )
    enunciado: str = Field(..., description="Texto completo do enunciado da questão")
    alternativa_a: str = Field(..., description="Primeira alternativa")
    alternativa_b: str = Field(..., description="Segunda alternativa")
    alternativa_c: str = Field(..., description="Terceira alternativa")
    alternativa_d: str = Field(..., description="Quarta alternativa")
    resposta_correta: Literal["A", "B", "C", "D"] = Field(
        ...,
        description="Letra da resposta correta",
    )
    objetivo_educacional: str = Field(..., description="Objetivo pedagógico da questão")

    # Comment fields from ComentadorOutput (8 columns)
    comentario_introducao: str = Field(
        ...,
        description="Comentário introdutório contextualizando o tema",
    )
    comentario_visao_especifica: str = Field(
        ...,
        description="Análise específica do enunciado e contexto clínico",
    )
    comentario_alt_a: str = Field(
        ...,
        description="Comentário explicativo da alternativa A",
    )
    comentario_alt_b: str = Field(
        ...,
        description="Comentário explicativo da alternativa B",
    )
    comentario_alt_c: str = Field(
        ...,
        description="Comentário explicativo da alternativa C",
    )
    comentario_alt_d: str = Field(
        ...,
        description="Comentário explicativo da alternativa D",
    )
    comentario_visao_aprovado: str = Field(
        ...,
        description="Visão geral do aprovado com síntese final",
    )
    referencia_bibliografica: str = Field(
        ...,
        description="Fonte bibliográfica verificável obtida do Pinecone RAG",
    )

    # Image support fields - optional (2 columns)
    suporte_imagem: str | None = Field(
        default=None,
        description="Nome do arquivo de imagem de suporte (se aplicável)",
    )
    fonte_imagem: str | None = Field(
        default=None,
        description="Fonte ou crédito da imagem utilizada",
    )

    # Metadata fields (3 columns)
    modelo_llm: str = Field(
        ...,
        description="Modelo de LLM utilizado (ex: gpt-4, claude-sonnet-4.5)",
    )
    rodadas_validacao: int = Field(
        ...,
        ge=1,
        description="Número de rodadas de validação até aprovação/rejeição",
    )
    concordancia_comentador: bool = Field(
        ...,
        description="Se o comentador concordou com o gabarito declarado",
    )
