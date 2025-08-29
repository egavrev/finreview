import json
from types import SimpleNamespace
from pathlib import Path
import builtins

import pytest

import pdf_processor as mod


class FakePage:
    def __init__(self, text="", tables=None):
        self._text = text
        self._tables = tables if tables is not None else []

    def extract_text(self, x_tolerance=1.5, y_tolerance=1.5):
        return self._text

    def extract_tables(self):
        return self._tables


class FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakePdfPlumber:
    def __init__(self, pdf):
        self._pdf = pdf

    def open(self, path):
        return self._pdf


def setup_fake_pdf(monkeypatch, pages):
    fake_pdf = FakePDF(pages)
    monkeypatch.setattr(mod, "pdfplumber", FakePdfPlumber(fake_pdf))
    # Clear any previous import error to avoid RuntimeError paths
    monkeypatch.setattr(mod, "_import_error", None)


def test_normalize_number_various_formats():
    assert mod._normalize_number("1,234.56") == 1234.56
    assert mod._normalize_number("1.234,56") == 1234.56
    assert mod._normalize_number("1 234,56") == 1234.56
    assert mod._normalize_number("1\u00A0234,56") == 1234.56
    assert mod._normalize_number("-12,34") == -12.34
    assert mod._normalize_number(None) is None
    assert mod._normalize_number("") is None


def test_parse_amount_patterns():
    assert mod._parse_amount("Total: 1.234,56 MDL") == 1234.56
    # Spaced sign isn't attached to the number per current regex, so positive
    assert mod._parse_amount("- 99,99") == 99.99
    assert mod._parse_amount("No number here") is None


def test_extract_card_operations_tables_happy_path(monkeypatch):
    header = ["Data", "Procesare", "Descriere", "Suma (LEI)"]
    rows = [
        header,
        ["01.08.2025", "02.08.2025", "MAGAZIN ABC", "123,45"],
        ["03.08.2025", "04.08.2025", "SUPERMARKET XYZ", "-67,89"],
    ]
    pages = [
        FakePage(text="Cardul număr 1234\nExtras", tables=[rows]),
    ]
    setup_fake_pdf(monkeypatch, pages)
    # Pretend the file exists
    monkeypatch.setattr(mod.Path, "exists", lambda self: True)

    ops = mod.extract_card_operations("/tmp/fake.pdf")
    assert len(ops) == 2
    assert ops[0].description == "MAGAZIN ABC"
    assert ops[0].amount_lei == 123.45
    assert ops[1].amount_lei == -67.89


def test_extract_card_operations_no_tables_text_fallback(monkeypatch):
    # No tables; fallback should parse lines with currency amounts
    line1 = "01.08.2025 02.08.2025 MERCHANT ONE MDL 10,50"
    line2 = "2025-08-03 2025-08-04 MERCHANT TWO USD 3,25"
    pages = [FakePage(text=f"{line1}\n{line2}\nBalance 999,99", tables=[])]
    setup_fake_pdf(monkeypatch, pages)
    monkeypatch.setattr(mod.Path, "exists", lambda self: True)

    ops = mod.extract_card_operations("/tmp/fake.pdf")
    # USD should be accepted; amount kept positive for MDL per logic
    assert len(ops) == 2
    assert ops[0].description == "MERCHANT ONE"
    assert ops[0].amount_lei == 10.5
    assert ops[1].description == "MERCHANT TWO"
    assert ops[1].amount_lei == 3.25


def test_search_patterns_detects_fields():
    text = (
        "Clientul: Ion Popescu\n"
        "Numarul contului: MD12AGRN0000000000000000\n"
        "Sold initial: 1.234,00\n"
        "Total iesiri: 123,45\n"
        "Sold final: 1.110,55\n"
    )
    client, account, total_iesiri, sold_initial, sold_final = mod._search_patterns(text)
    assert client.startswith("Ion")
    assert account.startswith("MD12")
    assert total_iesiri == 123.45
    assert sold_initial == 1234.0
    assert sold_final == 1110.55


def test_compute_total_iesiri_from_tables_sums_debits(monkeypatch):
    header = ["Descriere", "Debit"]
    rows = [
        header,
        ["Plata 1", "10,00"],
        ["Plata 2", "5,50"],
        ["Plata 3", "not a number"],
    ]
    pages = [FakePage(text="", tables=[rows])]
    setup_fake_pdf(monkeypatch, pages)

    total = mod._compute_total_iesiri_from_tables(Path("/tmp/fake.pdf"))
    assert total == 15.5


def test_process_pdf_uses_fallback_when_label_total_missing(monkeypatch):
    # Force text without labeled total iesiri; rely on compute fallback
    monkeypatch.setattr(mod, "_extract_text_from_pdf", lambda p: "Sold initial: 1,00\nSold final: 2,00")
    monkeypatch.setattr(mod, "_compute_total_iesiri_from_tables", lambda p: 42.0)
    monkeypatch.setattr(mod.Path, "exists", lambda self: True)

    # Account detection via IBAN in text fallback
    summary = mod.process_pdf("/tmp/any.pdf")
    assert isinstance(summary, mod.PDFSummary)
    assert summary.total_iesiri == 42.0
    assert summary.sold_initial == 1.0
    assert summary.sold_final == 2.0


def test_extract_card_operations_handles_missing_columns_and_anchor(monkeypatch):
    # Header without clear amount label; anchor present should allow fallback to last column
    header = ["A", "B", "C"]
    rows = [header, ["01.01.2025", "02.01.2025", "-12,34"]]
    pages = [FakePage(text="Some text with Cardul number anchoring", tables=[rows])]
    setup_fake_pdf(monkeypatch, pages)
    monkeypatch.setattr(mod.Path, "exists", lambda self: True)

    ops = mod.extract_card_operations("/tmp/fake.pdf")
    assert len(ops) == 1
    assert ops[0].amount_lei == -12.34


def test_main_cli_json_output(monkeypatch, capsys):
    # Provide a simple table extraction path and run main
    header = ["Data", "Descriere", "Suma (LEI)"]
    rows = [header, ["01.01.2025", "SHOP", "1,00"]]
    pages = [FakePage(text="Cardul number 123", tables=[rows])]
    setup_fake_pdf(monkeypatch, pages)

    # Fake argv and existence
    monkeypatch.setattr(mod.sys, "argv", ["prog", "/tmp/fake.pdf"])
    monkeypatch.setattr(mod.Path, "exists", lambda self: True)

    mod.main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list) and data[0]["description"] == "SHOP"


