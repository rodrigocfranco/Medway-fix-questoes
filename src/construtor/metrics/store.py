"""SQLite persistence layer for pipeline state and metrics.

This module provides the MetricsStore class for persisting question records,
metrics, checkpoints, and batch state to a SQLite database with WAL mode
for non-blocking concurrent reads during writes.
"""

import json
import logging
import sqlite3
from pathlib import Path

from construtor.config.exceptions import PipelineError
from construtor.models import BatchState, CheckpointResult, QuestionMetrics, QuestionRecord

logger = logging.getLogger(__name__)


class MetricsStore:
    """SQLite persistence layer for pipeline state and metrics.

    Provides atomic writes with transaction support, WAL mode for concurrent
    reads, and comprehensive methods for storing and retrieving questions,
    metrics, checkpoints, and batch progress.

    Args:
        db_path: Path to SQLite database file (created if not exists).
                 Defaults to "output/pipeline_state.db".

    Examples:
        >>> store = MetricsStore("output/pipeline_state.db")
        >>> question_id = store.save_question(question_record)
        >>> store.update_question_status(question_id, "approved")
    """

    def __init__(self, db_path: str = "output/pipeline_state.db") -> None:
        """Initialize database connection and create tables.

        Args:
            db_path: Path to SQLite database file
        """
        # Create output directory if needed
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # Connect to database
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Dict-like access to rows

        # Enable critical PRAGMAs
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA synchronous=NORMAL")

        # Create tables
        self._create_tables()

        logger.info(f"MetricsStore initialized with database: {db_path}")

    def _create_tables(self) -> None:
        """Create all tables with proper schema."""
        cursor = self.conn.cursor()

        # Questions table (maps to QuestionRecord with 26 fields + metadata)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema TEXT NOT NULL,
                foco TEXT NOT NULL,
                sub_foco TEXT NOT NULL,
                periodo TEXT NOT NULL,
                nivel_dificuldade INTEGER NOT NULL CHECK(nivel_dificuldade IN (1, 2, 3)),
                tipo_enunciado TEXT NOT NULL,
                enunciado TEXT NOT NULL,
                alternativa_a TEXT NOT NULL,
                alternativa_b TEXT NOT NULL,
                alternativa_c TEXT NOT NULL,
                alternativa_d TEXT NOT NULL,
                resposta_correta TEXT NOT NULL CHECK(resposta_correta IN ('A', 'B', 'C', 'D')),
                objetivo_educacional TEXT NOT NULL,
                comentario_introducao TEXT NOT NULL,
                comentario_visao_especifica TEXT NOT NULL,
                comentario_alt_a TEXT NOT NULL,
                comentario_alt_b TEXT NOT NULL,
                comentario_alt_c TEXT NOT NULL,
                comentario_alt_d TEXT NOT NULL,
                comentario_visao_aprovado TEXT NOT NULL,
                referencia_bibliografica TEXT NOT NULL,
                suporte_imagem TEXT,
                fonte_imagem TEXT,
                modelo_llm TEXT NOT NULL,
                rodadas_validacao INTEGER NOT NULL CHECK(rodadas_validacao >= 1),
                concordancia_comentador INTEGER NOT NULL CHECK(concordancia_comentador IN (0, 1)),
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'approved', 'rejected', 'failed')),
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT
            )
        """)

        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                modelo TEXT NOT NULL,
                tokens INTEGER NOT NULL CHECK(tokens >= 0),
                custo REAL NOT NULL CHECK(custo >= 0.0),
                rodadas INTEGER NOT NULL CHECK(rodadas >= 0),
                tempo REAL NOT NULL CHECK(tempo > 0.0),
                decisao TEXT NOT NULL CHECK(decisao IN ('aprovada', 'rejeitada', 'failed')),
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        """)

        # Checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkpoint_id TEXT NOT NULL UNIQUE,
                foco_range TEXT NOT NULL,
                total_geradas INTEGER NOT NULL CHECK(total_geradas >= 0),
                aprovadas INTEGER NOT NULL CHECK(aprovadas >= 0),
                rejeitadas INTEGER NOT NULL CHECK(rejeitadas >= 0),
                failed INTEGER NOT NULL CHECK(failed >= 0),
                taxa_aprovacao REAL NOT NULL
                    CHECK(taxa_aprovacao >= 0.0 AND taxa_aprovacao <= 1.0),
                concordancia_media REAL NOT NULL
                    CHECK(concordancia_media >= 0.0 AND concordancia_media <= 1.0),
                custo_total REAL NOT NULL CHECK(custo_total >= 0.0),
                sample_question_ids TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Batch state table (single row)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_state (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                foco_atual TEXT NOT NULL,
                sub_foco_atual INTEGER NOT NULL CHECK(sub_foco_atual >= 0),
                total_processados INTEGER NOT NULL CHECK(total_processados >= 0),
                timestamp TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Balancer state table (single row)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balancer_state (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                position_a INTEGER NOT NULL DEFAULT 0,
                position_b INTEGER NOT NULL DEFAULT 0,
                position_c INTEGER NOT NULL DEFAULT 0,
                position_d INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Create indexes for frequent queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_question_id ON metrics(question_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_modelo ON metrics(modelo)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_checkpoints_created_at ON checkpoints(created_at DESC)"
        )

        self.conn.commit()
        logger.info("Database tables created successfully")

    # ========================================================================
    # Questions Table Operations
    # ========================================================================

    def save_question(self, question: QuestionRecord) -> int:
        """Save question record to database.

        Args:
            question: QuestionRecord to save

        Returns:
            ID of saved question

        Raises:
            PipelineError: If database write fails
        """
        try:
            cursor = self.conn.cursor()

            # Convert Pydantic to dict
            data = question.model_dump()

            # Convert boolean to integer (SQLite doesn't have BOOLEAN)
            data["concordancia_comentador"] = int(data["concordancia_comentador"])

            # INSERT with all 26 fields using RETURNING clause
            cursor.execute(
                """
                INSERT INTO questions (
                    tema, foco, sub_foco, periodo, nivel_dificuldade,
                    tipo_enunciado, enunciado, alternativa_a, alternativa_b,
                    alternativa_c, alternativa_d, resposta_correta,
                    objetivo_educacional, comentario_introducao,
                    comentario_visao_especifica, comentario_alt_a,
                    comentario_alt_b, comentario_alt_c, comentario_alt_d,
                    comentario_visao_aprovado, referencia_bibliografica,
                    suporte_imagem, fonte_imagem, modelo_llm,
                    rodadas_validacao, concordancia_comentador
                ) VALUES (
                    :tema, :foco, :sub_foco, :periodo, :nivel_dificuldade,
                    :tipo_enunciado, :enunciado, :alternativa_a, :alternativa_b,
                    :alternativa_c, :alternativa_d, :resposta_correta,
                    :objetivo_educacional, :comentario_introducao,
                    :comentario_visao_especifica, :comentario_alt_a,
                    :comentario_alt_b, :comentario_alt_c, :comentario_alt_d,
                    :comentario_visao_aprovado, :referencia_bibliografica,
                    :suporte_imagem, :fonte_imagem, :modelo_llm,
                    :rodadas_validacao, :concordancia_comentador
                )
                RETURNING id
            """,
                data,
            )

            question_id = cursor.fetchone()[0]
            self.conn.commit()

            logger.info(f"Question {question_id} saved successfully")
            return question_id

        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Failed to save question: {e}", exc_info=True)
            raise PipelineError(f"Database write failed: {e}") from e

    def update_question_status(self, question_id: int, status: str) -> None:
        """Update question status.

        Args:
            question_id: ID of question to update
            status: New status (pending/approved/rejected/failed)

        Raises:
            PipelineError: If database write fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE questions
                SET status = ?, updated_at = datetime('now')
                WHERE id = ?
            """,
                (status, question_id),
            )
            self.conn.commit()

            logger.info(f"Question {question_id} status updated to {status}")

        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Failed to update question status: {e}", exc_info=True)
            raise PipelineError(f"Database write failed: {e}") from e

    def get_question_by_id(self, question_id: int) -> QuestionRecord | None:
        """Get question by ID.

        Args:
            question_id: ID of question to retrieve

        Returns:
            QuestionRecord if found, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        # Convert row to dict
        data = dict(row)

        # Remove database metadata fields
        data.pop("id", None)
        data.pop("status", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        # Convert integer back to boolean
        data["concordancia_comentador"] = bool(data["concordancia_comentador"])

        # Reconstruct Pydantic model
        return QuestionRecord(**data)

    def get_questions_by_status(self, status: str) -> list[QuestionRecord]:
        """Get all questions with given status.

        Args:
            status: Status to filter by

        Returns:
            List of QuestionRecords with matching status
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE status = ?", (status,))
        rows = cursor.fetchall()

        questions = []
        for row in rows:
            data = dict(row)
            # Remove database metadata
            data.pop("id", None)
            data.pop("status", None)
            data.pop("created_at", None)
            data.pop("updated_at", None)

            # Convert integer to boolean
            data["concordancia_comentador"] = bool(data["concordancia_comentador"])

            questions.append(QuestionRecord(**data))

        return questions

    # ========================================================================
    # Metrics Table Operations
    # ========================================================================

    def save_metrics(self, question_id: int, metrics: QuestionMetrics) -> None:
        """Save metrics for a question.

        Args:
            question_id: ID of associated question
            metrics: QuestionMetrics to save

        Raises:
            PipelineError: If database write fails
        """
        try:
            cursor = self.conn.cursor()
            data = metrics.model_dump()

            cursor.execute(
                """
                INSERT INTO metrics (
                    question_id, modelo, tokens, custo, rodadas,
                    tempo, decisao, timestamp
                ) VALUES (
                    :question_id, :modelo, :tokens, :custo, :rodadas,
                    :tempo, :decisao, :timestamp
                )
            """,
                {
                    "question_id": question_id,
                    **data,
                },
            )

            self.conn.commit()
            logger.info(f"Metrics saved for question {question_id}")

        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Failed to save metrics: {e}", exc_info=True)
            raise PipelineError(f"Database write failed: {e}") from e

    def get_metrics_by_question_id(self, question_id: int) -> QuestionMetrics | None:
        """Get metrics for a question.

        Args:
            question_id: ID of question

        Returns:
            QuestionMetrics if found, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM metrics WHERE question_id = ?", (question_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        data = dict(row)
        # Remove database fields
        data.pop("id", None)
        data.pop("question_id", None)
        data.pop("created_at", None)

        return QuestionMetrics(**data)

    def get_aggregate_metrics(self) -> dict:
        """Get aggregate metrics across all questions.

        Returns:
            Dictionary with aggregate statistics
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                SUM(custo) as total_cost,
                SUM(tokens) as total_tokens,
                AVG(tempo) as avg_latency,
                COUNT(*) as total_questions
            FROM metrics
        """)

        row = cursor.fetchone()

        return {
            "total_cost": row["total_cost"] or 0.0,
            "total_tokens": row["total_tokens"] or 0,
            "avg_latency": row["avg_latency"] or 0.0,
            "total_questions": row["total_questions"] or 0,
        }

    # ========================================================================
    # Checkpoints Table Operations
    # ========================================================================

    def save_checkpoint(self, checkpoint: CheckpointResult) -> int:
        """Save checkpoint result.

        Args:
            checkpoint: CheckpointResult to save

        Returns:
            ID of saved checkpoint

        Raises:
            PipelineError: If database write fails
        """
        try:
            cursor = self.conn.cursor()
            data = checkpoint.model_dump()

            # Convert list to JSON
            data["sample_question_ids"] = json.dumps(data["sample_question_ids"])

            cursor.execute(
                """
                INSERT INTO checkpoints (
                    checkpoint_id, foco_range, total_geradas, aprovadas,
                    rejeitadas, failed, taxa_aprovacao, concordancia_media,
                    custo_total, sample_question_ids
                ) VALUES (
                    :checkpoint_id, :foco_range, :total_geradas, :aprovadas,
                    :rejeitadas, :failed, :taxa_aprovacao, :concordancia_media,
                    :custo_total, :sample_question_ids
                )
                RETURNING id
            """,
                data,
            )

            checkpoint_id = cursor.fetchone()[0]
            self.conn.commit()

            logger.info(f"Checkpoint {checkpoint.checkpoint_id} saved with ID {checkpoint_id}")
            return checkpoint_id

        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Failed to save checkpoint: {e}", exc_info=True)
            raise PipelineError(f"Database write failed: {e}") from e

    def get_checkpoint_by_id(self, checkpoint_id: int) -> CheckpointResult | None:
        """Get checkpoint by ID.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            CheckpointResult if found, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM checkpoints WHERE id = ?", (checkpoint_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        data = dict(row)
        # Remove database fields
        data.pop("id", None)
        data.pop("created_at", None)

        # Deserialize JSON
        data["sample_question_ids"] = json.loads(data["sample_question_ids"])

        return CheckpointResult(**data)

    def get_all_checkpoints(self) -> list[CheckpointResult]:
        """Get all checkpoints ordered by timestamp DESC.

        Returns:
            List of CheckpointResults (most recent first)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM checkpoints ORDER BY created_at DESC, id DESC")
        rows = cursor.fetchall()

        checkpoints = []
        for row in rows:
            data = dict(row)
            data.pop("id", None)
            data.pop("created_at", None)
            data["sample_question_ids"] = json.loads(data["sample_question_ids"])
            checkpoints.append(CheckpointResult(**data))

        return checkpoints

    # ========================================================================
    # Batch Progress Operations
    # ========================================================================

    def save_batch_progress(self, state: BatchState) -> None:
        """Save batch progress state (UPSERT).

        Args:
            state: BatchState to save

        Raises:
            PipelineError: If database write fails
        """
        try:
            cursor = self.conn.cursor()
            data = state.model_dump()

            # UPSERT (INSERT OR REPLACE)
            cursor.execute(
                """
                INSERT OR REPLACE INTO batch_state (
                    id, foco_atual, sub_foco_atual, total_processados, timestamp
                ) VALUES (
                    1, :foco_atual, :sub_foco_atual, :total_processados, :timestamp
                )
            """,
                data,
            )

            self.conn.commit()
            logger.info("Batch progress saved")

        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Failed to save batch progress: {e}", exc_info=True)
            raise PipelineError(f"Database write failed: {e}") from e

    def get_batch_progress(self) -> BatchState | None:
        """Get latest batch progress state.

        Returns:
            BatchState if exists, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM batch_state WHERE id = 1")
        row = cursor.fetchone()

        if row is None:
            return None

        data = dict(row)
        # Remove database fields
        data.pop("id", None)
        data.pop("updated_at", None)

        return BatchState(**data)

    # ========================================================================
    # Balancer State Operations
    # ========================================================================

    def save_balancer_state(self, counts: dict[str, int]) -> None:
        """Save balancer state (UPSERT).

        Args:
            counts: Dictionary with position counts (A, B, C, D)

        Raises:
            PipelineError: If database write fails
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO balancer_state (
                    id, position_a, position_b, position_c, position_d
                ) VALUES (
                    1, :A, :B, :C, :D
                )
            """,
                counts,
            )

            self.conn.commit()
            logger.info("Balancer state saved")

        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Failed to save balancer state: {e}", exc_info=True)
            raise PipelineError(f"Database write failed: {e}") from e

    def get_balancer_state(self) -> dict[str, int] | None:
        """Get balancer state.

        Returns:
            Dictionary with position counts (A, B, C, D) if exists, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM balancer_state WHERE id = 1")
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "A": row["position_a"],
            "B": row["position_b"],
            "C": row["position_c"],
            "D": row["position_d"],
        }

    # ========================================================================
    # Resource Management
    # ========================================================================

    def close(self) -> None:
        """Close database connection.

        Always call this method when done with the store to prevent
        connection leaks.
        """
        self.conn.close()
        logger.info("Database connection closed")

    def __enter__(self) -> "MetricsStore":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: object,
    ) -> bool:
        """Context manager exit - ensures connection cleanup."""
        self.close()
        return False
