import json
import sys
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple

# Import operations matcher
try:
    from operations_matcher import get_matcher, MatchResult, ClassificationSuggestion
except ImportError:
    # Fallback if operations_matcher is not available
    get_matcher = None
    MatchResult = None
    ClassificationSuggestion = None


try:
    import pdfplumber  # type: ignore
except Exception as exc:  # pragma: no cover
    pdfplumber = None
    _import_error = exc
else:
    _import_error = None


@dataclass
class PDFSummary:
    client_name: Optional[str]
    account_number: Optional[str]
    total_iesiri: Optional[float]
    sold_initial: Optional[float]
    sold_final: Optional[float]


# Support thousands separated by dot/comma/space/nbsp and decimal with dot/comma
_NUM_PATTERN = r"[-+]?\d{1,3}(?:[\.,\s\u00A0]\d{3})*(?:[\.,]\d{2})?"
_NUM_WITH_DECIMALS_PATTERN = r"[-+]?\d{1,3}(?:[\.,\s\u00A0]\d{3})*[\.,]\d{2}"


@dataclass
class Operation:
    transaction_date: Optional[str]
    processed_date: Optional[str]
    description: Optional[str]
    amount_lei: Optional[float]


def _normalize_number(value: str) -> Optional[float]:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    # Handle Romanian/European formatting where comma is decimal separator
    text = text.replace("\xa0", "").replace(" ", "")
    # If both separators present, assume last one is decimal
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        # If only comma present, treat as decimal separator
        if "," in text:
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text
    try:
        return float(text)
    except ValueError:
        return None


def _extract_text_from_pdf(pdf_path: Path) -> str:
    if pdfplumber is None:
        raise RuntimeError(
            f"pdfplumber is required to read PDFs but failed to import: {_import_error}"
        )
    text_parts: List[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            # Extract text; preserve layout when possible
            page_text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5) or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def _find_pages_with_card_section(pdf_path: Path) -> List[int]:
    if pdfplumber is None:
        return []
    pages_with_card: List[int] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for idx, page in enumerate(pdf.pages):
            page_text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5) or ""
            if re.search(r"Cardul\s+num(?:e|ă|a)r|Cardul\s+number", page_text, re.IGNORECASE):
                pages_with_card.append(idx)
    return pages_with_card


def _parse_amount(text: Optional[str]) -> Optional[float]:
    if not text or not isinstance(text, str):
        return None
    # Keep only first numeric with decimals
    m = re.search(_NUM_WITH_DECIMALS_PATTERN, text)
    if not m:
        # fallback to any number
        m = re.search(_NUM_PATTERN, text or "")
    if not m:
        return None
    return _normalize_number(m.group(0))


