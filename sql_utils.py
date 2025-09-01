from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import hashlib

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
    operation_hash: Optional[str] = Field(default=None, index=True)  # Hash for deduplication


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


def generate_operation_hash(operation: Operation) -> str:
    """
    Generate a hash for an operation based on its key fields.
    This creates a unique identifier for deduplication purposes.
    Note: Excludes processed_date as it can vary between different PDF files for the same transaction.
    """
    # Create a string representation of the operation's key fields
    # Exclude processed_date as it can vary between different PDF files
    hash_string = f"{operation.transaction_date}|{operation.description}|{operation.amount_lei}"
    
    # Generate SHA-256 hash
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()


def check_operation_exists_by_hash(session: Session, operation_hash: str) -> Optional[OperationRow]:
    """
    Check if an operation with the given hash already exists in the database.
    
    Args:
        session: Database session
        operation_hash: Hash of the operation to check
        
    Returns:
        OperationRow if found, None otherwise
    """
    return session.exec(select(OperationRow).where(OperationRow.operation_hash == operation_hash)).first()


def store_operations_with_deduplication(
    session: Session,
    pdf_id: int,
    operations: Iterable[Operation],
    *,
    replace_existing: bool = True,
    skip_duplicates: bool = True,
) -> Tuple[int, int]:
    """
    Store operations with hash-based deduplication.
    
    Args:
        session: Database session
        pdf_id: PDF ID
        operations: Operations to store
        replace_existing: Whether to replace existing operations for this PDF
        skip_duplicates: Whether to skip operations that already exist (by hash)
        
    Returns:
        Tuple of (stored_count, skipped_count)
    """
    if replace_existing:
        session.exec(delete(OperationRow).where(OperationRow.pdf_id == pdf_id))

    stored_count = 0
    skipped_count = 0
    
    for op in operations:
        # Generate hash for the operation
        operation_hash = generate_operation_hash(op)
        
        # Check if operation already exists (if skip_duplicates is True)
        if skip_duplicates:
            existing_operation = check_operation_exists_by_hash(session, operation_hash)
            if existing_operation:
                skipped_count += 1
                continue
        
        # Create new operation row
        row = OperationRow(
            pdf_id=pdf_id,
            transaction_date=op.transaction_date,
            processed_date=op.processed_date,
            description=op.description,
            amount_lei=op.amount_lei,
            operation_hash=operation_hash,
        )
        session.add(row)
        stored_count += 1
    
    session.commit()
    return stored_count, skipped_count


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


def store_operations_with_deduplication(
    session: Session,
    pdf_id: int,
    operations: Iterable[Operation],
    *,
    replace_existing: bool = True,
    skip_duplicates: bool = True,
) -> Tuple[int, int]:
    """
    Store operations with hash-based deduplication.
    
    Args:
        session: Database session
        pdf_id: PDF ID
        operations: Operations to store
        replace_existing: Whether to replace existing operations for this PDF
        skip_duplicates: Whether to skip operations that already exist (by hash)
        
    Returns:
        Tuple of (stored_count, skipped_count)
    """
    if replace_existing:
        session.exec(delete(OperationRow).where(OperationRow.pdf_id == pdf_id))

    stored_count = 0
    skipped_count = 0
    
    for op in operations:
        # Generate hash for the operation
        operation_hash = generate_operation_hash(op)
        
        # Check if operation already exists (if skip_duplicates is True)
        if skip_duplicates:
            existing_operation = check_operation_exists_by_hash(session, operation_hash)
            if existing_operation:
                skipped_count += 1
                continue
        
        # Create new operation row
        row = OperationRow(
            pdf_id=pdf_id,
            transaction_date=op.transaction_date,
            processed_date=op.processed_date,
            description=op.description,
            amount_lei=op.amount_lei,
            operation_hash=operation_hash,
        )
        session.add(row)
        stored_count += 1
    
    session.commit()
    return stored_count, skipped_count


