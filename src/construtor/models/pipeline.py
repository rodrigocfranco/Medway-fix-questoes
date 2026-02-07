"""Pipeline state and checkpoint models for batch processing."""


from pydantic import BaseModel, ConfigDict, Field

from .feedback import FeedbackEstruturado


class BatchState(BaseModel):
    """Current state of batch processing pipeline.

    Tracks the current position in the batch processing workflow,
    enabling crash recovery and progress monitoring.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    foco_atual: str
    sub_foco_atual: int = Field(..., ge=0)
    total_processados: int = Field(..., ge=0)
    timestamp: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        description="Timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
    )


class CheckpointResult(BaseModel):
    """Checkpoint validation data for batch quality control.

    Contains aggregated metrics for a checkpoint (every 10 focos),
    including approval rates, agreement rates, cost tracking,
    and sample question IDs for manual review.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    checkpoint_id: str
    foco_range: str  # e.g., "Focos 1-10"
    total_geradas: int = Field(..., ge=0)
    aprovadas: int = Field(..., ge=0)
    rejeitadas: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    taxa_aprovacao: float = Field(..., ge=0.0, le=1.0)
    concordancia_media: float = Field(..., ge=0.0, le=1.0)
    custo_total: float = Field(..., ge=0.0)
    sample_question_ids: list[int]


class RetryContext(BaseModel):
    """Context for retry logic with structured feedback.

    Maintains state during question regeneration cycles,
    tracking the current retry attempt and the structured
    feedback that triggered the retry.
    """

    # MANDATORY: Strict validation - no type coercion
    model_config = ConfigDict(strict=True)

    rodada_atual: int = Field(..., ge=1, description="Current retry round (starts at 1)")
    feedback_estruturado: FeedbackEstruturado
    question_id: int | None = None