def extract_card_operations(pdf_path: str, debug: bool = False) -> List[Operation]:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdfplumber is None:
        raise RuntimeError(
            f"pdfplumber is required to read PDFs but failed to import: {_import_error}"
        )

    def _dbg(msg: str) -> None:
        if debug:
            print(f"[debug] {msg}", file=sys.stderr)

    operations: List[Operation] = []
    candidate_pages = _find_pages_with_card_section(path)
    if not candidate_pages:
        # if not found by text, try all pages
        candidate_pages = list(range(0, 10000))  # will be clipped by actual page count

    with pdfplumber.open(str(path)) as pdf:
        max_page_index = len(pdf.pages) - 1
        pages_to_scan = [p for p in candidate_pages if 0 <= p <= max_page_index]
        _dbg(f"pages_to_scan={len(pages_to_scan)} (of {len(pdf.pages)})")
        if not pages_to_scan:
            pages_to_scan = list(range(len(pdf.pages)))

        for page_index in pages_to_scan:
            page = pdf.pages[page_index]
            tables = page.extract_tables() or []
            _dbg(f"page {page_index+1}: tables_found={len(tables)}")
            if not tables:
                continue
            page_text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5) or ""
            has_card_anchor = re.search(r"Cardul\s+num(?:e|ă|a)r|Cardul\s+number", page_text, re.IGNORECASE) is not None

            for tbl in tables:
                if not tbl or len(tbl) < 2:
                    continue
                header = tbl[0]
                # Heuristically detect expected columns
                col_map = {"date": None, "processed": None, "description": None, "amount": None}  # type: ignore[var-annotated]
                for idx, col in enumerate(header):
                    label = (col or "").strip().lower()
                    if not label:
                        continue
                    if col_map["date"] is None and re.search(r"data|tranzac", label):
                        col_map["date"] = idx
                    if col_map["processed"] is None and re.search(r"proces|post|valut|settle", label):
                        col_map["processed"] = idx
                    if col_map["description"] is None and re.search(r"descr|detali|merchant|descriere", label):
                        col_map["description"] = idx
                    if col_map["amount"] is None and re.search(r"lei|sum|amount|valoare|debit|plati", label):
                        col_map["amount"] = idx

                # If we didn't detect a meaningful amount column, skip unless page has the card anchor
                if col_map["amount"] is None and not has_card_anchor:
                    continue

                # Fallbacks: try last column as amount, and choose plausible others by common patterns
                if col_map["amount"] is None:
                    col_map["amount"] = len(header) - 1
                if col_map["description"] is None and len(header) >= 2:
                    # pick the wordiest column
                    wordiest_idx = max(range(len(header)), key=lambda i: len((header[i] or "")))
                    if wordiest_idx != col_map["amount"]:
                        col_map["description"] = wordiest_idx
                # If still no date columns, we keep them None; we won't fail the row on that basis

                # Iterate rows
                for row in tbl[1:]:
                    if not any(cell for cell in row):
                        continue
                    try:
                        desc_cell = row[col_map["description"]] if col_map["description"] is not None and col_map["description"] < len(row) else None
                        amount_cell = row[col_map["amount"]] if col_map["amount"] is not None and col_map["amount"] < len(row) else None
                        date_cell = row[col_map["date"]] if col_map["date"] is not None and col_map["date"] < len(row) else None
                        processed_cell = row[col_map["processed"]] if col_map["processed"] is not None and col_map["processed"] < len(row) else None
                    except Exception:
                        continue

                    # Clean description: join multiline cells
                    def normalize_cell(c: Optional[str]) -> Optional[str]:
                        if c is None:
                            return None
                        if isinstance(c, str):
                            return c.replace("\n", " ").strip()
                        return str(c)

                    description = normalize_cell(desc_cell)
                    amount = _parse_amount(amount_cell if isinstance(amount_cell, str) else (str(amount_cell) if amount_cell is not None else None))
                    transaction_date = normalize_cell(date_cell)
                    processed_date = normalize_cell(processed_cell)

                    # Basic validity: must have description and amount
                    if description and amount is not None:
                        operations.append(
                            Operation(
                                transaction_date=transaction_date,
                                processed_date=processed_date,
                                description=description,
                                amount_lei=amount,
                            )
                        )

            # If we found a good number of operations on a card-anchored page, we can stop early
            if has_card_anchor and len(operations) >= 5:
                # Likely captured the card table already
                break

    _dbg(f"operations_from_tables={len(operations)}")

    # Text-line fallback if nothing was detected from tables
    if not operations:
        text = _extract_text_from_pdf(path)

        date_regex = re.compile(r"\b(?:\d{2}[./-]\d{2}[./-]\d{2,4}|\d{4}[./-]\d{2}[./-]\d{2})\b")
        currency_amount_regex = re.compile(
            rf"\b(?P<ccy>MDL|USD|EUR)\b\s*(?P<amt>{_NUM_WITH_DECIMALS_PATTERN})",
            re.IGNORECASE,
        )

        def find_dates(s: str) -> List[Tuple[int, int, str]]:
            return [(m.start(), m.end(), m.group(0)) for m in date_regex.finditer(s)]

        text_ops: List[Operation] = []
        for raw_line in text.splitlines():
            line = (raw_line or "").replace("\u00A0", " ").strip()
            if not line:
                continue

            # Try to match currency-amount; this avoids picking the trailing balance number
            m_ca = currency_amount_regex.search(line)
            if not m_ca:
                continue
            currency = (m_ca.group("ccy") or "").upper()
            amount = _normalize_number(m_ca.group("amt"))
            if amount is None:
                continue
            if currency == "MDL":
                amount = abs(amount)

            # Extract dates (transaction and processed)
            dates = find_dates(line)
            transaction_date = dates[0][2] if len(dates) >= 1 else None
            processed_date = dates[1][2] if len(dates) >= 2 else None

            # Merchant name is the text between the last date and the currency token
            last_date_end = dates[1][1] if len(dates) >= 2 else (dates[0][1] if dates else 0)
            merchant_segment = line[last_date_end:m_ca.start()].strip()
            # Clean merchant: collapse spaces and quotes
            merchant = re.sub(r"\s+", " ", merchant_segment)
            merchant = merchant.strip('"\'').strip()
            # Heuristics: take the longest word-ish token phrase containing letters
            if not re.search(r"[A-Za-zĂÂÎȘŞȚŢăâîșşțţ]", merchant):
                continue
            # Remove obvious filler like currency codes or double spaces
            merchant = merchant.replace("MDL", "").replace("USD", "").replace("EUR", "").strip()
            # Remove stray quotes completely
            merchant = merchant.replace('"', "").replace("'", "")
            # Shorten merchant by removing leading/trailing dates or separators left over
            merchant = re.sub(r"^[\-–—:\s]+|[\-–—:\s]+$", "", merchant)
            # Drop any trailing signed amount left in the merchant segment (e.g., " -143.00")
            merchant = re.sub(rf"\s*[-+]?({_NUM_WITH_DECIMALS_PATTERN}|{_NUM_PATTERN})\s*$", "", merchant)
            # Drop trailing pattern like "- 412" or "-412" (store internal codes)
            merchant = re.sub(r"\s*[\-–—]\s*\d{1,6}\s*$", "", merchant)
            # Normalize excess spaces
            merchant = re.sub(r"\s+", " ", merchant).strip()

            if not merchant:
                continue

            text_ops.append(
                Operation(
                    transaction_date=transaction_date,
                    processed_date=processed_date,
                    description=merchant,
                    amount_lei=amount,
                )
            )

        _dbg(f"operations_from_text_fallback={len(text_ops)}")
        if text_ops:
            operations = text_ops

    return operations


