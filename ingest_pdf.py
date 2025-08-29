from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from sql_utils import process_and_store


def _gather_pdfs(paths: Iterable[str]) -> List[Path]:
    results: List[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            results.extend(sorted([f for f in path.glob("**/*.pdf") if f.is_file()]))
        elif path.is_file() and path.suffix.lower() == ".pdf":
            results.append(path)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Process PDFs and store data into SQLite")
    parser.add_argument("inputs", nargs="+", help="PDF file(s) or directory(ies) containing PDFs")
    parser.add_argument(
        "--db",
        default="db.sqlite",
        help="Path to SQLite database file (default: db.sqlite)",
    )
    args = parser.parse_args()

    pdfs = _gather_pdfs(args.inputs)
    if not pdfs:
        print("No PDF files found to process.")
        return

    for pdf_path in pdfs:
        pdf_id, ops_count = process_and_store(pdf_path, args.db)
        print(f"Stored: id={pdf_id} ops={ops_count} file={pdf_path}")


if __name__ == "__main__":
    main()


