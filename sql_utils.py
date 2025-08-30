from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import event, delete

from pdf_processor import PDFSummary, Operation, process_pdf, extract_card_operations, extract_and_classify_operations, get_high_confidence_suggestions, get_medium_confidence_suggestions


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


def process_and_store_with_classification(
    pdf_path: str | Path,
    db_path: str | Path,
    config_path: Optional[str] = None,
    auto_assign_high_confidence: bool = True,
) -> Tuple[int, int, List[Tuple[int, str, str, float]]]:
    """
    Process PDF, store operations, and classify them using the operations matcher
    
    Args:
        pdf_path: Path to the PDF file
        db_path: Path to the database
        config_path: Optional path to operations matching configuration
        auto_assign_high_confidence: Whether to automatically assign high confidence classifications
        
    Returns:
        Tuple of (pdf_id, operations_count, classification_results)
        classification_results contains (operation_id, description, type_name, confidence)
    """
    pdf_path = Path(pdf_path)
    engine = get_engine(db_path)
    init_db(engine)
    
    with Session(engine) as session:
        # Process PDF and extract operations
        summary = process_pdf(str(pdf_path))
        pdf_id = store_pdf_summary(session, str(pdf_path), summary)
        operations, suggestions = extract_and_classify_operations(str(pdf_path), config_path)
        
        # Store operations
        n = store_operations(session, pdf_id, operations)
        
        # Get operation type mappings
        type_name_to_id = {ot.name: ot.id for ot in get_operation_types(session)}
        
        # Process high confidence suggestions for auto-assignment
        high_confidence = get_high_confidence_suggestions(suggestions)
        classification_results = []
        
        if auto_assign_high_confidence:
            for suggestion in high_confidence:
                type_id = type_name_to_id.get(suggestion.type_name)
                if type_id:
                    # Find the operation by description and assign type
                    operation = session.exec(
                        select(OperationRow).where(
                            OperationRow.pdf_id == pdf_id,
                            OperationRow.description == operations[suggestion.operation_id].description
                        )
                    ).first()
                    
                    if operation:
                        operation.type_id = type_id
                        session.add(operation)
                        classification_results.append((
                            operation.id,
                            operation.description,
                            suggestion.type_name,
                            suggestion.confidence
                        ))
            
            session.commit()
        
        return pdf_id, n, classification_results


def get_classification_suggestions_for_pdf(
    session: Session,
    pdf_id: int,
    config_path: Optional[str] = None,
) -> List[Tuple[OperationRow, str, float, str]]:
    """
    Get classification suggestions for operations in a PDF that don't have types assigned
    
    Args:
        session: Database session
        pdf_id: PDF ID
        config_path: Optional path to operations matching configuration
        
    Returns:
        List of (operation, suggested_type, confidence, method) tuples
    """
    from operations_matcher import get_matcher
    
    # Get operations without types
    unclassified_operations = get_operations_with_null_types(session, pdf_id)
    
    if not unclassified_operations:
        return []
    
    try:
        matcher = get_matcher(config_path)
        suggestions = []
        
        for operation in unclassified_operations:
            if operation.description:
                result = matcher.classify_operation(operation.description)
                if result:
                    suggestions.append((
                        operation,
                        result.type_name,
                        result.confidence,
                        result.method
                    ))
        
        return suggestions
    except Exception:
        return []


def auto_assign_high_confidence_operations(
    session: Session,
    pdf_id: int,
    config_path: Optional[str] = None,
) -> int:
    """
    Automatically assign types to operations with high confidence classifications
    
    Args:
        session: Database session
        pdf_id: PDF ID
        config_path: Optional path to operations matching configuration
        
    Returns:
        Number of operations auto-assigned
    """
    suggestions = get_classification_suggestions_for_pdf(session, pdf_id, config_path)
    
    if not suggestions:
        return 0
    
    # Get operation type mappings
    type_name_to_id = {ot.name: ot.id for ot in get_operation_types(session)}
    
    # Get thresholds from config
    try:
        from operations_matcher import get_matcher
        matcher = get_matcher(config_path)
        thresholds = matcher.config['confidence_thresholds']
    except Exception:
        # Default thresholds if config not available
        thresholds = {
            'fuzzy_match_auto': 95,
            'keyword_match_auto': 80,
            'pattern_match_auto': 75
        }
    
    assigned_count = 0
    
    for operation, suggested_type, confidence, method in suggestions:
        # Determine if should auto-assign based on method and confidence
        should_auto_assign = False
        
        if method == 'exact':
            should_auto_assign = True
        elif method == 'fuzzy' and confidence >= thresholds.get('fuzzy_match_auto', 95):
            should_auto_assign = True
        elif method == 'keyword' and confidence >= thresholds.get('keyword_match_auto', 80):
            should_auto_assign = True
        elif method == 'pattern' and confidence >= thresholds.get('pattern_match_auto', 75):
            should_auto_assign = True
        
        if should_auto_assign:
            type_id = type_name_to_id.get(suggested_type)
            if type_id:
                operation.type_id = type_id
                session.add(operation)
                assigned_count += 1
    
    if assigned_count > 0:
        session.commit()
    
    return assigned_count


def auto_assign_all_high_confidence_operations(
    session: Session,
    config_path: Optional[str] = None,
) -> int:
    """
    Automatically assign types to all operations with high confidence classifications
    across all PDFs
    
    Args:
        session: Database session
        config_path: Optional path to operations matching configuration
        
    Returns:
        Number of operations auto-assigned
    """
    # Get all unclassified operations
    unclassified_operations = get_operations_with_null_types(session)
    
    if not unclassified_operations:
        return 0
    
    # Get operation type mappings
    type_name_to_id = {ot.name: ot.id for ot in get_operation_types(session)}
    
    # Get thresholds from config
    try:
        from operations_matcher import get_matcher
        matcher = get_matcher(config_path)
        thresholds = matcher.config['confidence_thresholds']
    except Exception:
        # Default thresholds if config not available
        thresholds = {
            'fuzzy_match_auto': 95,
            'keyword_match_auto': 80,
            'pattern_match_auto': 75
        }
    
    assigned_count = 0
    
    for operation in unclassified_operations:
        if operation.description:
            result = matcher.classify_operation(operation.description)
            if result:
                # Determine if should auto-assign based on method and confidence
                should_auto_assign = False
                
                if result.method == 'exact':
                    should_auto_assign = True
                elif result.method == 'fuzzy' and result.confidence >= thresholds.get('fuzzy_match_auto', 95):
                    should_auto_assign = True
                elif result.method == 'keyword' and result.confidence >= thresholds.get('keyword_match_auto', 80):
                    should_auto_assign = True
                elif result.method == 'pattern' and result.confidence >= thresholds.get('pattern_match_auto', 75):
                    should_auto_assign = True
                
                if should_auto_assign:
                    type_id = type_name_to_id.get(result.type_name)
                    if type_id:
                        operation.type_id = type_id
                        session.add(operation)
                        assigned_count += 1
    
    if assigned_count > 0:
        session.commit()
    
    return assigned_count