def migrate_existing_operations_to_hashes(session: Session) -> int:
    """
    Add hashes to existing operations that don't have them.
    This is useful for migrating existing databases to use the hash system.
    
    Args:
        session: Database session
        
    Returns:
        Number of operations updated
    """
    # Get all operations without hashes
    operations_without_hash = session.exec(
        select(OperationRow).where(OperationRow.operation_hash.is_(None))
    ).all()
    
    updated_count = 0
    
    for operation in operations_without_hash:
        # Create a temporary Operation object to generate hash
        from pdf_processor import Operation
        temp_op = Operation(
            transaction_date=operation.transaction_date,
            processed_date=operation.processed_date,
            description=operation.description,
            amount_lei=operation.amount_lei,
        )
        
        # Generate and set the hash (processed_date is excluded in generate_operation_hash)
        operation.operation_hash = generate_operation_hash(temp_op)
        session.add(operation)
        updated_count += 1
    
    if updated_count > 0:
        session.commit()
    
    return updated_count


def get_duplicate_operations(session: Session) -> List[Tuple[OperationRow, OperationRow]]:
    """
    Find duplicate operations in the database based on their hashes.
    
    Args:
        session: Database session
        
    Returns:
        List of tuples containing duplicate operation pairs
    """
    from sqlalchemy import func
    
    # Find operations with the same hash (duplicates)
    duplicate_hashes = session.exec(
        select(OperationRow.operation_hash)
        .where(OperationRow.operation_hash.is_not(None))
        .group_by(OperationRow.operation_hash)
        .having(func.count(OperationRow.id) > 1)
    ).all()
    
    duplicates = []
    
    for hash_value in duplicate_hashes:
        if hash_value:
            operations_with_hash = session.exec(
                select(OperationRow).where(OperationRow.operation_hash == hash_value)
            ).all()
            
            # Create pairs of duplicates
            for i in range(len(operations_with_hash)):
                for j in range(i + 1, len(operations_with_hash)):
                    duplicates.append((operations_with_hash[i], operations_with_hash[j]))
    
    return duplicates


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
    skip_duplicates: bool = True,
) -> Tuple[int, int, int]:
    """
    Process PDF and store operations with optional deduplication.
    
    Args:
        pdf_path: Path to the PDF file
        db_path: Path to the database
        skip_duplicates: Whether to skip duplicate operations
        
    Returns:
        Tuple of (pdf_id, stored_count, skipped_count)
    """
    pdf_path = Path(pdf_path)
    engine = get_engine(db_path)
    init_db(engine)
    with Session(engine) as session:
        summary = process_pdf(str(pdf_path))
        pdf_id = store_pdf_summary(session, str(pdf_path), summary)
        ops = extract_card_operations(str(pdf_path))
        stored_count, skipped_count = store_operations_with_deduplication(
            session, pdf_id, ops, skip_duplicates=skip_duplicates
        )
        return pdf_id, stored_count, skipped_count


