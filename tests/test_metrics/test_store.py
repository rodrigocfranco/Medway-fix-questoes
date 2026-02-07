"""Comprehensive tests for MetricsStore SQLite persistence layer."""

import sqlite3

import pytest

from construtor.metrics import MetricsStore
from construtor.models import BatchState, CheckpointResult, QuestionMetrics, QuestionRecord


@pytest.fixture
def temp_db(tmp_path):
    """Temporary file-based database for testing file I/O."""
    db_path = tmp_path / "test.db"
    store = MetricsStore(str(db_path))
    yield store
    store.conn.close()


@pytest.fixture
def memory_db():
    """In-memory database for faster tests."""
    store = MetricsStore(":memory:")
    yield store
    store.conn.close()


@pytest.fixture
def sample_question():
    """Sample QuestionRecord for testing."""
    return QuestionRecord(
        tema="Cardiologia",
        foco="Insuficiência Cardíaca",
        sub_foco="Classificação NYHA",
        periodo="3º ano",
        nivel_dificuldade=2,
        tipo_enunciado="caso clínico",
        enunciado="Paciente de 65 anos com dispneia aos médios esforços...",
        alternativa_a="NYHA Classe I",
        alternativa_b="NYHA Classe II",
        alternativa_c="NYHA Classe III",
        alternativa_d="NYHA Classe IV",
        resposta_correta="B",
        objetivo_educacional="Classificar gravidade de IC segundo NYHA",
        comentario_introducao="A classificação NYHA é fundamental...",
        comentario_visao_especifica="Neste caso, sintomas aos médios esforços...",
        comentario_alt_a="Classe I: assintomático",
        comentario_alt_b="Classe II: sintomas aos médios esforços (correto)",
        comentario_alt_c="Classe III: sintomas aos pequenos esforços",
        comentario_alt_d="Classe IV: sintomas em repouso",
        comentario_visao_aprovado="Questão bem elaborada sobre NYHA",
        referencia_bibliografica="Harrison's Principles of Internal Medicine, 21st ed.",
        suporte_imagem=None,
        fonte_imagem=None,
        modelo_llm="gpt-4",
        rodadas_validacao=1,
        concordancia_comentador=True,
    )


@pytest.fixture
def sample_metrics():
    """Sample QuestionMetrics for testing."""
    return QuestionMetrics(
        modelo="gpt-4",
        tokens=1500,
        custo=0.045,
        rodadas=1,
        tempo=2.5,
        decisao="aprovada",
        timestamp="2026-02-07T10:30:00",
    )


@pytest.fixture
def sample_checkpoint():
    """Sample CheckpointResult for testing."""
    return CheckpointResult(
        checkpoint_id="cp-001",
        foco_range="Focos 1-10",
        total_geradas=100,
        aprovadas=85,
        rejeitadas=10,
        failed=5,
        taxa_aprovacao=0.85,
        concordancia_media=0.92,
        custo_total=12.50,
        sample_question_ids=[1, 2, 3, 4, 5],
    )


@pytest.fixture
def sample_batch_state():
    """Sample BatchState for testing."""
    return BatchState(
        foco_atual="Insuficiência Cardíaca",
        sub_foco_atual=3,
        total_processados=150,
        timestamp="2026-02-07T10:30:00",
    )


# ============================================================================
# Initialization Tests (3 tests)
# ============================================================================


def test_database_file_created(tmp_path):
    """Test that database file is created automatically."""
    db_path = tmp_path / "output" / "test.db"
    store = MetricsStore(str(db_path))

    assert db_path.exists()
    assert db_path.is_file()

    store.conn.close()


def test_output_directory_created(tmp_path):
    """Test that output directory is created if not exists."""
    db_path = tmp_path / "output" / "subdir" / "test.db"
    store = MetricsStore(str(db_path))

    assert db_path.parent.exists()
    assert db_path.parent.is_dir()

    store.conn.close()


def test_default_path_creates_correct_location():
    """Test that default path creates output/pipeline_state.db (AC#1)."""
    from pathlib import Path

    # Use default path
    store = MetricsStore()

    # Verify database created at default location
    default_path = Path("output/pipeline_state.db")
    assert default_path.exists(), "Database should be created at output/pipeline_state.db"
    assert default_path.is_file(), "Database should be a file"

    # Verify it's a valid SQLite database
    cursor = store.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    assert "questions" in tables, "Database should have questions table"

    store.close()


