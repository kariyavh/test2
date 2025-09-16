"""Utilities for previewing and applying batch file rename rules."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


@dataclass
class RenameRules:
    """Rules that describe how files should be renamed."""

    prefix: str = ""
    suffix: str = ""
    find_text: str = ""
    replace_text: str = ""
    include_sequence: bool = False
    sequence_start: int = 1
    sequence_padding: int = 2
    sequence_position: str = "suffix"  # "prefix" or "suffix"


@dataclass
class RenamePreview:
    """A preview of how a single file will be renamed."""

    original: Path
    new_name: str


def discover_files(directory: Path) -> List[Path]:
    """Return a sorted list of files directly within ``directory``."""
    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    return sorted([path for path in directory.iterdir() if path.is_file()])


def build_preview(files: Sequence[Path], rules: RenameRules) -> List[RenamePreview]:
    """Create preview entries for the supplied files and rules."""
    previews: List[RenamePreview] = []
    used_names: set[str] = set()

    for index, file_path in enumerate(files):
        stem = file_path.stem
        suffix = "".join(file_path.suffixes)

        transformed = stem
        if rules.find_text:
            transformed = transformed.replace(rules.find_text, rules.replace_text)

        if rules.include_sequence:
            number = rules.sequence_start + index
            sequence_value = str(number).zfill(max(0, rules.sequence_padding))
            if rules.sequence_position == "prefix":
                transformed = f"{sequence_value}{transformed}"
            else:
                transformed = f"{transformed}{sequence_value}"

        transformed = f"{rules.prefix}{transformed}{rules.suffix}"
        new_name = f"{transformed}{suffix}"

        if new_name in used_names:
            raise ValueError(
                "Renaming rules produce duplicate file names. Adjust your settings and try again."
            )
        used_names.add(new_name)

        previews.append(RenamePreview(original=file_path, new_name=new_name))

    return previews


def apply_renames(previews: Iterable[RenamePreview]) -> List[Tuple[Path, Path]]:
    """Perform the rename operations for the provided preview entries."""
    performed: List[Tuple[Path, Path]] = []
    for preview in previews:
        source = preview.original
        target = source.with_name(preview.new_name)
        if source == target:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)
        performed.append((source, target))
    return performed
