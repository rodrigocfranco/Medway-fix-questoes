"""Agents module for question generation pipeline.

This module contains AI agents that perform specific tasks in the pipeline:
- SubFocoGenerator: Generates specific sub-focos from a general foco
- CriadorAgent: Creates multiple-choice questions
- (Future) ComentadorAgent: Generates educational comments
- (Future) ValidadorAgent: Validates question quality
"""

from construtor.agents.criador import CriadorAgent
from construtor.agents.subfoco_generator import SubFocoGenerator

__all__ = [
    "CriadorAgent",
    "SubFocoGenerator",
]
