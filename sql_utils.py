from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import event, delete

from pdf_processor import PDFSummary, Operation, process_pdf, extract_card_operations


class PDF(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_path: str = Field(index=True, unique=True)
    client_name: Optional[str] = None
    account_number: Optional[str] = None
    total_iesiri: Optional[float] = None
    sold_initial: Optional[float] = None
    sold_final: Optional[float] = None
    created_at: Optional[str] = Field(default=None)  # could be set by app if needed


class OperationRow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pdf_id: int = Field(foreign_key="pdf.id")
    transaction_date: Optional[str] = None
    processed_date: Optional[str] = None
    description: Optional[str] = None
    amount_lei: Optional[float] = None


def get_engine(db_path: str | Path):
    url = f"sqlite:///{Path(db_path)}"
    engine = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-redef]
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    return engine


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)


def store_pdf_summary(
    session: Session,
    file_path: str | Path,
    summary: PDFSummary,
) -> int:
    file_path_str = str(file_path)
    existing = session.exec(select(PDF).where(PDF.file_path == file_path_str)).first()
    if existing is None:
        pdf = PDF(
            file_path=file_path_str,
            client_name=summary.client_name,
            account_number=summary.account_number,
            total_iesiri=summary.total_iesiri,
            sold_initial=summary.sold_initial,
            sold_final=summary.sold_final,
        )
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        return int(pdf.id)  # type: ignore[arg-type]
    else:
        existing.client_name = summary.client_name
        existing.account_number = summary.account_number
        existing.total_iesiri = summary.total_iesiri
        existing.sold_initial = summary.sold_initial
        existing.sold_final = summary.sold_final
        session.add(existing)
        session.commit()
        return int(existing.id)  # type: ignore[arg-type]


def store_operations(
    session: Session,
    pdf_id: int,
    operations: Iterable[Operation],
    *,
    replace_existing: bool = True,
) -> int:
    if replace_existing:
        session.exec(delete(OperationRow).where(OperationRow.pdf_id == pdf_id))

    count = 0
    for op in operations:
        row = OperationRow(
            pdf_id=pdf_id,
            transaction_date=op.transaction_date,
            processed_date=op.processed_date,
            description=op.description,
            amount_lei=op.amount_lei,
        )
        session.add(row)
        count += 1
    session.commit()
    return count


def get_pdf_by_path(session: Session, file_path: str | Path) -> Optional[PDF]:
    return session.exec(select(PDF).where(PDF.file_path == str(file_path))).first()


def get_operations_for_pdf(session: Session, pdf_id: int) -> List[OperationRow]:
    return list(session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf_id).order_by(OperationRow.id)))


def process_and_store(
    pdf_path: str | Path,
    db_path: str | Path,
) -> Tuple[int, int]:
    pdf_path = Path(pdf_path)
    engine = get_engine(db_path)
    init_db(engine)
    with Session(engine) as session:
        summary = process_pdf(str(pdf_path))
        pdf_id = store_pdf_summary(session, str(pdf_path), summary)
        ops = extract_card_operations(str(pdf_path))
        n = store_operations(session, pdf_id, ops)
        return pdf_id, n


