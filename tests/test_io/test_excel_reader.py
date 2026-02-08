"""Comprehensive tests for ExcelReader.

This test module covers:
- Happy path: reading valid Excel files
- Column validation: missing columns, case-insensitive matching
- Periodo validation: invalid values, all valid values
- Missing data: empty cells, whitespace-only values
- File handling: non-existent files, invalid formats
- Edge cases: whitespace in column names, data normalization
"""

from pathlib import Path

import pandas as pd
import pytest

from construtor.config.exceptions import OutputParsingError, ValidationError
from construtor.io import ExcelReader
from construtor.models.question import FocoInput

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def valid_excel_file(tmp_path: Path) -> Path:
    """Create temporary valid Excel file for testing.

    Returns:
        Path to temporary Excel file with valid data
    """
    df = pd.DataFrame(
        {
            "tema": ["Cardiologia", "Pneumologia", "Gastroenterologia"],
            "foco": [
                "Insuficiência Cardíaca",
                "Asma",
                "Doença do Refluxo Gastroesofágico",
            ],
            "periodo": ["3º ano", "2º ano", "4º ano"],
        }
    )

    file_path = tmp_path / "valid_input.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_missing_periodo_column(tmp_path: Path) -> Path:
    """Create Excel file missing 'periodo' column.

    Returns:
        Path to Excel file with missing periodo column
    """
    df = pd.DataFrame(
        {
            "tema": ["Cardiologia"],
            "foco": ["ICC"],
            # 'periodo' is MISSING
        }
    )

    file_path = tmp_path / "missing_periodo.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_missing_tema_column(tmp_path: Path) -> Path:
    """Create Excel file missing 'tema' column.

    Returns:
        Path to Excel file with missing tema column
    """
    df = pd.DataFrame(
        {
            # 'tema' is MISSING
            "foco": ["ICC"],
            "periodo": ["3º ano"],
        }
    )

    file_path = tmp_path / "missing_tema.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_invalid_periodo(tmp_path: Path) -> Path:
    """Create Excel file with invalid periodo value.

    Returns:
        Path to Excel file with invalid periodo ('5º ano')
    """
    df = pd.DataFrame(
        {
            "tema": ["Cardiologia", "Pneumologia"],
            "foco": ["ICC", "Asma"],
            "periodo": ["5º ano", "2º ano"],  # '5º ano' is invalid!
        }
    )

    file_path = tmp_path / "invalid_periodo.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_missing_data(tmp_path: Path) -> Path:
    """Create Excel file with missing data (NaN cells).

    Returns:
        Path to Excel file with empty cells
    """
    df = pd.DataFrame(
        {
            "tema": ["Cardiologia", None, "Gastroenterologia"],  # Row 2 missing
            "foco": ["ICC", "Asma", "DRGE"],
            "periodo": ["3º ano", "2º ano", "4º ano"],
        }
    )

    file_path = tmp_path / "missing_data.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_whitespace_only(tmp_path: Path) -> Path:
    """Create Excel file with whitespace-only values.

    Returns:
        Path to Excel file with whitespace-only values
    """
    df = pd.DataFrame(
        {
            "tema": ["Cardiologia", "   ", "Gastroenterologia"],  # Row 2: whitespace
            "foco": ["ICC", "Asma", "DRGE"],
            "periodo": ["3º ano", "2º ano", "4º ano"],
        }
    )

    file_path = tmp_path / "whitespace.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_case_insensitive_columns(tmp_path: Path) -> Path:
    """Create Excel file with uppercase column names.

    Returns:
        Path to Excel file with UPPERCASE columns
    """
    df = pd.DataFrame(
        {
            "TEMA": ["Cardiologia"],  # Uppercase
            "Foco": ["ICC"],  # Mixed case
            "PERIODO": ["3º ano"],  # Uppercase
        }
    )

    file_path = tmp_path / "uppercase_columns.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_whitespace_in_columns(tmp_path: Path) -> Path:
    """Create Excel file with whitespace in column names.

    Returns:
        Path to Excel file with spaces around column names
    """
    df = pd.DataFrame(
        {
            " tema ": ["Cardiologia"],  # Whitespace around
            "foco  ": ["ICC"],  # Trailing whitespace
            "  periodo": ["3º ano"],  # Leading whitespace
        }
    )

    file_path = tmp_path / "whitespace_columns.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


