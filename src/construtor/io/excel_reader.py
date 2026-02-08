"""Excel input file reader with comprehensive validation.

This module provides ExcelReader for reading and validating input Excel files
containing medical themes (temas), focus topics (focos), and academic periods.
"""

import logging
from pathlib import Path
from typing import ClassVar

import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException
from pydantic import ValidationError as PydanticValidationError

from construtor.config.exceptions import OutputParsingError, ValidationError
from construtor.models.question import FocoInput

logger = logging.getLogger(__name__)


class ExcelReader:
    """Excel input file reader with validation.

    This class reads Excel files (.xlsx format) containing medical themes,
    focus topics, and academic periods. It performs comprehensive validation
    including column existence, periodo value validation, and missing data
    detection.

    Example:
        >>> reader = ExcelReader()
        >>> focos = reader.read_input("data/input.xlsx")
        >>> print(f"Loaded {len(focos)} focos")
        Loaded 156 focos
    """

    # Class constants
    REQUIRED_COLUMNS: ClassVar[list[str]] = ["tema", "foco", "periodo"]
    VALID_PERIODOS: ClassVar[list[str]] = ["1º ano", "2º ano", "3º ano", "4º ano"]

    def read_input(self, file_path: str) -> list[FocoInput]:
        """Read and validate Excel input file.

        This method reads an Excel file, validates its structure and content,
        and returns a list of validated FocoInput objects.

        Args:
            file_path: Path to Excel file (.xlsx format)

        Returns:
            List of validated FocoInput objects

        Raises:
            FileNotFoundError: If file doesn't exist or is not a file
            ValidationError: If columns missing, periodo invalid, or data missing
            OutputParsingError: If Excel format is invalid or cannot be read

        Example:
            >>> reader = ExcelReader()
            >>> focos = reader.read_input("data/input.xlsx")
            >>> print(focos[0].tema)
            'Cardiologia'
        """
        logger.info(f"Loading Excel from {file_path}")

        # Validate file exists
        self._validate_file_exists(file_path)

        # Read Excel file
        try:
            df = pd.read_excel(
                file_path,
                engine="openpyxl",
                dtype=str,  # Read all as strings to prevent auto-conversion
                na_filter=True,  # Detect missing values
                keep_default_na=True,  # Use default NaN markers
            )
        except FileNotFoundError:
            logger.exception(f"File not found: {file_path}")
            raise
        except InvalidFileException as e:
            logger.exception(f"Invalid Excel format: {file_path}")
            raise OutputParsingError(f"Invalid Excel format: {file_path}") from e
        except Exception as e:
            logger.exception(f"Failed to read Excel {file_path}")
            raise OutputParsingError(f"Failed to read Excel: {e}") from e

        # Validate and clean data
        self._validate_columns(df, file_path)
        df = self._normalize_data(df)
        # Performance: keep only required columns after normalization
        df = df[self.REQUIRED_COLUMNS]
        self._validate_periodo_values(df, file_path)
        self._validate_no_missing_data(df, file_path)

        # Convert to Pydantic models
        focos = self._dataframe_to_focos(df, file_path)

        logger.info(f"Successfully loaded {len(focos)} focos from {file_path}")
        return focos

    def _validate_file_exists(self, file_path: str) -> None:
        """Validate file exists and is readable.

        Args:
            file_path: Path to validate

        Raises:
            FileNotFoundError: If file doesn't exist or is not a file
            ValidationError: If file extension is not .xlsx or .xlsm
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        if not path.is_file():
            raise FileNotFoundError(f"Path is not a file: {file_path}")

        # Validate file extension
        if path.suffix.lower() not in [".xlsx", ".xlsm"]:
            raise ValidationError(
                f"Invalid file format: {path.suffix}. "
                f"Expected Excel file with .xlsx or .xlsm extension."
            )

    def _validate_columns(self, df: pd.DataFrame, file_path: str) -> None:
        """Validate required columns exist.

        Performs case-insensitive column matching and handles extra whitespace.

        Args:
            df: DataFrame to validate
            file_path: Path to Excel file (for error messages)

        Raises:
            ValidationError: If required columns are missing
        """
        # Normalize column names: lowercase and strip whitespace
        actual_columns = {col.strip().lower() for col in df.columns}
        required_columns = {col.lower() for col in self.REQUIRED_COLUMNS}

        missing_columns = required_columns - actual_columns

        if missing_columns:
            logger.error(
                f"Missing columns {missing_columns} in {file_path}. "
                f"Expected: {self.REQUIRED_COLUMNS}. Found: {list(df.columns)}"
            )
            raise ValidationError(
                f"Missing required columns: {sorted(missing_columns)}. "
                f"Expected: {self.REQUIRED_COLUMNS}. Found: {list(df.columns)}"
            )

    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame column names and data.

        Normalizes column names to lowercase and strips whitespace from all
        string values. Also treats whitespace-only values as missing.

        Args:
            df: DataFrame to normalize

        Returns:
            Normalized DataFrame with clean column names and data
        """
        # Normalize column names: lowercase and strip
        df.columns = df.columns.str.strip().str.lower()

        # Strip whitespace from all string columns
        for col in self.REQUIRED_COLUMNS:
            if col in df.columns:
                df[col] = df[col].str.strip()

        # Replace whitespace-only values with NaN
        df.replace(r"^\s*$", pd.NA, regex=True, inplace=True)

        return df

    def _validate_periodo_values(self, df: pd.DataFrame, file_path: str) -> None:
        """Validate all periodo values are valid academic periods.

        Args:
            df: DataFrame to validate
            file_path: Path to Excel file (for error messages)

        Raises:
            ValidationError: If invalid periodo values are found
        """
        # Check all values against valid periodos
        invalid_mask = ~df["periodo"].isin(self.VALID_PERIODOS)
        invalid_rows = df[invalid_mask]

        if not invalid_rows.empty:
            # Collect row numbers (1-indexed for Excel, +2 for header)
            errors = [(idx + 2, row["periodo"]) for idx, row in invalid_rows.iterrows()]

            error_msg = (
                f"Invalid periodo values found in {file_path}:\n"
                + "\n".join(f"  Row {row_num}: '{value}'" for row_num, value in errors)
                + f"\nValid values: {self.VALID_PERIODOS}"
            )

            logger.error(error_msg)
            raise ValidationError(error_msg)

    def _validate_no_missing_data(self, df: pd.DataFrame, file_path: str) -> None:
        """Validate no missing data in required columns.

        Args:
            df: DataFrame to validate
            file_path: Path to Excel file (for error messages)

        Raises:
            ValidationError: If missing data is found
        """
        for col in self.REQUIRED_COLUMNS:
            missing_mask = df[col].isna()
            if missing_mask.any():
                # Get row numbers (1-indexed, +2 for header)
                row_numbers = [idx + 2 for idx in df[missing_mask].index]

                error_msg = f"Missing data in column '{col}' at rows {row_numbers} in {file_path}"

                logger.error(error_msg)
                raise ValidationError(error_msg)

    def _dataframe_to_focos(self, df: pd.DataFrame, file_path: str) -> list[FocoInput]:
        """Convert validated DataFrame to list of FocoInput models.

        Args:
            df: Validated DataFrame with clean data
            file_path: Path to Excel file (for error messages)

        Returns:
            List of FocoInput objects

        Raises:
            ValidationError: If Pydantic validation fails for any row
        """
        focos: list[FocoInput] = []

        for idx, row in df.iterrows():
            try:
                foco = FocoInput(
                    tema=row["tema"],
                    foco=row["foco"],
                    periodo=row["periodo"],
                )
                focos.append(foco)
            except PydanticValidationError as e:
                row_num = idx + 2  # Excel row number (header + 0-index)
                error_msg = f"Validation failed at row {row_num} in {file_path}: {e}"
                logger.exception(error_msg)
                raise ValidationError(error_msg) from e

        return focos
