import argparse
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
from collections import Counter
from typing import Dict, List, Optional, Tuple

import bs4
import requests

SEEDS = [
    {"idx": 1, "label": "MemGuard-Alpha", "arxiv": "2603.26797"},
    {"idx": 2, "label": "Profit Mirage", "arxiv": "2510.07920"},
    {"idx": 3, "label": "Dated Data", "arxiv": "2403.12958"},
    {"idx": 4, "label": "Set the Clock", "arxiv": "2402.16797"},
    {
        "idx": 5,
        "label": "Chronologically Consistent Large Language Models",
        "arxiv": "2502.21206",
    },
    {"idx": 6, "label": "DatedGPT", "arxiv": "2603.11838"},
    {
        "idx": 7,
        "label": "Quantifying Memorization Across Neural Language Models",
        "arxiv": "2202.07646",
    },
    {
        "idx": 8,
        "label": "Deduplicating Training Data Mitigates Privacy Risks",
        "arxiv": "2202.06539",
    },
    {"idx": 9, "label": "Entity-level Memorization in LLMs", "arxiv": "2308.15727"},
    {
        "idx": 10,
        "label": "Assessing Look-Ahead Bias via GPT Sentiment",
        "arxiv": "2309.17322",
    },
]

PRIMARY_FIELDS = ",".join(
    [
        "title",
        "year",
        "references.title",
        "references.year",
        "references.externalIds",
        "references.abstract",
        "references.venue",
        "references.citationCount",
        "references.authors",
    ]
)


def normalize_title(title: str) -> str:
    text = (title or "").lower().replace("&", "and")
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def prefix40(title: str) -> str:
    return normalize_title(title)[:40]


def load_titles(index_path: pathlib.Path, note_paths: List[pathlib.Path], broad_sweep_path: pathlib.Path):
    index_text = index_path.read_text(encoding="utf-8")
    library_titles = re.findall(r"\[(.+?)\]\(", index_text)

    note_titles: List[str] = []
    for path in note_paths:
        text = path.read_text(encoding="utf-8")
        note_titles.extend(re.findall(r"^##\s+(.+)$", text, flags=re.MULTILINE))
        note_titles.extend(re.findall(r"^- \*\*(.+?)\*\*", text, flags=re.MULTILINE))

    broad_text = broad_sweep_path.read_text(encoding="utf-8")
    broad_titles = sorted(set(re.findall(r"\[(.+?)\]\(", broad_text)))

    return library_titles, note_titles, broad_titles


def match_against_pool(title: str, pool: List[Tuple[str, str, str]]) -> Tuple[Optional[str], Optional[str]]:
    normalized = normalize_title(title)
    pref = normalized[:40]

    for original, normalized_other, pref_other in pool:
        if not normalized or not normalized_other:
            continue
        if normalized == normalized_other:
            return original, "exact"
        if pref and pref_other and (pref == pref_other or pref.startswith(pref_other) or pref_other.startswith(pref)):
            return original, "prefix40"

    for original, normalized_other, _ in pool:
        if not normalized or not normalized_other:
            continue
        short = min(len(normalized), len(normalized_other), 40)
        if short >= 20 and (normalized[:short] in normalized_other or normalized_other[:short] in normalized):
            return original, "substring"

    return None, None


def classify_match(match_type: Optional[str]) -> str:
    if match_type in {"exact", "prefix40"}:
        return "match"
    if match_type == "substring":
        return "possible"
    return "none"


def fetch_json(url: str, sleep_seconds: float) -> Dict:
    last_error = None
    for attempt in range(5):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; FinMemBenchSubtaskD/1.0)"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            wait = max(sleep_seconds, 1.0) * (attempt + 1)
            time.sleep(wait)
    raise RuntimeError(f"request failed after retries for {url}: {last_error}")


def fetch_seed(seed: Dict[str, str], sleep_seconds: float) -> Tuple[Dict, str, Optional[str]]:
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{seed['arxiv']}"
        f"?fields={PRIMARY_FIELDS}"
    )
    try:
        data = fetch_json(url, sleep_seconds)
        if data.get("references") is not None:
            return data, url, None
        fallback_reason = "arXiv lookup returned no references"
    except Exception as exc:  # noqa: BLE001
        fallback_reason = str(exc)

    search_url = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={urllib.parse.quote(seed['label'])}"
        f"&limit=5&fields=title,year,externalIds,references.title,references.year,"
        "references.externalIds,references.abstract,references.venue,"
        "references.citationCount,references.authors"
    )
    search_data = fetch_json(search_url, sleep_seconds)
    for candidate in search_data.get("data", []):
        external_ids = candidate.get("externalIds") or {}
        if external_ids.get("ArXiv") == seed["arxiv"]:
            return candidate, search_url, fallback_reason
    if search_data.get("data"):
        return search_data["data"][0], search_url, fallback_reason
    raise RuntimeError(f"failed to resolve seed {seed['label']} ({seed['arxiv']})")