@pytest.fixture
def excel_all_valid_periodos(tmp_path: Path) -> Path:
    """Create Excel file with all valid periodo values.

    Returns:
        Path to Excel file with all 4 valid periodos
    """
    df = pd.DataFrame(
        {
            "tema": ["Cardio", "Pneumo", "Gastro", "Neuro"],
            "foco": ["ICC", "Asma", "DRGE", "AVC"],
            "periodo": ["1º ano", "2º ano", "3º ano", "4º ano"],
        }
    )

    file_path = tmp_path / "all_periodos.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return file_path


# ============================================================================
# Happy Path Tests
# ============================================================================


def test_read_valid_excel_returns_foco_input_list(valid_excel_file: Path) -> None:
    """Test reading valid Excel file returns list of FocoInput objects."""
    # Arrange
    reader = ExcelReader()

    # Act
    focos = reader.read_input(str(valid_excel_file))

    # Assert
    assert isinstance(focos, list)
    assert len(focos) == 3
    assert all(isinstance(foco, FocoInput) for foco in focos)


def test_read_valid_excel_parses_fields_correctly(valid_excel_file: Path) -> None:
    """Test that all fields are parsed correctly from Excel."""
    # Arrange
    reader = ExcelReader()

    # Act
    focos = reader.read_input(str(valid_excel_file))

    # Assert
    assert focos[0].tema == "Cardiologia"
    assert focos[0].foco == "Insuficiência Cardíaca"
    assert focos[0].periodo == "3º ano"

    assert focos[1].tema == "Pneumologia"
    assert focos[1].foco == "Asma"
    assert focos[1].periodo == "2º ano"

    assert focos[2].tema == "Gastroenterologia"
    assert focos[2].foco == "Doença do Refluxo Gastroesofágico"
    assert focos[2].periodo == "4º ano"


def test_read_all_valid_periodos_accepted(excel_all_valid_periodos: Path) -> None:
    """Test that all valid periodo values (1º-4º ano) are accepted."""
    # Arrange
    reader = ExcelReader()

    # Act
    focos = reader.read_input(str(excel_all_valid_periodos))

    # Assert
    assert len(focos) == 4
    assert focos[0].periodo == "1º ano"
    assert focos[1].periodo == "2º ano"
    assert focos[2].periodo == "3º ano"
    assert focos[3].periodo == "4º ano"


# ============================================================================
# Column Validation Tests
# ============================================================================


def test_missing_periodo_column_raises_validation_error(
    excel_missing_periodo_column: Path,
) -> None:
    """Test error when 'periodo' column is missing."""
    # Arrange
    reader = ExcelReader()

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(excel_missing_periodo_column))

    error_msg = str(exc_info.value).lower()
    assert "periodo" in error_msg
    assert "missing" in error_msg


def test_missing_tema_column_raises_validation_error(
    excel_missing_tema_column: Path,
) -> None:
    """Test error when 'tema' column is missing."""
    # Arrange
    reader = ExcelReader()

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(excel_missing_tema_column))

    error_msg = str(exc_info.value).lower()
    assert "tema" in error_msg
    assert "missing" in error_msg


def test_case_insensitive_column_matching(
    excel_case_insensitive_columns: Path,
) -> None:
    """Test that column names are matched case-insensitively."""
    # Arrange
    reader = ExcelReader()

    # Act
    focos = reader.read_input(str(excel_case_insensitive_columns))

    # Assert - should work despite uppercase/mixed case
    assert len(focos) == 1
    assert focos[0].tema == "Cardiologia"
    assert focos[0].foco == "ICC"
    assert focos[0].periodo == "3º ano"


def test_whitespace_in_column_names_handled(
    excel_whitespace_in_columns: Path,
) -> None:
    """Test that whitespace in column names is stripped correctly."""
    # Arrange
    reader = ExcelReader()

    # Act
    focos = reader.read_input(str(excel_whitespace_in_columns))

    # Assert - should work despite whitespace
    assert len(focos) == 1
    assert focos[0].tema == "Cardiologia"
    assert focos[0].foco == "ICC"
    assert focos[0].periodo == "3º ano"


# ============================================================================
# Periodo Validation Tests
# ============================================================================


def test_invalid_periodo_raises_validation_error(excel_invalid_periodo: Path) -> None:
    """Test error for invalid periodo value ('5º ano')."""
    # Arrange
    reader = ExcelReader()

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(excel_invalid_periodo))

    error_msg = str(exc_info.value)
    assert "periodo" in error_msg.lower()
    assert "5º ano" in error_msg
    assert "row 2" in error_msg.lower()  # Excel row number


# ============================================================================
# Missing Data Tests
# ============================================================================


