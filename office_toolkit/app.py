"""Streamlit user interface for the Office Efficiency Toolkit."""
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

from . import __version__
from .data_tools import MergeResult, dataframe_to_csv_bytes, dataframe_to_excel_bytes, merge_tabular_files
from .pdf_tools import merge_pdfs
from .rename_tools import RenameRules, apply_renames, build_preview, discover_files


def _render_data_merge_tab() -> None:
    st.subheader("Merge spreadsheets and CSV files")
    st.write(
        "Upload any combination of CSV or Excel files. Headers will be cleaned and the data"
        " combined into a single table. Use the options below to remove duplicate rows and"
        " download a clean export."
    )

    uploaded_files = st.file_uploader(
        "Select files",
        type=["csv", "tsv", "xls", "xlsx", "xlsm"],
        accept_multiple_files=True,
        help="Files are processed in the order they are selected.",
    )

    if not uploaded_files:
        st.info("Add at least one CSV or Excel file to get started.")
        return

    merge_result: MergeResult = merge_tabular_files(uploaded_files)
    if merge_result.errors:
        for message in merge_result.errors:
            st.warning(message)

    if merge_result.dataframe is None or merge_result.dataframe.empty:
        st.error("No data could be merged. Check the warnings above and try again.")
        return

    df = merge_result.dataframe
    st.success(f"Merged {len(df)} rows across {len(uploaded_files)} files.")

    st.markdown("### Cleaning options")
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    dedupe_columns: List[str] = []
    if remove_duplicates:
        dedupe_columns = st.multiselect(
            "Columns to consider duplicates",
            options=list(df.columns),
            help="Leave empty to look for duplicates across all columns.",
        )
        if dedupe_columns:
            df = df.drop_duplicates(subset=dedupe_columns)
        else:
            df = df.drop_duplicates()

    st.markdown("### Preview")
    st.dataframe(df.head(200), use_container_width=True)

    st.markdown("### Download")
    export_format = st.radio(
        "Choose an export format",
        options=("CSV", "Excel"),
        horizontal=True,
    )

    if export_format == "CSV":
        data_bytes = dataframe_to_csv_bytes(df)
        st.download_button(
            "Download CSV",
            data=data_bytes,
            file_name="merged-data.csv",
            mime="text/csv",
        )
    else:
        excel_buffer = dataframe_to_excel_bytes(df)
        st.download_button(
            "Download Excel workbook",
            data=excel_buffer,
            file_name="merged-data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _render_pdf_merge_tab() -> None:
    st.subheader("Merge PDFs")
    st.write("Combine multiple PDF documents into a single file without leaving your desktop.")

    pdf_files = st.file_uploader(
        "Select PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if not pdf_files:
        st.info("Upload at least two PDFs to enable merging.")
        return

    result = merge_pdfs(pdf_files)
    if result.errors:
        for message in result.errors:
            st.warning(message)

    if result.data is None:
        st.error("No PDF pages could be merged. Double-check the files and try again.")
        return

    st.success(f"Created a single PDF with {result.page_count} pages.")
    st.download_button(
        "Download merged PDF",
        data=result.data,
        file_name="merged.pdf",
        mime="application/pdf",
    )


def _render_batch_rename_tab() -> None:
    st.subheader("Batch rename files")
    st.write(
        "Apply simple renaming rules to every file inside a folder. Enter a local directory"
        " path (only files directly within the folder are affected)."
    )

    directory_text = st.text_input("Folder path", help="Example: C:/Reports or /Users/me/Documents/Exports")
    if not directory_text:
        st.info("Enter a folder path to continue.")
        return

    directory = Path(directory_text).expanduser()
    try:
        files = discover_files(directory)
    except (FileNotFoundError, NotADirectoryError) as exc:
        st.error(str(exc))
        return

    if not files:
        st.warning("The selected folder does not contain any files yet.")
        return

    st.caption(f"Previewing {len(files)} files in {directory}")

    prefix = st.text_input("Prefix", value="")
    suffix = st.text_input("Suffix", value="")
    find_text = st.text_input("Find text", value="")
    replace_text = st.text_input("Replace with", value="")
    include_sequence = st.checkbox("Add sequential numbers", value=False)
    sequence_position = st.selectbox(
        "Sequence placement",
        options=["prefix", "suffix"],
        index=1,
        help="Choose whether numbers appear before or after the file name.",
    )
    sequence_start = st.number_input("Starting number", min_value=0, value=1, step=1)
    sequence_padding = st.number_input("Number padding", min_value=0, value=2, step=1)

    rules = RenameRules(
        prefix=prefix,
        suffix=suffix,
        find_text=find_text,
        replace_text=replace_text,
        include_sequence=include_sequence,
        sequence_start=int(sequence_start),
        sequence_padding=int(sequence_padding),
        sequence_position=sequence_position,
    )

    try:
        previews = build_preview(files, rules)
    except ValueError as exc:
        st.error(str(exc))
        return

    preview_rows = {
        "Original name": [path.name for path in files],
        "New name": [preview.new_name for preview in previews],
    }
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)

    if st.button("Rename files", type="primary"):
        try:
            applied = apply_renames(previews)
        except PermissionError as exc:
            st.error(f"Permission denied: {exc}")
            return
        except OSError as exc:  # pragma: no cover - OS dependent errors
            st.error(f"An unexpected error occurred: {exc}")
            return

        renamed_count = len(applied)
        if renamed_count == 0:
            st.info("No files needed to be renamed.")
        else:
            st.success(f"Renamed {renamed_count} files successfully.")


def _render_about_tab() -> None:
    st.subheader("About")
    st.markdown(
        """
        **Office Efficiency Toolkit** provides frequently requested automation helpers for busy
        teams. It runs locally so your data never needs to leave your machine. For documentation,
        troubleshooting tips, and packaged downloads visit the project's README or GitHub releases.
        """
    )
    st.markdown(f"**Version:** {__version__}")


def main() -> None:
    """Entry point for the Streamlit UI."""
    st.set_page_config(page_title="Office Efficiency Toolkit", layout="wide")
    st.title("Office Efficiency Toolkit")
    st.caption("Merge data, combine PDFs, and rename files without scripts.")

    tabs = st.tabs([
        "Data merge",
        "PDF merge",
        "Batch rename",
        "About",
    ])

    with tabs[0]:
        _render_data_merge_tab()
    with tabs[1]:
        _render_pdf_merge_tab()
    with tabs[2]:
        _render_batch_rename_tab()
    with tabs[3]:
        _render_about_tab()


if __name__ == "__main__":  # pragma: no cover - Streamlit entry point
    main()