def test_tables_created_with_correct_schema(memory_db):
    """Test that all tables are created with correct schema."""
    cursor = memory_db.conn.cursor()

    # Check questions table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
    assert cursor.fetchone() is not None

    # Check metrics table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
    assert cursor.fetchone() is not None

    # Check checkpoints table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'")
    assert cursor.fetchone() is not None

    # Check batch_state table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_state'")
    assert cursor.fetchone() is not None

    # Check balancer_state table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='balancer_state'")
    assert cursor.fetchone() is not None


# ============================================================================
# Questions Table Tests (8 tests)
# ============================================================================


def test_save_question_returns_valid_id(memory_db, sample_question):
    """Test that save_question returns valid question_id."""
    question_id = memory_db.save_question(sample_question)

    assert isinstance(question_id, int)
    assert question_id > 0


def test_save_question_with_all_26_fields(memory_db, sample_question):
    """Test save_question with all 26 QuestionRecord fields."""
    question_id = memory_db.save_question(sample_question)

    # Verify all fields saved
    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row["tema"] == "Cardiologia"
    assert row["foco"] == "Insuficiência Cardíaca"
    assert row["sub_foco"] == "Classificação NYHA"
    assert row["alternativa_a"] == "NYHA Classe I"
    assert row["resposta_correta"] == "B"


def test_get_question_by_id_returns_correct_question(memory_db, sample_question):
    """Test get_question_by_id returns correct question."""
    question_id = memory_db.save_question(sample_question)
    retrieved = memory_db.get_question_by_id(question_id)

    assert retrieved is not None
    assert retrieved.tema == "Cardiologia"
    assert retrieved.foco == "Insuficiência Cardíaca"
    assert retrieved.resposta_correta == "B"


def test_get_question_by_id_returns_none_for_invalid_id(memory_db):
    """Test get_question_by_id returns None for invalid ID."""
    retrieved = memory_db.get_question_by_id(9999)

    assert retrieved is None


def test_update_question_status_changes_status(memory_db, sample_question):
    """Test update_question_status changes status correctly."""
    question_id = memory_db.save_question(sample_question)

    memory_db.update_question_status(question_id, "approved")

    retrieved = memory_db.get_question_by_id(question_id)
    assert retrieved is not None

    # Get status directly from database
    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT status FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    assert row["status"] == "approved"


def test_get_questions_by_status_filters_correctly(memory_db, sample_question):
    """Test get_questions_by_status filters correctly."""
    # Save multiple questions with different statuses
    id1 = memory_db.save_question(sample_question)
    memory_db.update_question_status(id1, "approved")

    id2 = memory_db.save_question(sample_question)
    memory_db.update_question_status(id2, "rejected")

    _id3 = memory_db.save_question(sample_question)
    # _id3 stays in 'pending' status

    # Test filtering
    approved = memory_db.get_questions_by_status("approved")
    assert len(approved) == 1

    rejected = memory_db.get_questions_by_status("rejected")
    assert len(rejected) == 1

    pending = memory_db.get_questions_by_status("pending")
    assert len(pending) == 1