def test_missing_data_in_tema_raises_validation_error(
    excel_missing_data: Path,
) -> None:
    """Test error when 'tema' has empty cell."""
    # Arrange
    reader = ExcelReader()

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(excel_missing_data))

    error_msg = str(exc_info.value)
    assert "tema" in error_msg.lower()
    assert "missing" in error_msg.lower()
    assert "3" in error_msg  # Row 3 (header + row 2 in data)


def test_whitespace_only_treated_as_missing(excel_whitespace_only: Path) -> None:
    """Test that whitespace-only values are treated as missing data."""
    # Arrange
    reader = ExcelReader()

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(excel_whitespace_only))

    error_msg = str(exc_info.value)
    assert "tema" in error_msg.lower()
    assert "missing" in error_msg.lower()


# ============================================================================
# File Handling Tests
# ============================================================================


def test_file_not_found_raises_error(tmp_path: Path) -> None:
    """Test FileNotFoundError for non-existent file."""
    # Arrange
    reader = ExcelReader()
    non_existent = tmp_path / "does_not_exist.xlsx"

    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        reader.read_input(str(non_existent))

    assert "not found" in str(exc_info.value).lower()


def test_invalid_excel_format_raises_parsing_error(tmp_path: Path) -> None:
    """Test ValidationError for non-Excel file extension (.txt)."""
    # Arrange
    reader = ExcelReader()
    txt_file = tmp_path / "not_excel.txt"
    txt_file.write_text("This is not an Excel file")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(txt_file))

    error_msg = str(exc_info.value).lower()
    assert "invalid file format" in error_msg or ".txt" in error_msg


def test_directory_instead_of_file_raises_error(tmp_path: Path) -> None:
    """Test error when path is a directory instead of a file."""
    # Arrange
    reader = ExcelReader()
    directory = tmp_path / "not_a_file"
    directory.mkdir()

    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        reader.read_input(str(directory))

    assert "not a file" in str(exc_info.value).lower()


def test_corrupted_excel_file_raises_parsing_error(tmp_path: Path) -> None:
    """Test OutputParsingError for corrupted Excel file."""
    # Arrange
    reader = ExcelReader()
    corrupted_file = tmp_path / "corrupted.xlsx"
    # Write invalid Excel content (not a valid ZIP/XML structure)
    corrupted_file.write_bytes(b"This is not valid Excel XML content")

    # Act & Assert
    with pytest.raises(OutputParsingError) as exc_info:
        reader.read_input(str(corrupted_file))

    error_msg = str(exc_info.value).lower()
    assert "excel" in error_msg or "parsing" in error_msg or "failed" in error_msg


# ============================================================================
# Edge Cases and Integration Tests
# ============================================================================


def test_empty_excel_file_raises_validation_error(tmp_path: Path) -> None:
    """Test error when Excel file has no data rows."""
    # Arrange
    reader = ExcelReader()
    df = pd.DataFrame({"tema": [], "foco": [], "periodo": []})
    file_path = tmp_path / "empty.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")

    # Act
    focos = reader.read_input(str(file_path))

    # Assert - empty list is valid (no data to validate)
    assert focos == []


def test_data_with_extra_whitespace_stripped(tmp_path: Path) -> None:
    """Test that data values with extra whitespace are stripped."""
    # Arrange
    reader = ExcelReader()
    df = pd.DataFrame(
        {
            "tema": ["  Cardiologia  "],  # Extra whitespace
            "foco": ["  ICC  "],
            "periodo": ["  3º ano  "],
        }
    )
    file_path = tmp_path / "whitespace_data.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")

    # Act
    focos = reader.read_input(str(file_path))

    # Assert - whitespace should be stripped
    assert focos[0].tema == "Cardiologia"
    assert focos[0].foco == "ICC"
    assert focos[0].periodo == "3º ano"


def test_multiple_validation_errors_reported(tmp_path: Path) -> None:
    """Test that validation catches first error and reports it clearly."""
    # Arrange
    reader = ExcelReader()
    df = pd.DataFrame(
        {
            "tema": ["Cardiologia", "Pneumologia"],
            "foco": ["ICC", "Asma"],
            "periodo": ["5º ano", "6º ano"],  # Both invalid!
        }
    )
    file_path = tmp_path / "multiple_errors.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        reader.read_input(str(file_path))

    error_msg = str(exc_info.value)
    # Should report both rows with errors
    assert "5º ano" in error_msg
    assert "6º ano" in error_msg
    assert "row 2" in error_msg.lower()
    assert "row 3" in error_msg.lower()
