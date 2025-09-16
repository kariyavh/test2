"""Executable entry point that launches the Streamlit app."""
from __future__ import annotations

import os
from pathlib import Path

from streamlit.web import bootstrap


def main() -> None:
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")

    this_dir = Path(__file__).resolve().parent
    app_path = this_dir / "office_toolkit" / "app.py"
    bootstrap.run(str(app_path), "", [], {})


if __name__ == "__main__":  # pragma: no cover - entry point only used when running directly
    main()
