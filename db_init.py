from pathlib import Path
import argparse

from sqlmodel import Session

from sql_utils import get_engine, init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the SQLite database schema")
    parser.add_argument(
        "db",
        nargs="?",
        default="db.sqlite",
        help="Path to the SQLite database file (default: db.sqlite)",
    )
    args = parser.parse_args()

    engine = get_engine(args.db)
    init_db(engine)
    # Touch the file to ensure it exists on disk
    Path(args.db).touch(exist_ok=True)
    print(f"Initialized database at {args.db}")


if __name__ == "__main__":
    main()