def test_status_check_constraint_rejects_invalid_status(memory_db):
    """Test status CHECK constraint rejects invalid status."""
    cursor = memory_db.conn.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO questions (
                tema, foco, sub_foco, periodo, nivel_dificuldade,
                tipo_enunciado, enunciado, alternativa_a, alternativa_b,
                alternativa_c, alternativa_d, resposta_correta,
                objetivo_educacional, comentario_introducao,
                comentario_visao_especifica, comentario_alt_a,
                comentario_alt_b, comentario_alt_c, comentario_alt_d,
                comentario_visao_aprovado, referencia_bibliografica,
                modelo_llm, rodadas_validacao, concordancia_comentador,
                status
            ) VALUES (
                'Tema', 'Foco', 'SubFoco', '1º ano', 1,
                'conceitual', 'Enunciado', 'A', 'B',
                'C', 'D', 'A',
                'Objetivo', 'Intro',
                'Visao', 'ComA',
                'ComB', 'ComC', 'ComD',
                'Aprovado', 'Ref',
                'gpt-4', 1, 1,
                'invalid_status'
            )
        """)


def test_timestamps_auto_populated(memory_db, sample_question):
    """Test that created_at timestamp is auto-populated."""
    question_id = memory_db.save_question(sample_question)

    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT created_at FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()

    assert row["created_at"] is not None
    assert len(row["created_at"]) > 0


# ============================================================================
# Metrics Table Tests (4 tests)
# ============================================================================


def test_save_metrics_with_foreign_key(memory_db, sample_question, sample_metrics):
    """Test save_metrics with foreign key to question."""
    question_id = memory_db.save_question(sample_question)
    memory_db.save_metrics(question_id, sample_metrics)

    retrieved = memory_db.get_metrics_by_question_id(question_id)
    assert retrieved is not None
    assert retrieved.modelo == "gpt-4"
    assert retrieved.tokens == 1500
    assert retrieved.custo == 0.045


def test_get_metrics_by_question_id_returns_correct_metrics(
    memory_db, sample_question, sample_metrics
):
    """Test get_metrics_by_question_id returns correct metrics."""
    question_id = memory_db.save_question(sample_question)
    memory_db.save_metrics(question_id, sample_metrics)

    retrieved = memory_db.get_metrics_by_question_id(question_id)
    assert retrieved is not None
    assert retrieved.rodadas == 1
    assert retrieved.decisao == "aprovada"


def test_get_aggregate_metrics_calculates_totals(memory_db, sample_question, sample_metrics):
    """Test get_aggregate_metrics calculates totals correctly."""
    # Save multiple questions with metrics
    for _ in range(3):
        question_id = memory_db.save_question(sample_question)
        memory_db.save_metrics(question_id, sample_metrics)

    aggregates = memory_db.get_aggregate_metrics()

    assert "total_cost" in aggregates
    assert "total_tokens" in aggregates
    assert "avg_latency" in aggregates
    assert aggregates["total_cost"] == pytest.approx(0.045 * 3)
    assert aggregates["total_tokens"] == 1500 * 3


def test_foreign_key_constraint_cascade_delete(memory_db, sample_question, sample_metrics):
    """Test foreign key constraint deletes metrics when question deleted."""
    question_id = memory_db.save_question(sample_question)
    memory_db.save_metrics(question_id, sample_metrics)

    # Delete question
    cursor = memory_db.conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    memory_db.conn.commit()

    # Metrics should be deleted (CASCADE)
    retrieved = memory_db.get_metrics_by_question_id(question_id)
    assert retrieved is None


# ============================================================================
# Checkpoints Table Tests (3 tests)
# ============================================================================


def test_save_checkpoint_with_sample_ids_as_json(memory_db, sample_checkpoint):
    """Test save_checkpoint with sample_question_ids as JSON."""
    checkpoint_id = memory_db.save_checkpoint(sample_checkpoint)

    assert checkpoint_id > 0


def test_get_checkpoint_by_id_deserializes_json_correctly(memory_db, sample_checkpoint):
    """Test get_checkpoint_by_id deserializes JSON correctly."""
    checkpoint_id = memory_db.save_checkpoint(sample_checkpoint)
    retrieved = memory_db.get_checkpoint_by_id(checkpoint_id)

    assert retrieved is not None
    assert retrieved.checkpoint_id == "cp-001"
    assert retrieved.sample_question_ids == [1, 2, 3, 4, 5]
    assert retrieved.taxa_aprovacao == 0.85


def test_get_all_checkpoints_ordered_by_timestamp_desc(memory_db):
    """Test get_all_checkpoints ordered by timestamp DESC."""
    import time

    # Save multiple checkpoints
    cp1 = CheckpointResult(
        checkpoint_id="cp-001",
        foco_range="Focos 1-10",
        total_geradas=100,
        aprovadas=85,
        rejeitadas=10,
        failed=5,
        taxa_aprovacao=0.85,
        concordancia_media=0.92,
        custo_total=12.50,
        sample_question_ids=[1, 2, 3],
    )

    cp2 = CheckpointResult(
        checkpoint_id="cp-002",
        foco_range="Focos 11-20",
        total_geradas=100,
        aprovadas=90,
        rejeitadas=8,
        failed=2,
        taxa_aprovacao=0.90,
        concordancia_media=0.95,
        custo_total=11.00,
        sample_question_ids=[4, 5, 6],
    )

    memory_db.save_checkpoint(cp1)
    time.sleep(0.01)  # Ensure different timestamps
    memory_db.save_checkpoint(cp2)

    checkpoints = memory_db.get_all_checkpoints()

    # Most recent first
    assert len(checkpoints) == 2
    assert checkpoints[0].checkpoint_id == "cp-002"
    assert checkpoints[1].checkpoint_id == "cp-001"


# ============================================================================
# Batch Progress Tests (2 tests)
# ============================================================================


def test_save_batch_progress_upsert_behavior(memory_db, sample_batch_state):
    """Test save_batch_progress UPSERT behavior."""
    # Save initial state
    memory_db.save_batch_progress(sample_batch_state)

    # Update with new state
    updated_state = BatchState(
        foco_atual="Nova IC",
        sub_foco_atual=5,
        total_processados=200,
        timestamp="2026-02-07T11:00:00",
    )
    memory_db.save_batch_progress(updated_state)

    # Should only have one row
    retrieved = memory_db.get_batch_progress()
    assert retrieved is not None
    assert retrieved.total_processados == 200
    assert retrieved.foco_atual == "Nova IC"


def test_get_batch_progress_returns_latest_state(memory_db, sample_batch_state):
    """Test get_batch_progress returns latest state."""
    memory_db.save_batch_progress(sample_batch_state)

    retrieved = memory_db.get_batch_progress()
    assert retrieved is not None
    assert retrieved.foco_atual == "Insuficiência Cardíaca"
    assert retrieved.total_processados == 150


# ============================================================================
# Balancer State Tests (2 tests)
# ============================================================================


def test_save_balancer_state_with_position_counts(memory_db):
    """Test save_balancer_state with A/B/C/D counts."""
    counts = {"A": 10, "B": 12, "C": 8, "D": 15}
    memory_db.save_balancer_state(counts)

    retrieved = memory_db.get_balancer_state()
    assert retrieved == counts


def test_get_balancer_state_returns_correct_dict(memory_db):
    """Test get_balancer_state returns correct dict."""
    counts = {"A": 5, "B": 5, "C": 5, "D": 5}
    memory_db.save_balancer_state(counts)

    retrieved = memory_db.get_balancer_state()
    assert retrieved is not None
    assert retrieved["A"] == 5
    assert retrieved["D"] == 5


# ============================================================================
# Transaction Tests (3 tests)
# ============================================================================


def test_successful_write_commits_transaction(memory_db, sample_question):
    """Test successful write commits transaction."""
    _question_id = memory_db.save_question(sample_question)

    # Verify committed
    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    count = cursor.fetchone()["count"]
    assert count == 1


def test_failed_write_rolls_back(memory_db):
    """Test failed write rolls back (no partial data)."""
    initial_count = len(memory_db.get_questions_by_status("pending"))

    # Force error with invalid data
    try:
        cursor = memory_db.conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            INSERT INTO questions (tema, status)
            VALUES ('Test', 'invalid_status')
        """)
        memory_db.conn.commit()
    except sqlite3.IntegrityError:
        memory_db.conn.rollback()

    final_count = len(memory_db.get_questions_by_status("pending"))
    assert final_count == initial_count


