"""Utilities for working with tabular data files."""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import pandas as pd

SUPPORTED_TABLE_TYPES = {".csv", ".tsv", ".xls", ".xlsx", ".xlsm"}


@dataclass
class MergeResult:
    """Result of merging user supplied tabular files."""

    dataframe: pd.DataFrame | None
    errors: List[str]


def clean_header(name: str) -> str:
    """Create a friendly header from user provided column names."""
    if name is None:
        name = ""
    cleaned = str(name).strip()
    cleaned = cleaned.replace("\n", " ")
    cleaned = " ".join(cleaned.split())
    cleaned = cleaned.lower()
    allowed = []
    for char in cleaned:
        if char.isalnum():
            allowed.append(char)
        else:
            allowed.append("_")
    cleaned = "".join(allowed)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_")
    return cleaned or "column"


def make_unique(columns: Sequence[str]) -> List[str]:
    """Ensure column names are unique after cleaning."""
    seen = {}
    result: List[str] = []
    for name in columns:
        base = name
        if base not in seen:
            seen[base] = 0
            result.append(base)
            continue
        seen[base] += 1
        result.append(f"{base}_{seen[base]}")
    return result


def _read_csv(uploaded, delimiter: str = ",") -> pd.DataFrame:
    return pd.read_csv(uploaded, dtype=str, keep_default_na=False, na_values=[], delimiter=delimiter)


def _read_excel(uploaded) -> pd.DataFrame:
    return pd.read_excel(uploaded, dtype=str)


def read_table(uploaded) -> Tuple[pd.DataFrame | None, str | None]:
    """Read an uploaded table file into a DataFrame."""
    suffix = Path(uploaded.name).suffix.lower()
    try:
        uploaded.seek(0)
    except Exception:
        pass

    try:
        if suffix == ".csv":
            df = _read_csv(uploaded)
        elif suffix == ".tsv":
            df = _read_csv(uploaded, delimiter="\t")
        elif suffix in {".xls", ".xlsx", ".xlsm"}:
            df = _read_excel(uploaded)
        else:
            return None, f"Unsupported file type: {uploaded.name}"
    except Exception as exc:  # pragma: no cover - streamlit environment
        return None, f"Failed to read {uploaded.name}: {exc}"

    cleaned_cols = [clean_header(col) for col in df.columns]
    cleaned_cols = make_unique(cleaned_cols)
    df.columns = cleaned_cols
    return df, None


def merge_tabular_files(files: Iterable) -> MergeResult:
    """Merge multiple uploaded CSV/Excel files."""
    frames: List[pd.DataFrame] = []
    errors: List[str] = []

    for uploaded in files:
        df, error = read_table(uploaded)
        if error:
            errors.append(error)
            continue
        if df is not None:
            frames.append(df)

    if not frames:
        return MergeResult(dataframe=None, errors=errors)

    combined = pd.concat(frames, ignore_index=True, sort=False)
    return MergeResult(dataframe=combined, errors=errors)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Export a DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8-sig")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> BytesIO:
    """Export a DataFrame to an in-memory Excel workbook."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Merged Data")
    output.seek(0)
    return output