def split_authors(authors_text: str) -> List[str]:
    text = authors_text.replace(" and ", ", ")
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if len(parts) <= 2:
        return parts
    authors: List[str] = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts):
            authors.append(f"{parts[i]} {parts[i + 1]}")
            i += 2
        else:
            authors.append(parts[i])
            i += 1
    return authors


def parse_arxiv_html_reference(item: bs4.element.Tag) -> Dict:
    bibblock = item.select_one(".ltx_bibblock")
    text = " ".join(bibblock.stripped_strings) if bibblock else " ".join(item.stripped_strings)
    text = re.sub(r"\s+", " ", text).strip()

    venue = None
    if bibblock:
        italic = bibblock.select_one(".ltx_text.ltx_font_italic")
        if italic:
            venue = italic.get_text(" ", strip=True)

    year = None
    authors = []
    title = text
    match = re.search(r",\s*((?:19|20)\d{2})\s*,\s*", text)
    if match:
        year = int(match.group(1))
        authors = split_authors(text[: match.start()].strip(" ,.;"))
        remainder = text[match.end() :].strip()
        if venue and venue in remainder:
            title = remainder.split(venue, 1)[0].rstrip(" ,.;")
        else:
            title = remainder.rstrip(" ,.;")

    title = re.sub(r"\s+", " ", title).strip(" ,.;")
    return {
        "title": title,
        "year": year,
        "venue": venue,
        "citationCount": None,
        "externalIds": {},
        "authors": authors,
        "abstract": None,
    }


def fetch_seed_via_arxiv_html(seed: Dict[str, str]) -> Tuple[Dict, str]:
    url = f"https://arxiv.org/html/{seed['arxiv']}"
    response = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "Mozilla/5.0 (compatible; FinMemBenchSubtaskD/1.0)"},
    )
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    bibliography = soup.select("li.ltx_bibitem")
    if not bibliography:
        raise RuntimeError(f"no arXiv HTML bibliography found for {seed['arxiv']}")

    title_tag = soup.find("title")
    resolved_title = title_tag.get_text(" ", strip=True) if title_tag else seed["label"]
    references = []
    for item in bibliography:
        parsed = parse_arxiv_html_reference(item)
        if parsed["title"]:
            references.append(parsed)

    return {
        "title": resolved_title,
        "year": None,
        "references": references,
        "_fallback_source": "arxiv_html",
    }, url


def author_names(authors: List[Dict]) -> List[str]:
    return [author.get("name") for author in authors or [] if author.get("name")]


