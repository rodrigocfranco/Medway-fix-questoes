"""Question creator agent."""

import logging
import time

from construtor.config.exceptions import OutputParsingError
from construtor.config.prompt_loader import load_prompt
from construtor.config.settings import PipelineConfig
from construtor.models.question import CriadorOutput, SubFocoInput
from construtor.providers.base import LLMProvider

logger = logging.getLogger(__name__)

_DEFAULT_NIVEL_DIFICULDADE = 2


class CriadorAgent:
    """Generates complete questions with enunciado, alternatives, and gabarito.

    Uses an LLM to create medical questions with specific difficulty level,
    question type, and pre-determined correct answer position. Follows Bloom's
    taxonomy for difficulty levels and generates cognitive distractors based on
    student error patterns.

    Args:
        provider: LLM provider for generation calls.
        config: Pipeline configuration with model and temperature.

    Example:
        agent = CriadorAgent(provider, config)
        output = await agent.create_question(
            subfoco_input,
            posicao_correta="B",
            nivel_dificuldade=2
        )
        # Returns CriadorOutput with question, alternatives, gabarito
    """

    def __init__(self, provider: LLMProvider, config: PipelineConfig) -> None:
        self._provider = provider
        self._config = config
        self._prompt_template = load_prompt("criador")

    async def create_question(
        self,
        subfoco_input: SubFocoInput,
        posicao_correta: str,
        nivel_dificuldade: int = _DEFAULT_NIVEL_DIFICULDADE,
    ) -> CriadorOutput:
        """Create a complete question from a sub-foco input.

        Generates a medical question with enunciado (statement), four alternatives,
        correct answer at specified position, educational objective, and question type.
        Validates that the LLM placed the correct answer at the requested position.

        Args:
            subfoco_input: Input with tema, foco, sub_foco, periodo.
            posicao_correta: Pre-determined position for correct answer (A/B/C/D).
            nivel_dificuldade: Difficulty level 1-3 (Bloom taxonomy), default 2.
                1 = Remember/Understand (basic concepts, definitions)
                2 = Apply/Analyze (clinical application, case analysis)
                3 = Evaluate/Create (complex decision-making, synthesis)

        Returns:
            CriadorOutput with enunciado, alternatives, gabarito, objective.

        Raises:
            OutputParsingError: If generation fails or position validation fails.
            ValueError: If posicao_correta is not A/B/C/D or nivel_dificuldade not 1-3.
        """
        # Validate inputs
        if posicao_correta not in {"A", "B", "C", "D"}:
            msg = f"posicao_correta must be A/B/C/D, got '{posicao_correta}'"
            raise ValueError(msg)

        if nivel_dificuldade not in {1, 2, 3}:
            msg = f"nivel_dificuldade must be 1-3, got {nivel_dificuldade}"
            raise ValueError(msg)

        # Format prompt with all required variables
        # Wrap in try/except to catch template errors early (missing/extra placeholders)
        try:
            prompt = self._prompt_template.format(
                tema=subfoco_input.tema,
                foco=subfoco_input.foco,
                sub_foco=subfoco_input.sub_foco,
                periodo=subfoco_input.periodo,
                posicao_correta=posicao_correta,
                nivel_dificuldade=nivel_dificuldade,
            )
        except KeyError as e:
            msg = f"Prompt template missing required placeholder or has extra placeholder: {e}"
            raise ValueError(msg) from e

        # Call LLM provider with structured output
        start = time.monotonic()
        try:
            response = await self._provider.generate(
                prompt=prompt,
                model=self._config.default_model,
                temperature=self._config.temperature,
                response_model=CriadorOutput,
            )
        except Exception as e:
            msg = (
                f"Failed to generate question from LLM | "
                f"sub_foco={subfoco_input.sub_foco} | nivel={nivel_dificuldade} | "
                f"posicao={posicao_correta}"
            )
            raise OutputParsingError(
                msg,
                foco=subfoco_input.foco,
                modelo=self._config.default_model,
            ) from e

        latency = time.monotonic() - start

        criador_output: CriadorOutput = response["content"]

        # Validate correct answer position (CRITICAL!)
        if criador_output.resposta_correta != posicao_correta:
            msg = (
                f"LLM returned incorrect position: expected {posicao_correta}, "
                f"got {criador_output.resposta_correta} | "
                f"sub_foco={subfoco_input.sub_foco} | nivel={nivel_dificuldade}"
            )
            raise OutputParsingError(
                msg,
                foco=subfoco_input.foco,
                modelo=self._config.default_model,
            )

        # Log success with all metrics
        logger.info(
            "Question created | sub_foco=%s | nivel=%d | tipo=%s | posicao=%s | "
            "modelo=%s | tokens=%d | cost=%.4f | latency=%.2fs",
            subfoco_input.sub_foco,
            nivel_dificuldade,
            criador_output.tipo_enunciado,
            posicao_correta,
            self._config.default_model,
            response["tokens_used"],
            response["cost"],
            latency,
        )

        return criador_output
