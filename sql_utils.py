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


class OperationType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: Optional[str] = Field(default=None)


class OperationRow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pdf_id: int = Field(foreign_key="pdf.id")
    type_id: Optional[int] = Field(default=None, foreign_key="operationtype.id")
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


def create_operation_type(session: Session, name: str, description: Optional[str] = None) -> OperationType:
    """Create a new operation type"""
    operation_type = OperationType(name=name, description=description)
    session.add(operation_type)
    session.commit()
    session.refresh(operation_type)
    return operation_type


def get_operation_types(session: Session) -> List[OperationType]:
    """Get all operation types"""
    return list(session.exec(select(OperationType).order_by(OperationType.name)))


def get_operation_type_by_id(session: Session, type_id: int) -> Optional[OperationType]:
    """Get operation type by ID"""
    return session.exec(select(OperationType).where(OperationType.id == type_id)).first()


def get_operation_type_by_name(session: Session, name: str) -> Optional[OperationType]:
    """Get operation type by name"""
    return session.exec(select(OperationType).where(OperationType.name == name)).first()


def update_operation_type(session: Session, type_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[OperationType]:
    """Update an operation type"""
    operation_type = get_operation_type_by_id(session, type_id)
    if operation_type:
        if name is not None:
            operation_type.name = name
        if description is not None:
            operation_type.description = description
        session.add(operation_type)
        session.commit()
        session.refresh(operation_type)
    return operation_type


def delete_operation_type(session: Session, type_id: int) -> bool:
    """Delete an operation type (only if no operations are using it)"""
    operation_type = get_operation_type_by_id(session, type_id)
    if operation_type:
        # Check if any operations are using this type
        operations_using_type = session.exec(select(OperationRow).where(OperationRow.type_id == type_id)).first()
        if operations_using_type:
            return False  # Cannot delete if operations are using this type
        
        session.delete(operation_type)
        session.commit()
        return True
    return False


def assign_operation_type(session: Session, operation_id: int, type_id: Optional[int]) -> Optional[OperationRow]:
    """Assign a type to an operation"""
    operation = session.exec(select(OperationRow).where(OperationRow.id == operation_id)).first()
    if operation:
        operation.type_id = type_id
        session.add(operation)
        session.commit()
        session.refresh(operation)
    return operation


def get_operations_by_type(session: Session, type_id: int) -> List[OperationRow]:
    """Get all operations of a specific type"""
    return list(session.exec(select(OperationRow).where(OperationRow.type_id == type_id).order_by(OperationRow.transaction_date)))


def get_operations_with_types(session: Session, pdf_id: Optional[int] = None) -> List[Tuple[OperationRow, Optional[OperationType]]]:
    """Get operations with their associated types"""
    query = select(OperationRow, OperationType).outerjoin(OperationType, OperationRow.type_id == OperationType.id)
    if pdf_id:
        query = query.where(OperationRow.pdf_id == pdf_id)
    query = query.order_by(OperationRow.transaction_date)
    return list(session.exec(query))


def get_operations_with_null_types(session: Session, pdf_id: Optional[int] = None) -> List[OperationRow]:
    """Get operations that have null type_id"""
    query = select(OperationRow).where(OperationRow.type_id.is_(None))
    if pdf_id:
        query = query.where(OperationRow.pdf_id == pdf_id)
    query = query.order_by(OperationRow.transaction_date)
    return list(session.exec(query))


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