def build_output(root: pathlib.Path, output_path: pathlib.Path, sleep_seconds: float) -> None:
    index_path = root / "related papers" / "INDEX.md"
    note_paths = [
        root / "related papers" / "notes" / "memorization_extraction.md",
        root / "related papers" / "notes" / "temporal_lookahead.md",
        root / "related papers" / "notes" / "contamination_detection.md",
        root / "related papers" / "notes" / "financial_nlp.md",
    ]
    broad_sweep_path = root / "refine-logs" / "reviews" / "LIT_SWEEP_B_BROAD_SWEEP.md"

    library_titles, note_titles, broad_titles = load_titles(index_path, note_paths, broad_sweep_path)
    library_pool = [(title, normalize_title(title), prefix40(title)) for title in library_titles + note_titles]
    broad_pool = [(title, normalize_title(title), prefix40(title)) for title in broad_titles]

    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seeds": [],
        "all_references": [],
        "summary": {},
        "library_titles": library_titles,
        "note_titles": note_titles,
        "broad_sweep_titles": broad_titles,
    }

    all_references: Dict[str, Dict] = {}
    failures: List[Dict[str, str]] = []

    for index, seed in enumerate(SEEDS):
        if index:
            time.sleep(sleep_seconds)

        try:
            paper, source_url, fallback_reason = fetch_seed(seed, sleep_seconds)
        except Exception as exc:  # noqa: BLE001
            try:
                paper, source_url = fetch_seed_via_arxiv_html(seed)
                fallback_reason = f"Semantic Scholar failed; used arXiv HTML fallback: {exc}"
            except Exception as html_exc:  # noqa: BLE001
                failures.append(
                    {
                        "seed": seed["label"],
                        "arxiv": seed["arxiv"],
                        "error": str(exc),
                        "arxiv_html_error": str(html_exc),
                    }
                )
                continue

        references = []
        for reference in paper.get("references", []) or []:
            title = (reference.get("title") or "").strip()
            if not title:
                continue

            library_match, library_match_type = match_against_pool(title, library_pool)
            broad_match, broad_match_type = match_against_pool(title, broad_pool)
            library_status = classify_match(library_match_type)
            broad_status = classify_match(broad_match_type)

            reference_record = {
                "title": title,
                "year": reference.get("year"),
                "venue": reference.get("venue"),
                "citationCount": reference.get("citationCount"),
                "externalIds": reference.get("externalIds") or {},
                "authors": author_names(reference.get("authors") or [])
                if reference.get("authors") and isinstance(reference.get("authors")[0], dict)
                else reference.get("authors") or [],
                "abstract": reference.get("abstract"),
                "library_status": library_status,
                "library_match": library_match,
                "library_match_type": library_match_type,
                "broad_sweep_status": broad_status,
                "broad_sweep_match": broad_match,
                "broad_sweep_match_type": broad_match_type,
            }
            references.append(reference_record)

            key = normalize_title(title)
            aggregate = all_references.setdefault(
                key,
                {
                    "title": title,
                    "normalized_title": key,
                    "year": reference.get("year"),
                    "venue": reference.get("venue"),
                    "citationCount": reference.get("citationCount"),
                    "externalIds": reference.get("externalIds") or {},
                    "authors": author_names(reference.get("authors") or [])
                    if reference.get("authors") and isinstance(reference.get("authors")[0], dict)
                    else reference.get("authors") or [],
                    "abstract": reference.get("abstract"),
                    "library_status": library_status,
                    "library_match": library_match,
                    "library_match_type": library_match_type,
                    "broad_sweep_status": broad_status,
                    "broad_sweep_match": broad_match,
                    "broad_sweep_match_type": broad_match_type,
                    "seed_ids": [],
                    "seed_labels": [],
                },
            )

            if aggregate["library_status"] == "none" and library_status != "none":
                aggregate["library_status"] = library_status
                aggregate["library_match"] = library_match
                aggregate["library_match_type"] = library_match_type
            if aggregate["library_status"] == "possible" and library_status == "match":
                aggregate["library_status"] = library_status
                aggregate["library_match"] = library_match
                aggregate["library_match_type"] = library_match_type

            if aggregate["broad_sweep_status"] == "none" and broad_status != "none":
                aggregate["broad_sweep_status"] = broad_status
                aggregate["broad_sweep_match"] = broad_match
                aggregate["broad_sweep_match_type"] = broad_match_type
            if aggregate["broad_sweep_status"] == "possible" and broad_status == "match":
                aggregate["broad_sweep_status"] = broad_status
                aggregate["broad_sweep_match"] = broad_match
                aggregate["broad_sweep_match_type"] = broad_match_type

            if seed["idx"] not in aggregate["seed_ids"]:
                aggregate["seed_ids"].append(seed["idx"])
                aggregate["seed_labels"].append(seed["label"])

        output["seeds"].append(
            {
                "seed": seed,
                "resolved_title": paper.get("title"),
                "resolved_year": paper.get("year"),
                "source_url": source_url,
                "fallback_reason": fallback_reason,
                "source_type": paper.get("_fallback_source", "semantic_scholar"),
                "reference_count": len(references),
                "references": references,
            }
        )

    for record in all_references.values():
        record["seed_count"] = len(record["seed_ids"])

    sorted_references = sorted(
        all_references.values(),
        key=lambda item: (
            -item["seed_count"],
            -(item["citationCount"] or -1),
            item["title"].lower(),
        ),
    )

    summary = Counter()
    for record in sorted_references:
        if record["library_status"] == "match":
            summary["in_library"] += 1
        elif record["library_status"] == "possible":
            summary["possibly_in_library"] += 1
        elif record["broad_sweep_status"] == "match":
            summary["already_in_broad_sweep"] += 1
        elif record["broad_sweep_status"] == "possible":
            summary["possibly_in_broad_sweep"] += 1
        else:
            summary["new_vs_library_and_b"] += 1

        if record["seed_count"] >= 3:
            summary["seed_count_3_plus"] += 1
        elif record["seed_count"] == 2:
            summary["seed_count_2"] += 1
        else:
            summary["seed_count_1"] += 1

    output["all_references"] = sorted_references
    output["summary"] = dict(summary)
    output["failures"] = failures

    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:\\GitRepos\\LLM-Leakage-Test")
    parser.add_argument(
        "--output",
        default="D:\\GitRepos\\LLM-Leakage-Test\\refine-logs\\reviews\\_tmp_subtask_d_analysis.json",
    )
    parser.add_argument("--sleep-seconds", type=float, default=1.15)
    args = parser.parse_args()

    build_output(
        root=pathlib.Path(args.root),
        output_path=pathlib.Path(args.output),
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    main()
