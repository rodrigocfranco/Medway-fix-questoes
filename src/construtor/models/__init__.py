"""Pydantic models for question generation pipeline.

This module provides type-safe data models for all pipeline stages:
- Question models (CriadorOutput, QuestionRecord)
- Feedback models (FeedbackEstruturado, ComentadorOutput, ValidadorOutput)
- Pipeline models (BatchState, CheckpointResult, RetryContext)
- Metrics models (QuestionMetrics, BatchMetrics, ModelComparison)

All models use strict validation mode (ConfigDict(strict=True)) to prevent
type coercion and ensure data integrity across agent boundaries.
"""

# ruff: noqa: I001
# Question models
from .question import CriadorOutput, QuestionRecord

# Feedback models
from .feedback import ComentadorOutput, FeedbackEstruturado, ValidadorOutput

# Metrics models
from .metrics import BatchMetrics, ModelComparison, QuestionMetrics

# Pipeline models
from .pipeline import BatchState, CheckpointResult, RetryContext

__all__ = [
    "BatchMetrics",
    "BatchState",
    "CheckpointResult",
    "ComentadorOutput",
    "CriadorOutput",
    "FeedbackEstruturado",
    "ModelComparison",
    "QuestionMetrics",
    "QuestionRecord",
    "RetryContext",
    "ValidadorOutput",
]
