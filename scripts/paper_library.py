from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

from PyPDF2 import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT
RELATED_DIR = PROJECT_ROOT / "related papers"
NOTES_DIR = RELATED_DIR / "notes"
CATALOG_PATH = NOTES_DIR / "_paper_catalog.json"


@dataclass
class PaperRecord:
    filename: str
    sha256: str
    pages: int
    title_guess: str
    authors_guess: str
    year_guess: str
    abstract: str
    introduction_excerpt: str
    first_page_excerpt: str
    category_suggestion: str


CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "Financial NLP & Sentiment Analysis",
        (
            "financial",
            "finance",
            "stock",
            "earnings",
            "investment",
            "sentiment",
            "forecast",
            "analyst",
            "trading",
            "macro",
            "profit",
            "return predict",
        ),
    ),
    (
        "Knowledge Editing & Localization",
        (
            "knowledge editing",
            "editing factual",
            "mass-editing",
            "localization",
            "mquake",
            "rome",
            "memit",
            "unlearning",
            "knowledge neurons",
            "propagation pitfalls",
        ),
    ),
    (
        "Benchmark Contamination & Leakage Detection",
        (
            "contamination",
            "benchmark",
            "leakage",
            "lookahead",
            "look-ahead",
            "dated",
            "time travel",
            "decontamination",
            "pretraining data",
            "membership inference",
            "min-k",
            "mimir",
            "livebench",
            "sanitize",
            "reciting",
        ),
    ),
    (
        "Memorization & Training Data Extraction",
        (
            "memorization",
            "memorise",
            "memorized",
            "training data",
            "training corpus",
            "extracting",
            "extraction",
            "secret sharer",
            "membership inference",
            "pretraining data",
            "canary",
        ),
    ),
    (
        "Factual Grounding & Hallucination",
        (
            "ground",
            "grounding",
            "hallucination",
            "fact-check",
            "faithful",
            "faithfulness",
            "knowledge conflict",
            "context",
            "retrieval",
            "rag",
            "verification",
        ),
    ),
    (
        "Prompting & Reasoning Techniques",
        (
            "prompting",
            "prompt",
            "chain-of-thought",
            "chain-of-note",
            "chain-of-verification",
            "least-to-most",
            "reasoning",
            "rationalizing",
            "feature extraction",
            "re-imagine",
        ),
    ),
    (
        "Mechanistic Interpretability",
        (
            "mechanistic",
            "circuits",
            "ffn",
            "key-value",
            "entity cells",
            "entity identification",
            "space and time",
            "time encoded",
            "knowledge neurons",
            "factual associations",
            "internals",
            "attribution",
            "traces",
        ),
    ),
    (
        "Other",
        (
            "causal",
            "invariant",
            "anchor regression",
            "calibration",
            "entropy",
            "shapley",
            "probability estimation",
            "stable prediction",
        ),
    ),
]


