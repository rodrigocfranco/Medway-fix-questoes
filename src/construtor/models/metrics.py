"""Metrics models for question generation analytics and model comparison."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuestionMetrics(BaseModel):
    """Per-question generation and validation metrics.

    Tracks resource consumption, timing, and outcome for each
    individual question generated in the pipeline. Used for
    cost tracking, performance monitoring, and dashboard analytics.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    modelo: str
    tokens: int = Field(..., ge=0, description="Total tokens consumed")
    custo: float = Field(..., ge=0.0, description="Cost in dollars")
    rodadas: int = Field(..., ge=0, description="Number of retry rounds before approval/rejection")
    tempo: float = Field(..., gt=0.0, description="Duration in seconds")
    decisao: Literal["aprovada", "rejeitada", "failed"]
    timestamp: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        description="Timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
    )


class BatchMetrics(BaseModel):
    """Batch-level aggregated metrics.

    Aggregates metrics across all questions in a batch,
    providing summary statistics for approval rates,
    costs, and timing.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    total_questoes: int = Field(..., ge=0)
    aprovadas: int = Field(..., ge=0)
    rejeitadas: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    custo_total: float = Field(..., ge=0.0)
    tempo_total: float = Field(..., ge=0.0)
    taxa_aprovacao: float = Field(..., ge=0.0, le=1.0)


class ModelComparison(BaseModel):
    """Model performance comparison metrics.

    Enables comparison of different LLM models based on
    quality (approval rate, agreement), cost, and latency.
    Used in the dashboard for model selection decisions.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    modelo: str
    questoes_geradas: int = Field(..., ge=0)
    taxa_aprovacao: float = Field(..., ge=0.0, le=1.0)
    custo_medio: float = Field(..., ge=0.0)
    latencia_media: float = Field(..., ge=0.0, description="Average latency in seconds")
    taxa_concordancia: float = Field(..., ge=0.0, le=1.0, description="Agreement rate with commentator")