def _search_patterns(text: str) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[float], Optional[float]]:
    # Romanian labels (variants and diacritics)
    client_patterns = [
        r"Clientul\s*[:\-]?\s*(?P<val>.+)",
        r"Nume\s+client\s*[:\-]?\s*(?P<val>.+)",
        r"Titular\s*[:\-]?\s*(?P<val>.+)",
    ]

    account_patterns = [
        r"Num[aă]r(?:ul)?\s+contului\s*[:\-]?\s*(?P<val>[^\r\n]+)",
        r"IBAN\s*[:\-]?\s*(?P<val>[^\r\n]+)",
    ]

    sold_initial_patterns = [
        rf"Sold(?:ul)?\s+ini(?:ț|ţ|t)i?al\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
        rf"Sold\s+de\s+deschidere\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
    ]

    sold_final_patterns = [
        rf"Sold(?:ul)?\s+fin(?:a|ă)l\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
        rf"Sold\s+de\s+închidere\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
        rf"Sold\s+de\s+inchidere\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
    ]

    total_iesiri_patterns = [
        rf"Total\s+ie[sșş]ir[iîí]\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
        rf"Total\s+pl[aă]t[iîí]\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
        rf"Total\s+debit\s*[:\-]?\s*(?P<val>{_NUM_PATTERN})",
    ]

    # In some PDFs, the amount is on the next column/line. Search forward after label if direct match fails.
    def find_after(label_regex: str) -> Optional[str]:
        m = re.search(label_regex, text, re.IGNORECASE)
        if not m:
            return None
        # Look ahead a limited window for the first number
        start_idx = m.end()
        window = text[start_idx:start_idx + 120]
        mnum = re.search(_NUM_PATTERN, window)
        return mnum.group(0) if mnum else None

    def first_match(patterns: List[str], flags: int = re.IGNORECASE) -> Optional[str]:
        for pat in patterns:
            m = re.search(pat, text, flags)
            if m:
                return (m.group("val") or "").strip()
        return None

    client = first_match(client_patterns)
    account_line = first_match(account_patterns)
    sold_initial_str = first_match(sold_initial_patterns)
    if not sold_initial_str:
        sold_initial_str = find_after(r"Sold(?:ul)?\s+ini(?:ț|ţ|t)i?al")

    sold_final_str = first_match(sold_final_patterns)
    if not sold_final_str:
        sold_final_str = find_after(r"Sold(?:ul)?\s+fin(?:a|ă)l|Sold\s+de\s+închidere|Sold\s+de\s+inchidere")

    total_iesiri_str = first_match(total_iesiri_patterns)
    if not total_iesiri_str:
        total_iesiri_str = find_after(r"Total\s+ie[sșş]ir[iîí]|Total\s+pl[aă]t[iîí]|Total\s+debit")

    sold_initial = _normalize_number(sold_initial_str) if sold_initial_str else None
    sold_final = _normalize_number(sold_final_str) if sold_final_str else None
    total_iesiri = _normalize_number(total_iesiri_str) if total_iesiri_str else None

    # Post-process account: try to extract a plausible IBAN from the same line or entire text
    account: Optional[str] = None
    iban_regex = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
    if account_line:
        m = iban_regex.search(account_line.replace(" ", "")) or iban_regex.search(account_line)
        if m:
            account = m.group(0).upper()
        else:
            # Fallback: take first long token starting with country letters (MD/RO/DE/etc.)
            tokens = re.split(r"\s+", account_line.strip())
            for tok in tokens:
                tok_clean = re.sub(r"[^A-Za-z0-9]", "", tok)
                if len(tok_clean) >= 16 and tok_clean[:2].isalpha():
                    account = tok_clean.upper()
                    break
    if account is None:
        m_any = iban_regex.search(text.replace(" ", "")) or iban_regex.search(text)
        if m_any:
            account = m_any.group(0).upper()

    return client, account, total_iesiri, sold_initial, sold_final


