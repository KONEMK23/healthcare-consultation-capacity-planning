"""Structurally validate the generated MATH6186 Word report."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from docx import Document
from lxml import etree


EXPECTED_SECTION_TITLES = [
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
EXPECTED_MEDIA_COUNT = 5
EXPECTED_TABLE_COUNT = 2
EXPECTED_CAPTIONS = 5
EXPECTED_EQUATIONS = [
    (
        "dS/dt = -(beta_P + beta_WP)SI_P - beta_W SI_W + delta_P R_P + gamma_W I_W\n"
        "dI_P/dt = beta_P SI_P + alpha beta_P I_P I_W - gamma_P I_P\n"
        "dI_W/dt = -alpha beta_P I_P I_W + beta_W SI_W + beta_WP SI_P - gamma_W I_W\n"
        "dR_P/dt = gamma_P I_P - delta_P R_P"
    ),
    "m_t = N[p_P I_P(t) + p_W I_W(t)]",
    "min_q (1/n) sum_j [c_u(D_j-q)^+ + c_o(q-D_j)^+]",
    "tau = c_u/(c_u+c_o), q* = F_n^{-1}(tau)",
]
EXPECTED_STYLES = {
    "Normal": {
        "font": "Calibri",
        "size": "22",
        "color": None,
        "before": "0",
        "after": "160",
        "line": "320",
        "line_rule": "auto",
        "alignment": "both",
    },
    "Heading 1": {
        "font": "Calibri",
        "size": "32",
        "color": "2E74B5",
        "before": "360",
        "after": "200",
        "line": None,
        "line_rule": None,
        "alignment": None,
    },
    "Heading 2": {
        "font": "Calibri",
        "size": "26",
        "color": "2E74B5",
        "before": "240",
        "after": "120",
        "line": None,
        "line_rule": None,
        "alignment": None,
    },
    "Heading 3": {
        "font": "Calibri",
        "size": "24",
        "color": "1F4D78",
        "before": "160",
        "after": "80",
        "line": None,
        "line_rule": None,
        "alignment": None,
    },
    "Caption": {
        "font": "Calibri",
        "size": "18",
        "color": "595959",
        "before": "80",
        "after": "120",
        "line": "240",
        "line_rule": "auto",
        "alignment": "center",
    },
}
STYLE_IDS = {
    "Normal": "Normal",
    "Heading 1": "Heading1",
    "Heading 2": "Heading2",
    "Heading 3": "Heading3",
    "Caption": "Caption",
}
ROOT = Path(__file__).resolve().parent.parent
DOCX_PATH = ROOT / "report" / "MATH6186_case_study_draft.docx"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
IDENTITY_TOKEN = re.compile(r"\[\[[^\[\]\r\n]+\]\]")
PERMITTED_IDENTITY_TOKENS = {"[[STUDENT_NAME]]", "[[STUDENT_ID]]"}
PROHIBITED_MARKERS = (
    "[[VALUE:",
    "[[FIGURE:",
    "[[EQUATION:",
    "[[REFERENCE:",
    "[[PARAMETER_TABLE]]",
    "[[POLICY_TABLE]]",
)


def fail(message: str) -> None:
    raise ValueError(message)


def require_attribute(
    element: etree._Element | None, attribute: str, expected: str, label: str
) -> None:
    if element is None:
        fail(f"{label} is missing.")
    actual = element.get(f"{{{NS['w']}}}{attribute}")
    if actual != expected:
        fail(f"{label} must be {expected}, found {actual!r}.")


def xml_part(archive: zipfile.ZipFile, name: str) -> etree._Element:
    try:
        payload = archive.read(name)
    except KeyError as error:
        fail(f"DOCX is missing required part: {name}")
        raise AssertionError("unreachable") from error
    return etree.fromstring(payload)


def validate_sections(document_xml: etree._Element) -> None:
    headings = [
        "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))
        for paragraph in document_xml.xpath(
            ".//w:body/w:p[w:pPr/w:pStyle[@w:val='Heading1']]",
            namespaces=NS,
        )
    ]
    if headings != EXPECTED_SECTION_TITLES:
        fail(
            "Heading 1 section sequence does not match the required report sections: "
            f"{headings!r}"
        )


def validate_page_geometry(document_xml: etree._Element) -> None:
    section_properties = document_xml.xpath(".//w:sectPr", namespaces=NS)
    if not section_properties:
        fail("DOCX has no section properties.")
    for index, section in enumerate(section_properties, start=1):
        page_size = section.find("w:pgSz", NS)
        require_attribute(page_size, "w", "12240", f"Section {index} page width")
        require_attribute(page_size, "h", "15840", f"Section {index} page height")
        page_margin = section.find("w:pgMar", NS)
        for edge in ("top", "right", "bottom", "left"):
            require_attribute(
                page_margin, edge, "1440", f"Section {index} {edge} margin"
            )
        require_attribute(
            page_margin, "header", "708", f"Section {index} header distance"
        )
        require_attribute(
            page_margin, "footer", "708", f"Section {index} footer distance"
        )


def validate_styles(styles_xml: etree._Element) -> None:
    for style_name, expected in EXPECTED_STYLES.items():
        matches = styles_xml.xpath(
            ".//w:style[@w:styleId=$style_id]",
            namespaces=NS,
            style_id=STYLE_IDS[style_name],
        )
        if len(matches) != 1:
            fail(f"Expected exactly one {style_name!r} style, found {len(matches)}.")
        style = matches[0]
        run_properties = style.find("w:rPr", NS)
        if run_properties is None:
            fail(f"{style_name} style has no explicit run properties.")
        fonts = run_properties.find("w:rFonts", NS)
        require_attribute(fonts, "ascii", expected["font"], f"{style_name} font")
        require_attribute(fonts, "hAnsi", expected["font"], f"{style_name} font")
        require_attribute(run_properties.find("w:sz", NS), "val", expected["size"], f"{style_name} size")
        color = run_properties.find("w:color", NS)
        if expected["color"] is None:
            if color is not None and color.get(f"{{{NS['w']}}}val") not in (None, "000000", "auto"):
                fail(f"{style_name} color must be black/default.")
        else:
            require_attribute(color, "val", expected["color"], f"{style_name} color")
        paragraph_properties = style.find("w:pPr", NS)
        if paragraph_properties is None:
            fail(f"{style_name} style has no explicit paragraph properties.")
        spacing = paragraph_properties.find("w:spacing", NS)
        require_attribute(spacing, "before", expected["before"], f"{style_name} before spacing")
        require_attribute(spacing, "after", expected["after"], f"{style_name} after spacing")
        if expected["line"] is not None:
            require_attribute(spacing, "line", expected["line"], f"{style_name} line spacing")
            require_attribute(
                spacing,
                "lineRule",
                expected["line_rule"],
                f"{style_name} line-spacing rule",
            )
        if expected["alignment"] is not None:
            require_attribute(
                paragraph_properties.find("w:jc", NS),
                "val",
                expected["alignment"],
                f"{style_name} alignment",
            )


def validate_tables(document_xml: etree._Element) -> None:
    tables = document_xml.xpath(".//w:body/w:tbl", namespaces=NS)
    if len(tables) != EXPECTED_TABLE_COUNT:
        fail(f"Expected {EXPECTED_TABLE_COUNT} tables, found {len(tables)}.")
    for index, table in enumerate(tables, start=1):
        properties = table.find("w:tblPr", NS)
        if properties is None:
            fail(f"Table {index} has no table properties.")
        width = properties.find("w:tblW", NS)
        require_attribute(width, "type", "dxa", f"Table {index} width type")
        require_attribute(width, "w", "9360", f"Table {index} width")
        require_attribute(
            properties.find("w:tblInd", NS), "w", "120", f"Table {index} indent"
        )
        require_attribute(
            properties.find("w:tblLayout", NS),
            "type",
            "fixed",
            f"Table {index} layout",
        )
        grid_widths = [
            int(column.get(f"{{{NS['w']}}}w"))
            for column in table.xpath("./w:tblGrid/w:gridCol", namespaces=NS)
        ]
        if not grid_widths or sum(grid_widths) != 9360:
            fail(f"Table {index} grid widths must sum to 9360 DXA: {grid_widths!r}")
        for row_number, row in enumerate(table.xpath("./w:tr", namespaces=NS), start=1):
            cells = row.xpath("./w:tc", namespaces=NS)
            if len(cells) != len(grid_widths):
                fail(
                    f"Table {index} row {row_number} has {len(cells)} cells "
                    f"for {len(grid_widths)} grid columns."
                )
            cell_widths: list[int] = []
            for cell in cells:
                tc_width = cell.find("w:tcPr/w:tcW", NS)
                require_attribute(
                    tc_width,
                    "type",
                    "dxa",
                    f"Table {index} row {row_number} cell width type",
                )
                cell_widths.append(int(tc_width.get(f"{{{NS['w']}}}w")))
            if cell_widths != grid_widths:
                fail(
                    f"Table {index} row {row_number} cell widths {cell_widths!r} "
                    f"do not match grid {grid_widths!r}."
                )
            if row.find("w:trPr/w:trHeight", NS) is not None:
                fail(f"Table {index} row {row_number} must not use a fixed height.")


def validate_figures(
    archive: zipfile.ZipFile, document_xml: etree._Element
) -> None:
    media = [
        name
        for name in archive.namelist()
        if name.startswith("word/media/") and not name.endswith("/")
    ]
    if len(media) != EXPECTED_MEDIA_COUNT:
        fail(f"Expected {EXPECTED_MEDIA_COUNT} media files, found {len(media)}.")
    inline = document_xml.xpath(".//wp:inline", namespaces=NS)
    anchored = document_xml.xpath(".//wp:anchor", namespaces=NS)
    if len(inline) != EXPECTED_MEDIA_COUNT:
        fail(f"Expected {EXPECTED_MEDIA_COUNT} inline drawings, found {len(inline)}.")
    if anchored:
        fail(f"Anchored drawings are prohibited; found {len(anchored)}.")
    for index, drawing in enumerate(inline, start=1):
        extent = drawing.find("wp:extent", NS)
        if extent is None:
            fail(f"Figure {index} has no drawing extent.")
        width_emu = int(extent.get("cx", "0"))
        if width_emu <= 0 or width_emu > int(6.35 * 914400):
            fail(f"Figure {index} width is outside (0, 6.35] inches.")


def validate_captions_and_bookmarks(document_xml: etree._Element) -> None:
    captions = document_xml.xpath(
        ".//w:body/w:p[w:pPr/w:pStyle[@w:val='Caption']]",
        namespaces=NS,
    )
    if len(captions) != EXPECTED_CAPTIONS:
        fail(f"Expected {EXPECTED_CAPTIONS} captions, found {len(captions)}.")
    bookmark_names = {
        element.get(f"{{{NS['w']}}}name")
        for element in document_xml.xpath(".//w:bookmarkStart", namespaces=NS)
    }
    expected_bookmarks = {f"fig{index}" for index in range(1, 6)}
    if bookmark_names & expected_bookmarks != expected_bookmarks:
        fail(
            "Figure bookmarks must contain fig1-fig5; found "
            f"{sorted(name for name in bookmark_names if name)}."
        )
    for index, caption in enumerate(captions, start=1):
        text = "".join(caption.xpath(".//w:t/text()", namespaces=NS))
        if text != f"Figure {index}. {text.partition('. ')[2]}":
            fail(f"Caption {index} does not contain cached display text 'Figure {index}.'.")
        instructions = [
            value.strip()
            for value in caption.xpath(".//w:instrText/text()", namespaces=NS)
        ]
        if not any(instruction == "SEQ Figure" for instruction in instructions):
            fail(f"Caption {index} is missing a SEQ Figure field.")
        starts = caption.xpath(
            f".//w:bookmarkStart[@w:name='fig{index}']", namespaces=NS
        )
        ends = caption.xpath(".//w:bookmarkEnd", namespaces=NS)
        if len(starts) != 1 or not ends:
            fail(f"Caption {index} does not contain its fig{index} bookmark.")


def validate_equations(document_xml: etree._Element) -> None:
    equation_paragraphs = document_xml.xpath(
        ".//w:body/w:p[w:pPr/w:pStyle[@w:val='Equation']]",
        namespaces=NS,
    )
    equations = [
        "\n".join(
            "".join(run.xpath(".//w:t/text()", namespaces=NS))
            for run in paragraph.xpath("./w:r", namespaces=NS)
            if run.xpath(".//w:t", namespaces=NS)
        )
        for paragraph in equation_paragraphs
    ]
    equations = [re.sub(r"\n+", "\n", equation).strip() for equation in equations]
    if equations != EXPECTED_EQUATIONS:
        fail(f"Expected the four implemented equations exactly, found {equations!r}.")
    for index, paragraph in enumerate(equation_paragraphs, start=1):
        require_attribute(
            paragraph.find("w:pPr/w:jc", NS),
            "val",
            "center",
            f"Equation {index} alignment",
        )
        fonts = paragraph.xpath(".//w:rPr/w:rFonts", namespaces=NS)
        if not fonts:
            fail(f"Equation {index} has no explicit run font.")
        for font in fonts:
            if font.get(f"{{{NS['w']}}}ascii") != "Cambria Math":
                fail(f"Equation {index} must use Cambria Math.")


def validate_markers(document_xml: etree._Element) -> None:
    text = "\n".join(document_xml.xpath(".//w:t/text()", namespaces=NS))
    for marker in PROHIBITED_MARKERS:
        if marker in text:
            fail(f"Unresolved marker remains in DOCX: {marker}")
    tokens = IDENTITY_TOKEN.findall(text)
    if set(tokens) != PERMITTED_IDENTITY_TOKENS or len(tokens) != 2:
        fail(
            "The only remaining double-bracket tokens must be exactly "
            "[[STUDENT_NAME]] and [[STUDENT_ID]]."
        )


def validate_page_furniture(
    archive: zipfile.ZipFile, document_xml: etree._Element
) -> None:
    section = document_xml.find(".//w:body/w:sectPr", NS)
    if section is None or section.find("w:titlePg", NS) is None:
        fail("The section must use a different first page to suppress cover furniture.")
    header_parts = [
        name
        for name in archive.namelist()
        if re.fullmatch(r"word/header\d+\.xml", name)
    ]
    footer_parts = [
        name
        for name in archive.namelist()
        if re.fullmatch(r"word/footer\d+\.xml", name)
    ]
    if len(header_parts) != 2 or len(footer_parts) != 2:
        fail("Expected separate default and first-page header/footer parts.")
    header_texts = [
        "".join(xml_part(archive, name).xpath(".//w:t/text()", namespaces=NS))
        for name in header_parts
    ]
    expected_header = "MATH6186 | Worried-Well Consultation Capacity"
    if header_texts.count(expected_header) != 1 or header_texts.count("") != 1:
        fail("Expected one running header and one blank first-page header.")
    default_footer_found = False
    blank_footer_found = False
    for name in footer_parts:
        footer = xml_part(archive, name)
        text = "".join(footer.xpath(".//w:t/text()", namespaces=NS))
        instructions = [
            value.strip() for value in footer.xpath(".//w:instrText/text()", namespaces=NS)
        ]
        if text == "" and not instructions:
            blank_footer_found = True
        if "PAGE" in instructions:
            paragraphs = footer.xpath(".//w:p", namespaces=NS)
            if len(paragraphs) != 1:
                fail("The page-number footer must contain exactly one paragraph.")
            require_attribute(
                paragraphs[0].find("w:pPr/w:jc", NS),
                "val",
                "right",
                "Page-number footer alignment",
            )
            default_footer_found = True
    if not default_footer_found or not blank_footer_found:
        fail("Expected one right-aligned PAGE footer and one blank first-page footer.")


def main() -> None:
    if not DOCX_PATH.is_file():
        fail(f"Missing DOCX: {DOCX_PATH.relative_to(ROOT)}")
    if DOCX_PATH.stat().st_size == 0:
        fail(f"Empty DOCX: {DOCX_PATH.relative_to(ROOT)}")
    Document(DOCX_PATH)
    with zipfile.ZipFile(DOCX_PATH) as archive:
        document_xml = xml_part(archive, "word/document.xml")
        styles_xml = xml_part(archive, "word/styles.xml")
        validate_sections(document_xml)
        validate_page_geometry(document_xml)
        validate_styles(styles_xml)
        validate_tables(document_xml)
        validate_figures(archive, document_xml)
        validate_captions_and_bookmarks(document_xml)
        validate_equations(document_xml)
        validate_markers(document_xml)
        validate_page_furniture(archive, document_xml)
    print(
        "Report DOCX validation passed: "
        f"{len(EXPECTED_SECTION_TITLES)} sections, {EXPECTED_TABLE_COUNT} tables, "
        f"{EXPECTED_MEDIA_COUNT} inline figures, {EXPECTED_CAPTIONS} captions, "
        f"{len(EXPECTED_EQUATIONS)} equations."
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile, etree.XMLSyntaxError) as error:
        print(f"Report DOCX validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
