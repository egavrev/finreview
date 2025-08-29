import pytest

import sql_utils as db
from pdf_processor import PDFSummary, Operation


@pytest.fixture()
def temp_session(tmp_path):
    db_file = tmp_path / "test.db"
    engine = db.get_engine(db_file)
    db.init_db(engine)
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


def test_init_db_idempotent(tmp_path):
    db_file = tmp_path / "idempotent.db"
    engine = db.get_engine(db_file)
    db.init_db(engine)
    db.init_db(engine)
    # Verify via SQLModel metadata tables exist by simple insert/select
    from sqlmodel import Session, select
    with Session(engine) as session:
        # no exception on simple select
        session.exec(select(db.PDF)).first()


def test_store_pdf_summary_and_fetch(temp_session, tmp_path):
    summary = PDFSummary(
        client_name="John Doe",
        account_number="MD12BANK0000000000000000",
        total_iesiri=123.45,
        sold_initial=1000.0,
        sold_final=900.0,
    )
    pdf_path = tmp_path / "file.pdf"
    pdf_id = db.store_pdf_summary(temp_session, pdf_path, summary)
    assert isinstance(pdf_id, int)
    row = db.get_pdf_by_path(temp_session, pdf_path)
    assert row.client_name == "John Doe"
    assert row.account_number.startswith("MD12")

    # Upsert should update
    summary2 = PDFSummary(
        client_name="Jane Doe",
        account_number="MD12BANK1111111111111111",
        total_iesiri=200.0,
        sold_initial=1100.0,
        sold_final=900.0,
    )
    pdf_id2 = db.store_pdf_summary(temp_session, pdf_path, summary2)
    assert pdf_id2 == pdf_id
    row2 = db.get_pdf_by_path(temp_session, pdf_path)
    assert row2.client_name == "Jane Doe"
    assert row2.total_iesiri == 200.0


def test_store_operations_replace_and_list(temp_session):
    # Create a pdf parent
    pdf_id = db.store_pdf_summary(
        temp_session,
        "/tmp/fake.pdf",
        PDFSummary("A", "ACC", 0.0, 0.0, 0.0),
    )
    ops = [
        Operation("2025-08-01", "2025-08-02", "SHOP A", 10.5),
        Operation("2025-08-03", "2025-08-04", "SHOP B", -9.0),
    ]
    inserted = db.store_operations(temp_session, pdf_id, ops)
    assert inserted == 2
    rows = db.get_operations_for_pdf(temp_session, pdf_id)
    assert [r.description for r in rows] == ["SHOP A", "SHOP B"]

    # Replace existing
    ops2 = [Operation("2025-08-05", None, "SHOP C", 1.0)]
    inserted2 = db.store_operations(temp_session, pdf_id, ops2, replace_existing=True)
    assert inserted2 == 1
    rows2 = db.get_operations_for_pdf(temp_session, pdf_id)
    assert len(rows2) == 1 and rows2[0].description == "SHOP C"


def test_process_and_store_integration(monkeypatch, tmp_path):
    # Stub out heavy PDF processing with predictable results
    fake_summary = PDFSummary("Client X", "MD12ABCD0000000000000000", 50.0, 100.0, 150.0)
    fake_ops = [
        Operation("01.01.2025", "02.01.2025", "M1", 10.0),
        Operation("03.01.2025", None, "M2", 40.0),
    ]
    monkeypatch.setattr(db, "process_pdf", lambda p: fake_summary)
    monkeypatch.setattr(db, "extract_card_operations", lambda p: fake_ops)

    pdf_path = tmp_path / "doc.pdf"
    db_path = tmp_path / "db.sqlite"
    pdf_id, n = db.process_and_store(pdf_path, db_path)

    # Verify persisted content
    engine = db.get_engine(db_path)
    from sqlmodel import Session
    with Session(engine) as session:
        row = db.get_pdf_by_path(session, pdf_path)
        assert row.client_name == "Client X"
        ops_rows = db.get_operations_for_pdf(session, row.id)
        assert len(ops_rows) == 2


