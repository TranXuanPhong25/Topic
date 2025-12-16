
from __future__ import annotations

import argparse
from typing import Iterable, Tuple

from .Load import DEFAULT_DATA_DIR
from .metadata import extract_pdf_metadata


def iter_metadata_paths(data_dir: str | None) -> Iterable[Tuple[str, dict]]:
    """
    Yield (path, metadata) for all PDFs inside the target directory.
    """
    from pathlib import Path

    base = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    if not base.exists():
        raise FileNotFoundError(f"Data directory not found: {base}")

    for pdf in sorted(base.glob("*.pdf")):
        yield str(pdf), extract_pdf_metadata(pdf)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect metadata of PDF documents inside the RAG data folder.")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Path to the directory containing documents (defaults to rag/Data).",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("PDF Metadata Inspection")
    print(f"Directory: {args.data_dir or DEFAULT_DATA_DIR}")
    print("=" * 80)

    try:
        for path, metadata in iter_metadata_paths(args.data_dir):
            print(f"\n===== {path} =====")
            if not metadata:
                print("(No metadata found)")
                continue

            for key, value in metadata.items():
                print(f"{key}: {value}")
    except Exception as exc:
        print(f"ERROR: Không thể đọc metadata: {exc}")


if __name__ == "__main__":
    main()

