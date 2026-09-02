"""Validate the report's bibliographic and generated-evidence contract."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


EXPECTED_REFERENCE_IDS = {"allen_2017", "asmundson_taylor_2020", "blyuss_kyrychko_2005", "chatterjee_2020", "hick_2004", "qin_2011", "singh_gromov_2025", "singh_rebennack_2026"}
EXPECTED_CSVS = {"daily_metrics.csv", "parameters.csv", "summary.csv", "trajectories.csv"}
EXPECTED_FIGURES = {"figure_1_compartments.png", "figure_2_risk_ratio.png", "figure_3_demand_uncertainty.png", "figure_4_optimal_capacity.png", "figure_5_sensitivity.png"}
REFERENCE_FIELDS = {"id", "authors", "year", "title", "journal", "volume", "issue", "pages_or_article", "doi", "url", "role", "limitation"}
ASSUMPTION_FIELDS = {"alpha", "beta_p", "beta_w", "beta_wp", "gamma_p", "gamma_w", "delta_p", "initial_susceptible", "initial_infected", "initial_worried", "initial_recovered", "population", "p_infected", "p_worried", "cv", "underage", "overage", "model_structure_provenance", "behaviour_provenance", "rate_parameter_provenance", "initial_condition_provenance", "service_demand_provenance", "uncertainty_provenance", "cost_provenance"}
ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    raise ValueError(message)


def require_nonempty_file(path: Path) -> None:
    if not path.is_file():
        fail(f"Missing evidence file: {path.relative_to(ROOT)}")
    if path.stat().st_size == 0:
        fail(f"Empty evidence file: {path.relative_to(ROOT)}")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    require_nonempty_file(path)
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            fail(f"Evidence CSV has no header: {path.relative_to(ROOT)}")
        rows = list(reader)
    if not rows:
        fail(f"Evidence CSV has no data rows: {path.relative_to(ROOT)}")
    return reader.fieldnames, rows


def validate_references(path: Path) -> int:
    require_nonempty_file(path)
    with path.open(encoding="utf-8") as stream:
        references = json.load(stream)
    if not isinstance(references, list):
        fail("references.json must contain a JSON array.")
    ids: list[str] = []
    for reference in references:
        if not isinstance(reference, dict):
            fail("Each reference must be a JSON object.")
        missing = REFERENCE_FIELDS - reference.keys()
        if missing:
            fail(f"Reference is missing fields: {', '.join(sorted(missing))}")
        if not isinstance(reference["id"], str) or not reference["id"]:
            fail("Reference ID must be a non-empty string.")
        if not isinstance(reference["authors"], list) or not reference["authors"]:
            fail(f"Reference {reference['id']} must contain ordered authors.")
        if any(not isinstance(author, str) or not author for author in reference["authors"]):
            fail(f"Reference {reference['id']} has an invalid author.")
        for field in REFERENCE_FIELDS - {"authors", "year", "issue"}:
            if not isinstance(reference[field], str) or not reference[field]:
                fail(f"Reference {reference['id']} has an empty {field} field.")
        if not isinstance(reference["year"], int):
            fail(f"Reference {reference['id']} has an invalid year.")
        ids.append(reference["id"])
    if len(ids) != len(set(ids)):
        fail("Duplicate reference IDs found.")
    if set(ids) != EXPECTED_REFERENCE_IDS:
        fail("Reference IDs do not match the eight canonical references.")
    for reference in references:
        if (
            not reference["doi"].startswith("10.")
            or reference["url"] != f"https://doi.org/{reference['doi']}"
        ):
            fail(f"Reference {reference['id']} does not use its DOI URL.")
    return len(references)


def validate_evidence_files() -> None:
    for name in EXPECTED_CSVS:
        read_csv(ROOT / "outputs" / "data" / name)
    for name in EXPECTED_FIGURES:
        require_nonempty_file(ROOT / "outputs" / "figures" / name)


def validate_evidence_map(path: Path) -> int:
    _, rows = read_csv(path)
    if len(rows) != 12:
        fail(f"evidence-map.csv must contain 12 evidence claims, found {len(rows)}.")
    assumptions_rows = [row for row in rows if row["report_section"] == "3-4"]
    if len(assumptions_rows) != 1:
        fail("evidence-map.csv must contain exactly one 3-4 assumptions row.")
    assumptions = {value.strip() for value in assumptions_rows[0]["required_columns"].split(";") if value.strip()}
    missing_assumptions = ASSUMPTION_FIELDS - assumptions
    if missing_assumptions:
        fail("Assumptions row omits provenance fields: " + ", ".join(sorted(missing_assumptions)))
    for row in rows:
        evidence_file = ROOT / row["evidence_file"]
        require_nonempty_file(evidence_file)
        if evidence_file.suffix == ".csv":
            headers, _ = read_csv(evidence_file)
            required = {value.strip() for value in row["required_columns"].split(";") if value.strip()}
            unresolved = required - set(headers)
            if unresolved:
                fail(f"Unresolvable columns for {row['evidence_file']}: " + ", ".join(sorted(unresolved)))
    return len(rows)


def validate_chart_map(path: Path) -> None:
    require_nonempty_file(path)
    notes = path.read_text(encoding="utf-8")
    start = notes.find("## Chart map")
    if start == -1:
        fail("report-source-notes.md is missing the Chart map heading.")
    end = notes.find("## ", start + len("## Chart map"))
    chart_map = notes[start:] if end == -1 else notes[start:end]
    for figure in EXPECTED_FIGURES:
        if not any(f"| `{figure}` |" in line for line in chart_map.splitlines()):
            fail(f"Chart map is missing a record for {figure}.")


def main() -> None:
    reference_count = validate_references(ROOT / "report" / "references.json")
    validate_evidence_files()
    claim_count = validate_evidence_map(ROOT / "report" / "evidence-map.csv")
    validate_chart_map(ROOT / "report" / "report-source-notes.md")
    print(f"Report source validation passed: {reference_count} references, {claim_count} evidence claims, {len(EXPECTED_FIGURES)} figures.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as error:
        print(f"Report source validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
