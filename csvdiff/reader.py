"""CSV reader module for loading and indexing CSV files by key columns."""

import csv
from pathlib import Path
from typing import Dict, List, Tuple, Union


class CSVReader:
    """Reads a CSV file and indexes rows by one or more key columns."""

    def __init__(self, key_columns: List[str]):
        """
        Initialize the reader with the specified key columns.

        Args:
            key_columns: List of column names to use as the composite key.
        """
        if not key_columns:
            raise ValueError("At least one key column must be specified.")
        self.key_columns = key_columns

    def load(self, filepath: Union[str, Path]) -> Tuple[List[str], Dict[tuple, Dict[str, str]]]:
        """
        Load a CSV file and return its headers and a row index.

        Args:
            filepath: Path to the CSV file.

        Returns:
            A tuple of (headers, index) where index maps key tuples to row dicts.

        Raises:
            FileNotFoundError: If the file does not exist.
            KeyError: If any key column is missing from the CSV headers.
            ValueError: If duplicate keys are detected in the CSV file.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        index: Dict[tuple, Dict[str, str]] = {}
        headers: List[str] = []

        with filepath.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                return [], {}
            headers = list(reader.fieldnames)

            missing = [col for col in self.key_columns if col not in headers]
            if missing:
                raise KeyError(
                    f"Key column(s) not found in '{filepath.name}': {missing}"
                )

            for row in reader:
                key = tuple(row[col] for col in self.key_columns)
                if key in index:
                    raise ValueError(
                        f"Duplicate key {key} found in '{filepath.name}'. "
                        "Key columns must uniquely identify each row."
                    )
                index[key] = dict(row)

        return headers, index