def _compute_total_iesiri_from_tables(pdf_path: Path) -> Optional[float]:
    if pdfplumber is None:
        return None
    total_out: float = 0.0
    found_any = False
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for tbl in tables:
                # Heuristic: find header row and detect a column that looks like iesiri/debit/out/withdrawal
                header = None
                for row in tbl:
                    if row and any(isinstance(cell, str) and cell.strip() for cell in row):
                        header = row
                        break
                if not header:
                    continue
                debit_idx: Optional[int] = None
                for idx, col in enumerate(header):
                    label = (col or "").strip().lower()
                    if any(key in label for key in ["ies", "debit", "plati", "ieș", "iesiri", "ieșiri", "plăti", "retragere"]):
                        debit_idx = idx
                        break
                if debit_idx is None:
                    # Try last column as a fallback
                    debit_idx = len(header) - 1
                # Sum numeric cells in that column, skipping header
                for row in tbl[1:]:
                    if debit_idx < len(row):
                        cell = row[debit_idx]
                        if isinstance(cell, str):
                            cell_text = cell.replace("\n", " ").strip()
                            # Avoid counting integers like dates; prefer values with decimals
                            m = re.search(_NUM_WITH_DECIMALS_PATTERN, cell_text)
                            if m:
                                num = _normalize_number(m.group(0))
                                if num is not None:
                                    found_any = True
                                    total_out += num
    return total_out if found_any else None


def process_pdf(pdf_path: str) -> PDFSummary:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    text = _extract_text_from_pdf(path)
    client, account, total_iesiri, sold_initial, sold_final = _search_patterns(text)
    if total_iesiri is None:
        computed = _compute_total_iesiri_from_tables(path)
        if computed is not None:
            total_iesiri = computed
    return PDFSummary(
        client_name=client,
        account_number=(account.replace(" ", "").upper() if account else None),
        total_iesiri=total_iesiri,
        sold_initial=sold_initial,
        sold_final=sold_final,
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Extract card operations from a PDF")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    ops = extract_card_operations(args.pdf, debug=getattr(args, "debug", False))
    print(json.dumps([asdict(op) for op in ops], ensure_ascii=False, indent=2))


# Operations matching functions
def classify_operations_with_matcher(operations: List[Operation], config_path: Optional[str] = None) -> List[ClassificationSuggestion]:
    """
    Classify operations using the operations matcher
    
    Args:
        operations: List of operations to classify
        config_path: Optional path to configuration file
        
    Returns:
        List of classification suggestions
    """
    if get_matcher is None:
        return []
    
    try:
        matcher = get_matcher(config_path)
        # Convert operations to (id, description) tuples for the matcher
        operation_tuples = [(i, op.description) for i, op in enumerate(operations) if op.description]
        return matcher.get_classification_suggestions(operation_tuples)
    except Exception as e:
        print(f"Error in operations matching: {e}", file=sys.stderr)
        return []


def extract_and_classify_operations(pdf_path: str, config_path: Optional[str] = None, debug: bool = False) -> Tuple[List[Operation], List[ClassificationSuggestion]]:
    """
    Extract operations from PDF and classify them using the matcher
    
    Args:
        pdf_path: Path to the PDF file
        config_path: Optional path to configuration file
        debug: Enable debug logging
        
    Returns:
        Tuple of (operations, classification_suggestions)
    """
    # Extract operations
    operations = extract_card_operations(pdf_path, debug=debug)
    
    # Classify operations
    suggestions = classify_operations_with_matcher(operations, config_path)
    
    return operations, suggestions


def get_high_confidence_suggestions(suggestions: List[ClassificationSuggestion]) -> List[ClassificationSuggestion]:
    """
    Filter suggestions to only include high confidence ones that should be auto-assigned
    
    Args:
        suggestions: List of all classification suggestions
        
    Returns:
        List of high confidence suggestions for auto-assignment
    """
    return [s for s in suggestions if s.should_auto_assign]


def get_medium_confidence_suggestions(suggestions: List[ClassificationSuggestion]) -> List[ClassificationSuggestion]:
    """
    Filter suggestions to only include medium confidence ones for user review
    
    Args:
        suggestions: List of all classification suggestions
        
    Returns:
        List of medium confidence suggestions for user review
    """
    return [s for s in suggestions if not s.should_auto_assign and s.confidence >= 70]


if __name__ == "__main__":
    main()


