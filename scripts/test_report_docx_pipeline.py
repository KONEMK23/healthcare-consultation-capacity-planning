"""Focused regression tests for the MATH6186 Markdown-to-DOCX contract."""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree

import scripts.build_report_docx as builder
import scripts.validate_report_draft as draft_validator
import scripts.validate_report_docx as validator


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "report" / "MATH6186_case_study_draft.md"
DOCX = ROOT / "report" / "MATH6186_case_study_draft.docx"
NS = validator.NS


def rewrite_docx(
    destination: Path,
    *,
    xml_mutator=None,
    media_mutator=None,
) -> None:
    with zipfile.ZipFile(DOCX, "r") as source_archive:
        payloads = {
            name: source_archive.read(name) for name in source_archive.namelist()
        }
    if xml_mutator is not None:
        root = etree.fromstring(payloads["word/document.xml"])
        xml_mutator(root)
        payloads["word/document.xml"] = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone=True
        )
    if media_mutator is not None:
        media_mutator(payloads)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in payloads.items():
            archive.writestr(name, payload)


class BuilderContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.references = builder.load_references(builder.REFERENCE_PATH)
        self.summary = builder.load_summary(builder.SUMMARY_PATH)
        self.source_text = SOURCE.read_text(encoding="utf-8")

    def build_mutation(self, mutated_text: str) -> None:
        with tempfile.TemporaryDirectory(prefix="report_source_mutation_") as directory:
            source = Path(directory) / "mutated.md"
            output = Path(directory) / "mutated.docx"
            source.write_text(mutated_text, encoding="utf-8")
            builder.build_report(source, output)

    def test_canonical_reference_set_includes_stochastic_and_surge_sources(self) -> None:
        self.assertEqual(
            set(self.references),
            {
                "allen_2017",
                "asmundson_taylor_2020",
                "blyuss_kyrychko_2005",
                "chatterjee_2020",
                "hick_2004",
                "qin_2011",
                "singh_gromov_2025",
                "singh_rebennack_2026",
            },
        )

    def test_reference_validation_accepts_a_report_that_ends_after_references(self) -> None:
        without_appendix = self.source_text.split(
            "\n## Appendix A. Reproducibility", 1
        )[0].rstrip() + "\n"
        try:
            draft_validator.validate_citations_and_references(
                without_appendix, set(self.references)
            )
        except ValueError as error:
            self.fail(str(error))

    def test_rejects_indented_nested_bullet(self) -> None:
        mutated = self.source_text.replace(
            "## Abstract\n", "## Abstract\n\n  - nested bullet\n", 1
        )
        with self.assertRaises(ValueError):
            self.build_mutation(mutated)

    def test_rejects_unsupported_blockquote(self) -> None:
        mutated = self.source_text.replace(
            "## Abstract\n", "## Abstract\n\n> unsupported blockquote\n", 1
        )
        with self.assertRaises(ValueError):
            self.build_mutation(mutated)

    def test_rejects_unmatched_double_bracket(self) -> None:
        mutated = self.source_text.replace(
            "## Abstract\n", "## Abstract\n\nUnmatched [[BROKEN marker.\n", 1
        )
        with self.assertRaises(ValueError):
            self.build_mutation(mutated)

    def test_rejects_unknown_complete_marker(self) -> None:
        mutated = self.source_text.replace(
            "## Abstract\n", "## Abstract\n\nUnknown [[UNKNOWN:value]] marker.\n", 1
        )
        with self.assertRaises(ValueError):
            self.build_mutation(mutated)

    def test_build_rejects_extra_well_formed_value_marker(self) -> None:
        marker = "[[VALUE:cost_cu_10_co_1|relative_cost_reduction_pct|.2f]]"
        mutated = self.source_text.replace(
            "## Abstract\n", f"## Abstract\n\nDuplicate value {marker}.\n", 1
        )
        with self.assertRaises(ValueError):
            self.build_mutation(mutated)

    def test_inline_code_delimiters_are_not_emitted(self) -> None:
        pieces = builder.resolve_inline_markup(
            "Use `python scripts/run_analysis.py` to regenerate.", self.references
        )
        self.assertEqual(
            "".join(text for text, _, _ in pieces),
            "Use python scripts/run_analysis.py to regenerate.",
        )

    def test_tex_subscript_grouping_is_not_emitted(self) -> None:
        cases = (
            (r"\(\beta_{WP}=0.70\)", "beta_WP=0.70"),
            (r"\(D_{ts}\)", "D_ts"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                pieces = builder.resolve_inline_markup(source, self.references)
                self.assertEqual(
                    "".join(text for text, _, _ in pieces),
                    expected,
                )

    def test_rejects_unsupported_tex_grouping(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported inline math"):
            builder.resolve_inline_markup(r"\(x_{a+b}\)", self.references)

    def test_rejects_noncanonical_value_marker(self) -> None:
        with self.assertRaises(ValueError):
            builder.resolve_value_marker(
                "[[VALUE:cost_cu_5_co_1|peak_infected|.8f]]", self.summary
            )

    def test_rejects_nonfinite_value(self) -> None:
        mutated = {key: dict(value) for key, value in self.summary.items()}
        mutated["cost_cu_10_co_1"]["relative_cost_reduction_pct"] = "nan"
        with self.assertRaises(ValueError):
            builder.resolve_value_marker(
                "[[VALUE:cost_cu_10_co_1|relative_cost_reduction_pct|.2f]]",
                mutated,
            )

    def test_rejects_noncanonical_figure_marker(self) -> None:
        with self.assertRaises(ValueError):
            builder.parse_figure_marker(
                "[[FIGURE:arbitrary.png|Arbitrary replacement.|fig1]]"
            )


class DocxMutationTests(unittest.TestCase):
    def assert_mutation_rejected(self, *, xml_mutator=None, media_mutator=None) -> None:
        with tempfile.TemporaryDirectory(prefix="report_docx_mutation_") as directory:
            mutated = Path(directory) / "mutated.docx"
            rewrite_docx(
                mutated, xml_mutator=xml_mutator, media_mutator=media_mutator
            )
            original = validator.DOCX_PATH
            validator.DOCX_PATH = mutated
            try:
                with self.assertRaises(ValueError):
                    validator.main()
            finally:
                validator.DOCX_PATH = original

    def test_rejects_decorative_cover_rule(self) -> None:
        def mutate(root):
            title = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='Title']][1]", namespaces=NS
            )[0]
            properties = title.find("w:pPr", NS)
            borders = etree.SubElement(properties, qname("pBdr"))
            bottom = etree.SubElement(borders, qname("bottom"))
            bottom.set(qname("val"), "single")
            bottom.set(qname("sz"), "8")

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_missing_explicit_even_page_setting(self) -> None:
        def mutate(payloads):
            root = etree.fromstring(payloads["word/settings.xml"])
            setting = root.find(".//w:evenAndOddHeaders", NS)
            self.assertIsNotNone(setting)
            setting.getparent().remove(setting)
            payloads["word/settings.xml"] = etree.tostring(
                root, xml_declaration=True, encoding="UTF-8", standalone=True
            )

        self.assert_mutation_rejected(media_mutator=mutate)

    def test_rejects_ordinary_body_text_substitution(self) -> None:
        def mutate(root):
            nodes = root.xpath(
                ".//w:t[contains(text(), 'Healthcare consultation systems face')]",
                namespaces=NS,
            )
            self.assertEqual(len(nodes), 1)
            nodes[0].text = "Substituted ordinary paragraph."

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_cover_metadata_substitution(self) -> None:
        def mutate(root):
            paragraph = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='CoverMetadata']][1]",
                namespaces=NS,
            )[0]
            nodes = paragraph.xpath(".//w:t", namespaces=NS)
            nodes[-1].text = "Substituted identity"

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_reference_substitution(self) -> None:
        def mutate(root):
            paragraphs = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='NarrativeBullet']]",
                namespaces=NS,
            )
            reference = next(
                paragraph
                for paragraph in paragraphs
                if "Mathematically modeling worried-well behavior"
                in "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))
            )
            reference.xpath(".//w:t", namespaces=NS)[0].text = "Substituted reference"

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_resolved_value_substitution(self) -> None:
        def mutate(root):
            nodes = root.xpath(
                ".//w:t[contains(text(), 'infected fraction peaks at 0.545')]",
                namespaces=NS,
            )
            self.assertEqual(len(nodes), 1)
            nodes[0].text = (nodes[0].text or "").replace("0.545", "9.999", 1)

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_canonical_caption_substitution(self) -> None:
        def mutate(root):
            captions = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='Caption']]",
                namespaces=NS,
            )
            nodes = captions[0].xpath(".//w:t", namespaces=NS)
            nodes[-1].text = ". Substituted caption."

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_expected_image_substitution(self) -> None:
        def mutate(payloads):
            payloads["word/media/image1.png"] = payloads["word/media/image2.png"]

        self.assert_mutation_rejected(media_mutator=mutate)

    def test_rejects_table_content_substitution(self) -> None:
        def mutate(root):
            nodes = root.xpath(
                ".//w:tbl[1]//w:t[text()='Parameter']", namespaces=NS
            )
            self.assertEqual(len(nodes), 1)
            nodes[0].text = "Substituted"

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_duplicate_bookmark_pair(self) -> None:
        def mutate(root):
            body = root.find(".//w:body", NS)
            paragraph = etree.Element(qname("p"))
            start = etree.SubElement(paragraph, qname("bookmarkStart"))
            start.set(qname("id"), "999")
            start.set(qname("name"), "fig1")
            end = etree.SubElement(paragraph, qname("bookmarkEnd"))
            end.set(qname("id"), "999")
            body.insert(0, paragraph)

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_mismatched_bookmark_end_id(self) -> None:
        def mutate(root):
            caption = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='Caption']][1]", namespaces=NS
            )[0]
            end = caption.find("w:bookmarkEnd", NS)
            end.set(qname("id"), "999")

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_malformed_seq_field_order(self) -> None:
        def mutate(root):
            caption = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='Caption']][1]", namespaces=NS
            )[0]
            fields = caption.xpath(".//w:fldChar", namespaces=NS)
            fields[1].set(qname("fldCharType"), "end")
            fields[2].set(qname("fldCharType"), "separate")

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_malformed_page_field_order(self) -> None:
        def mutate(payloads):
            footer_name = next(
                name
                for name, payload in payloads.items()
                if name.startswith("word/footer")
                and b"PAGE" in payload
            )
            root = etree.fromstring(payloads[footer_name])
            fields = root.xpath(".//w:fldChar", namespaces=NS)
            fields[1].set(qname("fldCharType"), "end")
            fields[2].set(qname("fldCharType"), "separate")
            payloads[footer_name] = etree.tostring(
                root, xml_declaration=True, encoding="UTF-8", standalone=True
            )

        self.assert_mutation_rejected(media_mutator=mutate)

    def test_rejects_wrong_page_field_cached_display(self) -> None:
        def mutate(payloads):
            footer_name = next(
                name
                for name, payload in payloads.items()
                if name.startswith("word/footer")
                and b"PAGE" in payload
            )
            root = etree.fromstring(payloads[footer_name])
            fields = root.xpath(".//w:fldChar", namespaces=NS)
            nodes = list(root.iter())
            positions = {id(node): index for index, node in enumerate(nodes)}
            separate = positions[id(fields[1])]
            end = positions[id(fields[2])]
            result = next(
                node
                for node in root.xpath(".//w:t", namespaces=NS)
                if separate < positions[id(node)] < end
            )
            result.text = "9"
            payloads[footer_name] = etree.tostring(
                root, xml_declaration=True, encoding="UTF-8", standalone=True
            )

        self.assert_mutation_rejected(media_mutator=mutate)

    def test_rejects_wrong_header_relationship_type(self) -> None:
        def mutate(root):
            reference = root.find(
                ".//w:sectPr/w:headerReference[@w:type='default']", NS
            )
            reference.set(qname("type"), "even")

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_equation_without_actual_line_breaks(self) -> None:
        def mutate(root):
            equation = root.xpath(
                ".//w:p[w:pPr/w:pStyle[@w:val='Equation']][1]", namespaces=NS
            )[0]
            for line_break in equation.xpath(".//w:br", namespaces=NS):
                line_break.getparent().remove(line_break)

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_table_indent_with_non_dxa_type(self) -> None:
        def mutate(root):
            indent = root.find(".//w:tbl[1]/w:tblPr/w:tblInd", NS)
            indent.set(qname("type"), "pct")

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_wrong_table_cell_margin(self) -> None:
        def mutate(root):
            margin = root.find(".//w:tbl[1]//w:tcPr/w:tcMar/w:start", NS)
            margin.set(qname("w"), "999")

        self.assert_mutation_rejected(xml_mutator=mutate)

    def test_rejects_missing_repeated_table_header(self) -> None:
        def mutate(root):
            header = root.find(".//w:tbl[1]/w:tr[1]/w:trPr/w:tblHeader", NS)
            header.getparent().remove(header)

        self.assert_mutation_rejected(xml_mutator=mutate)


def qname(local_name: str) -> str:
    return f"{{{NS['w']}}}{local_name}"


if __name__ == "__main__":
    unittest.main(verbosity=2)