def process_and_store_with_classification(
    pdf_path: str | Path,
    db_path: str | Path,
    config_path: Optional[str] = None,
    auto_assign_high_confidence: bool = True,
    skip_duplicates: bool = True,
) -> Tuple[int, int, int, List[Tuple[int, str, str, float]]]:
    """
    Process PDF, store operations, and classify them using the operations matcher
    
    Args:
        pdf_path: Path to the PDF file
        db_path: Path to the database
        config_path: Optional path to operations matching configuration
        auto_assign_high_confidence: Whether to automatically assign high confidence classifications
        skip_duplicates: Whether to skip duplicate operations
        
    Returns:
        Tuple of (pdf_id, stored_count, skipped_count, classification_results)
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
        
        # Store operations with deduplication
        stored_count, skipped_count = store_operations_with_deduplication(
            session, pdf_id, operations, skip_duplicates=skip_duplicates
        )
        
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
        
        return pdf_id, stored_count, skipped_count, classification_results


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


def get_monthly_report_data(
    session: Session,
    year: int,
    month: int,
) -> dict:
    """
    Get monthly report data grouped by operation types
    
    Args:
        session: Database session
        year: Year for the report
        month: Month for the report (1-12)
        
    Returns:
        Dictionary with pie chart data and summary statistics
    """
    from sqlalchemy import func, extract
    
    # Get operations for the specified month
    operations_query = select(OperationRow, OperationType).outerjoin(
        OperationType, OperationRow.type_id == OperationType.id
    ).where(
        extract('year', func.date(OperationRow.transaction_date)) == year,
        extract('month', func.date(OperationRow.transaction_date)) == month
    )
    
    operations_with_types = session.exec(operations_query).all()
    
    # Group by operation type
    type_groups = {}
    total_amount = 0
    total_operations = 0
    
    for op, op_type in operations_with_types:
        type_name = op_type.name if op_type else "Uncategorized"
        type_id = op_type.id if op_type else None
        
        if type_name not in type_groups:
            type_groups[type_name] = {
                "type_id": type_id,
                "type_name": type_name,
                "total_amount": 0,
                "operation_count": 0,
                "operations": []
            }
        
        amount = op.amount_lei or 0
        type_groups[type_name]["total_amount"] += amount
        type_groups[type_name]["operation_count"] += 1
        type_groups[type_name]["operations"].append({
            "id": op.id,
            "transaction_date": op.transaction_date,
            "processed_date": op.processed_date,
            "description": op.description,
            "amount_lei": op.amount_lei,
        })
        
        total_amount += amount
        total_operations += 1
    
    # Sort operations within each group by amount (descending)
    for group in type_groups.values():
        group["operations"].sort(key=lambda x: x["amount_lei"] or 0, reverse=True)
    
    # Create pie chart data
    pie_chart_data = [
        {
            "name": group["type_name"],
            "value": group["total_amount"],
            "color": f"hsl({hash(group['type_name']) % 360}, 70%, 50%)"
        }
        for group in type_groups.values()
        if group["total_amount"] > 0
    ]
    
    # Sort groups by total amount (descending)
    sorted_groups = sorted(
        type_groups.values(),
        key=lambda x: x["total_amount"],
        reverse=True
    )
    
    return {
        "year": year,
        "month": month,
        "total_amount": total_amount,
        "total_operations": total_operations,
        "type_groups": sorted_groups,
        "pie_chart_data": pie_chart_data,
        "summary": {
            "average_amount_per_operation": total_amount / total_operations if total_operations > 0 else 0,
            "most_expensive_type": sorted_groups[0]["type_name"] if sorted_groups else None,
            "most_expensive_amount": sorted_groups[0]["total_amount"] if sorted_groups else 0,
        }
    }


def get_available_months(session: Session) -> List[dict]:
    """
    Get list of available months with data
    
    Returns:
        List of dictionaries with year and month
    """
    from sqlalchemy import func, extract
    
    # Get unique year-month combinations from operations
    query = select(
        extract('year', func.date(OperationRow.transaction_date)).label('year'),
        extract('month', func.date(OperationRow.transaction_date)).label('month')
    ).distinct().where(
        OperationRow.transaction_date.is_not(None)
    ).order_by(
        extract('year', func.date(OperationRow.transaction_date)).desc(),
        extract('month', func.date(OperationRow.transaction_date)).desc()
    )
    
    results = session.exec(query).all()
    
    return [
        {
            "year": int(year),
            "month": int(month),
            "label": f"{year}-{month:02d}"
        }
        for year, month in results
        if year is not None and month is not None
    ]


def get_operations_by_type_for_month(
    session: Session,
    type_id: int,
    year: int,
    month: int,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """
    Get operations of a specific type for a given month with pagination
    
    Args:
        session: Database session
        type_id: Operation type ID
        year: Year
        month: Month (1-12)
        limit: Number of operations to return
        offset: Number of operations to skip
        
    Returns:
        Dictionary with operations and pagination info
    """
    from sqlalchemy import func, extract
    
    # Get operation type
    op_type = get_operation_type_by_id(session, type_id)
    if not op_type:
        return {"error": "Operation type not found"}
    
    # Get operations for the type and month
    query = select(OperationRow).where(
        OperationRow.type_id == type_id,
        extract('year', func.date(OperationRow.transaction_date)) == year,
        extract('month', func.date(OperationRow.transaction_date)) == month
    ).order_by(
        OperationRow.amount_lei.desc()
    ).offset(offset).limit(limit)
    
    operations = session.exec(query).all()
    
    # Get total count for pagination
    count_query = select(func.count(OperationRow.id)).where(
        OperationRow.type_id == type_id,
        extract('year', func.date(OperationRow.transaction_date)) == year,
        extract('month', func.date(OperationRow.transaction_date)) == month
    )
    total_count = session.exec(count_query).first()
    
    return {
        "type": {
            "id": op_type.id,
            "name": op_type.name,
            "description": op_type.description,
        },
        "year": year,
        "month": month,
        "operations": [
            {
                "id": op.id,
                "pdf_id": op.pdf_id,
                "transaction_date": op.transaction_date,
                "processed_date": op.processed_date,
                "description": op.description,
                "amount_lei": op.amount_lei,
            }
            for op in operations
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_count,
            "has_more": (offset + limit) < total_count
        }
    }


