"""Validate the evidence-linked MATH6186 report manuscript."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "Abstract",
    "1. Introduction",
    "2. Literature Review",
    "3. Deterministic Worried-Well Model",
    "4. Stochastic Consultation Demand",
    "5. Newsvendor Formulation",
    "6. Experimental Design",
    "7. Results",
    "8. Discussion",
    "9. Conclusion",
    "References",
    "Appendix A. Reproducibility",
]
REQUIRED_FIGURES = [
    "figure_1_compartments.png",
    "figure_2_risk_ratio.png",
    "figure_3_demand_uncertainty.png",
    "figure_4_optimal_capacity.png",
    "figure_5_sensitivity.png",
]
PERMITTED_IDENTITY_TOKENS = {"[[STUDENT_NAME]]", "[[STUDENT_ID]]"}
PERMITTED_EQUATIONS = {
    "compartment_system",
    "expected_demand",
    "sample_average_cost",
    "critical_fractile",
}
ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "report" / "MATH6186_case_study_draft.md"
REFERENCE_PATH = ROOT / "report" / "references.json"
SUMMARY_PATH = ROOT / "outputs" / "data" / "summary.csv"

FIGURE_PATTERN = re.compile(
    r"\[\[FIGURE:([^|\]]+)\|([^|\]]+)\|(fig[1-5])\]\]"
)
VALUE_PATTERN = re.compile(
    r"\[\[VALUE:([^|\]]+)\|([^|\]]+)\|([^|\]]+)\]\]"
)
EQUATION_PATTERN = re.compile(r"\[\[EQUATION:([a-z_]+)\]\]")
CITATION_PATTERN = re.compile(r"\[@([a-z0-9_]+)\]")
REFERENCE_PATTERN = re.compile(r"\[\[REFERENCE:([a-z0-9_]+)\]\]")
DOUBLE_BRACKET_PATTERN = re.compile(r"\[\[[^\[\]\r\n]+\]\]")
WORD_PATTERN = re.compile(r"\b[\w]+(?:[’'-][\w]+)*\b", re.UNICODE)


def fail(message: str) -> None:
    raise ValueError(message)


def read_required_text(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing report draft: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        fail(f"Empty report draft: {path.relative_to(ROOT)}")
    return text


def load_references() -> set[str]:
    with REFERENCE_PATH.open(encoding="utf-8") as stream:
        references = json.load(stream)
    if not isinstance(references, list):
        fail("references.json must contain a JSON array.")
    ids = {
        reference.get("id")
        for reference in references
        if isinstance(reference, dict) and isinstance(reference.get("id"), str)
    }
    if len(ids) != 6:
        fail(f"references.json must define six unique reference IDs, found {len(ids)}.")
    return ids


def load_summary() -> tuple[list[str], list[dict[str, str]]]:
    with SUMMARY_PATH.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            fail("summary.csv has no header.")
        rows = list(reader)
    if not rows:
        fail("summary.csv has no data rows.")
    return reader.fieldnames, rows


def heading_positions(text: str) -> dict[str, int]:
    positions: dict[str, int] = {}
    previous_position = -1
    for heading in REQUIRED_HEADINGS:
        matches = list(
            re.finditer(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE)
        )
        if len(matches) != 1:
            fail(f"Heading must appear exactly once: {heading}")
        position = matches[0].start()
        if position <= previous_position:
            fail(f"Required heading is out of order: {heading}")
        positions[heading] = position
        previous_position = position
    return positions


def validate_figures(text: str) -> None:
    matches = list(FIGURE_PATTERN.finditer(text))
    filenames = [match.group(1) for match in matches]
    bookmarks = [match.group(3) for match in matches]
    for figure in REQUIRED_FIGURES:
        if filenames.count(figure) != 1:
            fail(f"Figure marker must appear exactly once: {figure}")
    if len(matches) != len(REQUIRED_FIGURES):
        fail("Only the five required figure markers are permitted.")
    if len(set(bookmarks)) != 5 or set(bookmarks) != {
        "fig1",
        "fig2",
        "fig3",
        "fig4",
        "fig5",
    }:
        fail("Figure markers must use unique fig1-fig5 bookmarks.")
    expected_pairs = list(zip(REQUIRED_FIGURES, [f"fig{i}" for i in range(1, 6)]))
    actual_pairs = [(match.group(1), match.group(3)) for match in matches]
    if actual_pairs != expected_pairs:
        fail("Figure markers must appear in order and use the corresponding bookmark.")


def validate_fixed_markers(text: str) -> None:
    for marker in ("[[PARAMETER_TABLE]]", "[[POLICY_TABLE]]"):
        if text.count(marker) != 1:
            fail(f"Marker must appear exactly once: {marker}")
    for token in PERMITTED_IDENTITY_TOKENS:
        if text.count(token) != 1:
            fail(f"Identity token must appear exactly once: {token}")


def validate_citations_and_references(text: str, reference_ids: set[str]) -> None:
    citation_ids = CITATION_PATTERN.findall(text)
    unknown_citations = set(citation_ids) - reference_ids
    if unknown_citations:
        fail("Unknown citation keys: " + ", ".join(sorted(unknown_citations)))
    missing_citations = reference_ids - set(citation_ids)
    if missing_citations:
        fail("Uncited reference IDs: " + ", ".join(sorted(missing_citations)))
    reference_markers = REFERENCE_PATTERN.findall(text)
    if len(reference_markers) != len(reference_ids) or set(reference_markers) != reference_ids:
        fail("References must contain one [[REFERENCE:<id>]] marker per citation key.")


def validate_values(
    text: str,
    summary_columns: list[str],
    summary_rows: list[dict[str, str]],
) -> None:
    for scenario, column, output_format in VALUE_PATTERN.findall(text):
        rows = [row for row in summary_rows if row.get("scenario") == scenario]
        if len(rows) != 1:
            fail(
                f"VALUE marker scenario must resolve to exactly one summary row: {scenario}"
            )
        if column not in summary_columns or column in {"scenario", "group"}:
            fail(f"VALUE marker column is not a numeric summary column: {column}")
        try:
            value = float(rows[0][column])
        except (TypeError, ValueError) as error:
            fail(f"VALUE marker does not resolve to a numeric value: {scenario}|{column}")
            raise AssertionError("unreachable") from error
        try:
            format(value, output_format)
        except (ValueError, TypeError) as error:
            fail(
                "VALUE marker uses an invalid numeric format: "
                f"{scenario}|{column}|{output_format}"
            )
            raise AssertionError("unreachable") from error


def validate_equations(text: str) -> None:
    equation_ids = EQUATION_PATTERN.findall(text)
    if set(equation_ids) != PERMITTED_EQUATIONS or len(equation_ids) != 4:
        fail(
            "Equation markers must contain each permitted equation ID exactly once."
        )


def validate_marker_grammar(text: str) -> None:
    recognized = set(PERMITTED_IDENTITY_TOKENS)
    recognized.update(match.group(0) for match in FIGURE_PATTERN.finditer(text))
    recognized.update(match.group(0) for match in VALUE_PATTERN.finditer(text))
    recognized.update(match.group(0) for match in EQUATION_PATTERN.finditer(text))
    recognized.update(match.group(0) for match in REFERENCE_PATTERN.finditer(text))
    recognized.update({"[[PARAMETER_TABLE]]", "[[POLICY_TABLE]]"})
    unresolved = [
        marker
        for marker in DOUBLE_BRACKET_PATTERN.findall(text)
        if marker not in recognized
    ]
    if unresolved:
        fail("Unresolved square-bracket markers: " + ", ".join(sorted(set(unresolved))))


def validate_language(text: str) -> None:
    prohibited = {
        r"\bforecasts?\b": "forecast",
        r"\bpredictions?\b": "prediction",
        r"\bobserved demand\b": "observed demand",
        r"\bpatient data\b": "patient data",
        r"\bclinically calibrated results\b": "clinically calibrated results",
    }
    for pattern, label in prohibited.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"Prohibited output characterization found: {label}")


def count_main_text_words(text: str, positions: dict[str, int]) -> int:
    start = positions["Abstract"]
    end = positions["References"]
    main_text = text[start:end]
    main_text = re.sub(r"^#{1,6}\s+.*$", "", main_text, flags=re.MULTILINE)
    main_text = FIGURE_PATTERN.sub("", main_text)
    main_text = VALUE_PATTERN.sub("value", main_text)
    main_text = EQUATION_PATTERN.sub("", main_text)
    main_text = CITATION_PATTERN.sub("", main_text)
    main_text = main_text.replace("[[PARAMETER_TABLE]]", "")
    main_text = main_text.replace("[[POLICY_TABLE]]", "")
    return len(WORD_PATTERN.findall(main_text))


def main() -> None:
    text = read_required_text(REPORT_PATH)
    reference_ids = load_references()
    summary_columns, summary_rows = load_summary()
    positions = heading_positions(text)
    validate_figures(text)
    validate_fixed_markers(text)
    validate_citations_and_references(text, reference_ids)
    validate_values(text, summary_columns, summary_rows)
    validate_equations(text)
    validate_marker_grammar(text)
    validate_language(text)
    word_count = count_main_text_words(text, positions)
    if not 4_500 <= word_count <= 5_500:
        fail(
            "Main-text word count must be 4,500-5,500 after exclusions; "
            f"found {word_count}."
        )
    print(
        "Report draft validation passed: "
        f"{word_count} main-text words, {len(reference_ids)} references, "
        f"{len(REQUIRED_FIGURES)} figures."
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as error:
        print(f"Report draft validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