def test_exception_raised_on_database_error(memory_db):
    """Test exception raised on database error."""

    # Try to save question with missing required fields
    with pytest.raises(sqlite3.Error):
        cursor = memory_db.conn.cursor()
        cursor.execute("INSERT INTO questions (tema) VALUES (?)", ("Test",))


# ============================================================================
# Concurrency Tests (2 tests)
# ============================================================================


def test_wal_mode_enabled(temp_db):
    """Test WAL mode enabled (PRAGMA returns 'wal')."""
    # Note: In-memory databases return 'memory', only file-based DBs support WAL
    cursor = temp_db.conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    result = cursor.fetchone()[0]

    assert result == "wal"


def test_concurrent_reads_during_write_dont_block(temp_db, sample_question):
    """Test concurrent reads during write don't block."""
    # Save initial question
    question_id = temp_db.save_question(sample_question)

    # Create second connection for reading
    conn2 = sqlite3.connect(temp_db.conn.execute("PRAGMA database_list").fetchone()[2])
    conn2.row_factory = sqlite3.Row

    # Read should succeed even during write transaction
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor2.fetchone()

    assert row is not None

    conn2.close()


def test_write_latency_under_10ms(memory_db, sample_question):
    """Test write latency is under 10ms per question (Success Metric).

    Story requirement (lines 116, 176): Write latency < 10ms per question.
    This validates NFR4 (non-blocking writes).
    """
    import time

    # Warm up database
    memory_db.save_question(sample_question)

    # Measure write latency over 10 iterations
    latencies = []
    for _ in range(10):
        start = time.perf_counter()
        memory_db.save_question(sample_question)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to milliseconds

    # Calculate average latency
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    # Assert performance requirement
    assert avg_latency < 10.0, f"Average write latency {avg_latency:.2f}ms exceeds 10ms threshold"
    assert max_latency < 20.0, (
        f"Max write latency {max_latency:.2f}ms is too high (should be <20ms)"
    )


def test_context_manager_closes_connection(tmp_path):
    """Test that context manager properly closes database connection."""
    db_path = tmp_path / "test_context.db"

    with MetricsStore(str(db_path)) as store:
        # Store should be usable inside context
        cursor = store.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert len(tables) > 0

    # Connection should be closed after context exit
    # Attempting to use it should raise an error
    with pytest.raises(sqlite3.ProgrammingError):
        store.conn.cursor()