HEADING_PATTERNS = [
    r"\n\s*abstract\s*\n",
    r"\n\s*abstract[:.]\s*",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\u00a0", " ")
    text = text.replace("\r", "\n")
    text = text.replace("-\n", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_match_text(text: str) -> str:
    text = text.lower().replace("_", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokens_for_match(text: str) -> set[str]:
    return {token for token in normalize_match_text(text).split() if len(token) > 1}


def pretty_title_from_filename(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").strip()


def extract_text_pages(pdf_path: Path, max_pages: int = 5) -> tuple[list[str], int]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages[:max_pages]:
        try:
            pages.append(normalize_text(page.extract_text() or ""))
        except Exception:
            pages.append("")
    return pages, len(reader.pages)


def looks_like_title_line(line: str) -> bool:
    lower = line.lower()
    if not line or len(line) < 6 or len(line) > 220:
        return False
    if "@" in line or line.startswith("http") or line.startswith("arXiv"):
        return False
    if lower in {"abstract", "introduction"}:
        return False
    if re.fullmatch(r"[\d\W_]+", line):
        return False
    if any(token in lower for token in ("university", "department", "institute", "school", "conference", "journal")):
        return False
    letters = sum(ch.isalpha() for ch in line)
    return letters >= max(6, len(line) // 3)


def guess_title(first_page: str, metadata_title: str | None, filename: str) -> str:
    if metadata_title:
        cleaned = normalize_text(metadata_title)
        if cleaned and cleaned.lower() not in {filename.lower(), filename[:-4].lower()} and len(cleaned) > 8:
            return cleaned

    lines = [line.strip() for line in first_page.splitlines() if line.strip()]
    candidates: list[str] = []
    for line in lines[:12]:
        if re.search(r"\babstract\b", line, re.IGNORECASE):
            break
        if looks_like_title_line(line):
            candidates.append(line)
        elif candidates:
            break

    if candidates:
        title = " ".join(candidates[:3])
        title = re.sub(r"\s+", " ", title).strip(" -")
        if len(title) > 8:
            return title

    return filename[:-4]


def guess_authors(first_page: str, title: str) -> str:
    lines = [line.strip() for line in first_page.splitlines() if line.strip()]
    if not lines:
        return "Unknown"

    joined_title = title.replace(" ", "").lower()
    try:
        start_index = next(
            index
            for index, line in enumerate(lines[:12])
            if line.replace(" ", "").lower() in joined_title or joined_title in line.replace(" ", "").lower()
        )
    except StopIteration:
        start_index = 0

    author_lines: list[str] = []
    for line in lines[start_index + 1 : start_index + 7]:
        lower = line.lower()
        if re.search(r"\babstract\b", lower):
            break
        if any(token in lower for token in ("university", "institute", "department", "school", "email", "@", "arxiv", "conference")):
            if author_lines:
                break
            continue
        if re.search(r"\b(introduction|keywords|ccs concepts)\b", lower):
            break
        if len(line) > 120:
            continue
        author_lines.append(line)
        if "," in line and len(author_lines) >= 2:
            break

    authors = " ".join(author_lines).strip()
    authors = re.sub(r"\s+", " ", authors)
    return authors or "Unknown"


def guess_year(text: str, filename: str) -> str:
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", text[:1800])
    filtered = [year for year in years if 1990 <= int(year) <= 2030]
    if filtered:
        return max(filtered)
    filename_year = re.search(r"\b(19\d{2}|20\d{2})\b", filename)
    return filename_year.group(1) if filename_year else "Unknown"


def extract_block(text: str, start_patterns: Iterable[str], end_patterns: Iterable[str], limit: int = 4000) -> str:
    lower = text.lower()
    start_index = -1
    for pattern in start_patterns:
        match = re.search(pattern, lower, re.IGNORECASE)
        if match:
            start_index = match.end()
            break
    if start_index == -1:
        return ""

    end_index = min(len(text), start_index + limit)
    for pattern in end_patterns:
        match = re.search(pattern, lower[start_index:end_index], re.IGNORECASE)
        if match:
            end_index = start_index + match.start()
            break

    block = text[start_index:end_index]
    block = normalize_text(block)
    return block[:1800].strip()


def extract_abstract(text: str) -> str:
    abstract = extract_block(
        text,
        HEADING_PATTERNS,
        (
            r"\n\s*\d+\.?\s+introduction\b",
            r"\n\s*introduction\b",
            r"\n\s*keywords\b",
            r"\n\s*ccs concepts\b",
            r"\n\s*1\s+background\b",
        ),
    )
    if abstract:
        return abstract

    # Fallback: take the first dense paragraph after "abstract".
    match = re.search(r"abstract[:.\s]*", text, re.IGNORECASE)
    if match:
        tail = normalize_text(text[match.end() : match.end() + 1800])
        return tail
    return ""


def extract_introduction_excerpt(text: str) -> str:
    intro = extract_block(
        text,
        (
            r"\n\s*\d+\.?\s+introduction\b",
            r"\n\s*introduction\b",
        ),
        (
            r"\n\s*\d+\.?\s+[A-Z][^\n]{0,80}\n",
            r"\n\s*related work\b",
            r"\n\s*background\b",
            r"\n\s*method\b",
        ),
        limit=5000,
    )
    return intro[:2200].strip()


def suggest_category(title: str, abstract: str, filename: str) -> str:
    text = " ".join((title, abstract, filename)).lower()
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_RULES:
        scores[category] = sum(1 for keyword in keywords if keyword in text)
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else "Other"


def parse_markdown_table_rows(path: Path) -> list[list[str]]:
    if not path.exists():
        return []

    rows: list[list[str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if set(line.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def load_metadata_overrides() -> dict[str, dict[str, str]]:
    overrides: dict[str, dict[str, str]] = {}

    # Exact filename matches from the repo-level paper index.
    paper_index_rows = parse_markdown_table_rows(PROJECT_ROOT / "PAPER_INDEX.md")
    for cells in paper_index_rows:
        if len(cells) < 4 or not cells[0].endswith(".pdf"):
            continue
        filename, authors, year = cells[0], cells[1], cells[2]
        overrides[filename] = {
            "title": pretty_title_from_filename(filename),
            "authors": authors if authors not in {"—", "-", ""} else "Unknown",
            "year": year if year not in {"—", "-", ""} else "Unknown",
        }

    # Fuzzy title matches from the pre-existing related papers index.
    related_index_rows = parse_markdown_table_rows(RELATED_DIR / "INDEX.md")
    local_rows: list[dict[str, str]] = []
    for cells in related_index_rows:
        if len(cells) < 7:
            continue
        if not re.match(r"^[A-Z]\d+$", cells[0]):
            continue
        status = cells[6]
        if "Local" not in status:
            continue
        local_rows.append(
            {
                "title": cells[1],
                "authors": cells[2] if cells[2] not in {"—", "-", ""} else "Unknown",
                "year": cells[3] if cells[3] not in {"—", "-", ""} else "Unknown",
            }
        )

    unmatched_filenames = [
        pdf_path.name
        for pdf_path in RELATED_DIR.glob("*.pdf")
        if pdf_path.name not in overrides
    ]

    used_titles: set[str] = set()
    for filename in unmatched_filenames:
        filename_tokens = tokens_for_match(filename)
        filename_norm = normalize_match_text(pretty_title_from_filename(filename))
        best_score = 0.0
        best_row: dict[str, str] | None = None

        for row in local_rows:
            if row["title"] in used_titles:
                continue
            title_norm = normalize_match_text(row["title"])
            title_tokens = tokens_for_match(row["title"])
            overlap = len(filename_tokens & title_tokens)
            coverage = overlap / max(1, len(filename_tokens))
            recall = overlap / max(1, len(title_tokens))
            seq = SequenceMatcher(None, filename_norm, title_norm).ratio()
            score = max(seq, 0.55 * coverage + 0.45 * recall)
            if score > best_score:
                best_score = score
                best_row = row

        if best_row and best_score >= 0.62:
            overrides[filename] = {
                "title": best_row["title"],
                "authors": best_row["authors"],
                "year": best_row["year"],
            }
            used_titles.add(best_row["title"])

    return overrides


def move_root_pdfs() -> dict[str, list[dict[str, str]]]:
    RELATED_DIR.mkdir(exist_ok=True)
    NOTES_DIR.mkdir(exist_ok=True)

    existing_hashes: dict[str, str] = {}
    for pdf_path in RELATED_DIR.glob("*.pdf"):
        existing_hashes[sha256(pdf_path)] = pdf_path.name

    moved: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    seen_root_hashes: set[str] = set()

    for pdf_path in sorted(PROJECT_ROOT.glob("*.pdf")):
        digest = sha256(pdf_path)
        if digest in existing_hashes:
            skipped.append(
                {
                    "filename": pdf_path.name,
                    "reason": "duplicate_of_related_papers",
                    "matched_file": existing_hashes[digest],
                }
            )
            continue
        if digest in seen_root_hashes:
            skipped.append(
                {
                    "filename": pdf_path.name,
                    "reason": "duplicate_in_project_root",
                    "matched_file": "",
                }
            )
            continue

        destination = RELATED_DIR / pdf_path.name
        if destination.exists():
            skipped.append(
                {
                    "filename": pdf_path.name,
                    "reason": "name_collision",
                    "matched_file": destination.name,
                }
            )
            continue

        shutil.move(str(pdf_path), str(destination))
        existing_hashes[digest] = destination.name
        seen_root_hashes.add(digest)
        moved.append({"filename": destination.name})

    return {"moved": moved, "skipped": skipped}


def build_catalog() -> list[PaperRecord]:
    overrides = load_metadata_overrides()
    records: list[PaperRecord] = []
    for pdf_path in sorted(RELATED_DIR.glob("*.pdf")):
        pages, page_count = extract_text_pages(pdf_path)
        first_page = pages[0] if pages else ""
        merged_text = "\n\n".join(pages)

        reader = PdfReader(str(pdf_path))
        metadata_title = ""
        try:
            metadata = reader.metadata or {}
            metadata_title = getattr(metadata, "title", "") or metadata.get("/Title", "") or ""
        except Exception:
            metadata_title = ""

        title = guess_title(first_page, metadata_title, pdf_path.name)
        authors = guess_authors(first_page, title)
        abstract = extract_abstract(merged_text)
        introduction_excerpt = extract_introduction_excerpt(merged_text)
        year = guess_year(merged_text or first_page, pdf_path.name)
        first_page_excerpt = normalize_text(first_page)[:1600]
        category = suggest_category(title, abstract or introduction_excerpt, pdf_path.name)

        override = overrides.get(pdf_path.name)
        if override:
            title = override.get("title") or title
            authors = override.get("authors") or authors
            year = override.get("year") or year
        else:
            if len(title) > 180 or title.count(",") > 6:
                title = pretty_title_from_filename(pdf_path.name)

        records.append(
            PaperRecord(
                filename=pdf_path.name,
                sha256=sha256(pdf_path),
                pages=page_count,
                title_guess=title,
                authors_guess=authors,
                year_guess=year,
                abstract=abstract,
                introduction_excerpt=introduction_excerpt,
                first_page_excerpt=first_page_excerpt,
                category_suggestion=category,
            )
        )

    return records


def main() -> None:
    move_report = move_root_pdfs()
    records = build_catalog()
    NOTES_DIR.mkdir(exist_ok=True)
    payload = {
        "move_report": move_report,
        "paper_count": len(records),
        "papers": [asdict(record) for record in records],
    }
    CATALOG_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Moved: {len(move_report['moved'])}")
    print(f"Skipped: {len(move_report['skipped'])}")
    print(f"Cataloged: {len(records)}")
    print(CATALOG_PATH)


if __name__ == "__main__":
    main()
