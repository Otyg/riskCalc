#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

EXCLUDE_KEYS = {
    "__samples",
    "alternatives",
    "factor",
    "calculation",
    "weight",
    "factor_sum",
    "factor_mul",
    "factor_range",
    "factor_mean",
    "factor_mean_75",
    "ale",
    # Exclude these qualitative fields
    "likelihood_initiation_or_occurence",
    "likelihood_adverse_impact",
}

# ------------------------------------------------------------
# Data cleaning / filtering
# ------------------------------------------------------------


def sanitize(obj: Any) -> Any:
    """Recursively remove excluded keys anywhere in dict/list."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k in EXCLUDE_KEYS:
                continue
            sv = sanitize(v)
            if sv == {} or sv == []:
                continue
            cleaned[k] = sv
        return cleaned
    if isinstance(obj, list):
        cleaned_list = []
        for item in obj:
            si = sanitize(item)
            if si == {} or si == []:
                continue
            cleaned_list.append(si)
        return cleaned_list
    return obj


# ------------------------------------------------------------
# Common formatting
# ------------------------------------------------------------


def fmt_number(value: Any) -> str:
    """Format numbers with 2 decimals. Keeps other types as string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return str(value)


# ------------------------------------------------------------
# Markdown helpers
# ------------------------------------------------------------


def md_escape(text: Any) -> str:
    return str(text).replace("\n", " ").strip()


def md_heading(level: int, text: str) -> str:
    return f"{'#' * level} {text}\n"


def md_kv_table(rows: List[Tuple[str, Any]]) -> str:
    out = []
    out.append("| Fält | Värde |")
    out.append("|---|---|")
    for k, v in rows:
        out.append(f"| {md_escape(k)} | {md_escape(fmt_number(v))} |")
    return "\n".join(out) + "\n"


def md_metric_table(metrics: List[Tuple[str, Dict[str, Any]]]) -> str:
    cols = ["min", "probable", "max", "p90"]
    present = [
        c for c in cols if any(isinstance(m[1], dict) and c in m[1] for m in metrics)
    ]

    headers = ["Mått"] + present
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for name, stats in metrics:
        row = [md_escape(name)]
        for c in present:
            row.append(md_escape(fmt_number(stats.get(c, ""))))
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------
# Report generator (Markdown) – mirrors PDF layout
# ------------------------------------------------------------


def generate_markdown_report(data: Dict[str, Any], source_name: str = "") -> str:
    data = sanitize(data)

    analysis_object = str(data.get("analysis_object", "")).strip()
    title = f"Riskrapport för {analysis_object}" if analysis_object else "Riskrapport"

    lines: List[str] = []

    # --- Cover (matches PDF) ---
    lines.append(md_heading(1, title))

    if source_name:
        lines.append(f"_Källa: {md_escape(source_name)}_\n")

    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"_Genererad: {generated}_\n")

    meta_rows = []
    for k in ["analysis_object", "version", "date", "scope", "owner"]:
        if k in data:
            meta_rows.append((k, data[k]))
    if meta_rows:
        lines.append(md_heading(2, "Metadata"))
        lines.append(md_kv_table(meta_rows))

    # Summary on cover (matches PDF)
    if "summary" in data and isinstance(data["summary"], dict) and data["summary"]:
        lines.append(md_heading(2, "Sammanfattning"))
        lines.append(md_kv_table(list(data["summary"].items())))

    # Cover -> content break
    lines.append("\n\\newpage\n")
    lines.append("\n---\n")

    # --- Content ---
    scenarios = data.get("scenarios", [])
    if isinstance(scenarios, list) and scenarios:
        lines.append(md_heading(2, f"Scenarier ({len(scenarios)})"))

        for i, sc in enumerate(scenarios, start=1):
            # Force a new page before each scenario so the title stays with the tables (Pandoc)
            lines.append("\n\\newpage\n")

            name = sc.get("name", f"Scenario {i}")

            # Scenario title (kept together by starting on a new page)
            lines.append(md_heading(3, f"{i}. {name}"))

            # Overview
            overview_rows = []
            for k in [
                "category",
                "actor",
                "asset",
                "threat",
                "vulnerability_desc",
                "description",
            ]:
                v = sc.get(k, None)
                if v not in ("", None):
                    overview_rows.append((k, v))
            if overview_rows:
                lines.append(md_heading(4, "Översikt"))
                lines.append(md_kv_table(overview_rows))

            # Risk
            risk = sc.get("risk", {})
            if isinstance(risk, dict):
                qualitative = risk.get("qualitative", {})
                quantitative = risk.get("quantitative", {})

                if isinstance(qualitative, dict) and qualitative:
                    q_rows = []
                    for k in ["overall_likelihood", "impact", "overall_risk"]:
                        if k in qualitative:
                            q_rows.append((k, qualitative[k]))
                    if q_rows:
                        lines.append(md_heading(4, "Kvalitativ risk"))
                        lines.append(md_kv_table(q_rows))

                if isinstance(quantitative, dict) and quantitative:
                    lines.append(md_heading(4, "Kvantitativ risk"))

                    qmeta = []
                    for k in ["currency", "budget"]:
                        if k in quantitative:
                            qmeta.append((k, quantitative[k]))
                    if qmeta:
                        lines.append(md_kv_table(qmeta))

                    metrics: List[Tuple[str, Dict[str, Any]]] = []
                    for k, v in quantitative.items():
                        if isinstance(v, dict) and any(
                            x in v for x in ("min", "probable", "max", "p90")
                        ):
                            metrics.append((k, v))
                    if metrics:
                        lines.append(md_metric_table(metrics))

            # Questionnaires: merged, no headings tef/vuln/lm
            qn = sc.get("questionaires", {})
            if isinstance(qn, dict) and qn:
                lines.append(md_heading(4, "Frågebatterier"))

                qa_rows: List[Tuple[str, str]] = []
                for _battery_name, qobj in qn.items():
                    if not isinstance(qobj, dict):
                        continue
                    questions = qobj.get("questions", [])
                    if not isinstance(questions, list):
                        continue
                    for q in questions:
                        q_text = q.get("text", "")
                        ans = q.get("answer", {})
                        ans_text = ans.get("text", "") if isinstance(ans, dict) else ""
                        qa_rows.append((q_text, ans_text if ans_text else "(saknas)"))

                if qa_rows:
                    lines.append("| Fråga | Svar |")
                    lines.append("|---|---|")
                    for q_text, ans_text in qa_rows:
                        lines.append(f"| {md_escape(q_text)} | {md_escape(ans_text)} |")
                    lines.append("")
                else:
                    lines.append("- Inga frågor hittades.\n")

            lines.append("\n---\n")

    return "\n".join(lines).strip() + "\n"


# ------------------------------------------------------------
# PDF export (Platypus) – cover page + summary + tables + wrapping + rounding
# ------------------------------------------------------------


def build_pdf_report(
    data: Dict[str, Any], out_path: str, source_name: str = ""
) -> None:
    """
    High-quality PDF with cover page (title+metadata+summary), tables with proper wrapping,
    headers/footers, page numbers. All numeric values rounded to 2 decimals.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            KeepTogether,
        )
        from html import escape  # stdlib
    except Exception as e:
        raise RuntimeError(
            "PDF-export kräver paketet 'reportlab'. Installera med: pip install reportlab"
        ) from e

    data = sanitize(data)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleBig",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3", parent=styles["Heading3"], spaceBefore=10, spaceAfter=4
        )
    )
    styles.add(
        ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=11)
    )
    styles.add(
        ParagraphStyle(name="Body", parent=styles["BodyText"], fontSize=10, leading=13)
    )

    def as_paragraph(value: Any, style) -> Paragraph:
        """Paragraph for table cells to enable wrapping + number rounding."""
        text = fmt_number(value)
        text = escape(text)
        text = text.replace("\n", "<br/>")
        return Paragraph(text, style)

    analysis_object = str(data.get("analysis_object", "")).strip()
    title = f"Riskrapport för {analysis_object}" if analysis_object else "Riskrapport"

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
    )

    def header_footer(canvas, doc_obj):
        canvas.saveState()
        w, h = A4
        canvas.setFont("Helvetica", 9)
        canvas.drawString(18 * mm, h - 12 * mm, title)
        canvas.drawRightString(w - 18 * mm, 10 * mm, f"Sida {canvas.getPageNumber()}")
        canvas.restoreState()

    def kv_table(rows: List[Tuple[str, Any]], key_w=45 * mm) -> Table:
        table_data = [
            [
                as_paragraph("Fält", styles["Small"]),
                as_paragraph("Värde", styles["Small"]),
            ]
        ]
        for k, v in rows:
            table_data.append(
                [as_paragraph(k, styles["Small"]), as_paragraph(v, styles["Small"])]
            )

        t = Table(table_data, colWidths=[key_w, (doc.width - key_w)])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.whitesmoke, colors.white],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ]
            )
        )
        return t

    def metric_table(metrics: List[Tuple[str, Dict[str, Any]]]) -> Optional[Table]:
        cols = ["min", "probable", "max", "p90"]
        present = [
            c
            for c in cols
            if any(isinstance(m[1], dict) and c in m[1] for m in metrics)
        ]
        if not present:
            return None

        header = ["Mått"] + present
        rows = [[as_paragraph(h, styles["Small"]) for h in header]]

        for name, stats in metrics:
            row = [as_paragraph(name, styles["Small"])]
            for c in present:
                row.append(as_paragraph(stats.get(c, ""), styles["Small"]))
            rows.append(row)

        first = 55 * mm
        rest_total = doc.width - first
        rest = rest_total / max(1, len(present))
        col_widths = [first] + [rest] * len(present)

        t = Table(rows, colWidths=col_widths)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.whitesmoke, colors.white],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ]
            )
        )
        return t

    story: List[Any] = []

    # --- Cover page ---
    story.append(Paragraph(escape(title), styles["TitleBig"]))

    if source_name:
        story.append(Paragraph(f"Källa: {escape(str(source_name))}", styles["Small"]))
        story.append(Spacer(1, 6))

    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph(f"Genererad: {generated}", styles["Small"]))
    story.append(Spacer(1, 10))

    meta_rows = []
    for k in ["analysis_object", "version", "date", "scope", "owner"]:
        if k in data:
            meta_rows.append((k, data[k]))
    if meta_rows:
        story.append(Paragraph("Metadata", styles["H2"]))
        story.append(kv_table(meta_rows))
        story.append(Spacer(1, 10))

    if "summary" in data and isinstance(data["summary"], dict) and data["summary"]:
        story.append(Paragraph("Sammanfattning", styles["H2"]))
        story.append(kv_table(list(data["summary"].items())))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # --- Content ---
    scenarios = data.get("scenarios", [])
    if isinstance(scenarios, list) and scenarios:
        story.append(Paragraph(f"Scenarier ({len(scenarios)})", styles["H2"]))

        for i, sc in enumerate(scenarios, start=1):
            name = sc.get("name", f"Scenario {i}")

            # Keep scenario title + overview/qual/quant together
            main_block: List[Any] = [
                Paragraph(f"{i}. {escape(str(name))}", styles["H3"])
            ]

            overview_rows = []
            for k in [
                "category",
                "actor",
                "asset",
                "threat",
                "vulnerability_desc",
                "description",
            ]:
                v = sc.get(k, None)
                if v not in ("", None):
                    overview_rows.append((k, v))
            if overview_rows:
                main_block.append(Paragraph("Översikt", styles["Body"]))
                main_block.append(kv_table(overview_rows))

            risk = sc.get("risk", {})
            if isinstance(risk, dict):
                qualitative = risk.get("qualitative", {})
                quantitative = risk.get("quantitative", {})

                if isinstance(qualitative, dict) and qualitative:
                    q_rows = []
                    for k in ["overall_likelihood", "impact", "overall_risk"]:
                        if k in qualitative:
                            q_rows.append((k, qualitative[k]))
                    if q_rows:
                        main_block.append(Spacer(1, 8))
                        main_block.append(Paragraph("Kvalitativ risk", styles["Body"]))
                        main_block.append(kv_table(q_rows))

                if isinstance(quantitative, dict) and quantitative:
                    main_block.append(Spacer(1, 8))
                    main_block.append(Paragraph("Kvantitativ risk", styles["Body"]))

                    qmeta = []
                    for k in ["currency", "budget"]:
                        if k in quantitative:
                            qmeta.append((k, quantitative[k]))
                    if qmeta:
                        main_block.append(kv_table(qmeta))

                    metrics: List[Tuple[str, Dict[str, Any]]] = []
                    for k, v in quantitative.items():
                        if isinstance(v, dict) and any(
                            x in v for x in ("min", "probable", "max", "p90")
                        ):
                            metrics.append((k, v))
                    mt = metric_table(metrics)
                    if mt is not None:
                        main_block.append(mt)

            story.append(KeepTogether(main_block))

            # Questionnaires (may spill to next pages)
            qn = sc.get("questionaires", {})
            if isinstance(qn, dict) and qn:
                story.append(Spacer(1, 10))
                story.append(Paragraph("Frågebatterier", styles["Body"]))

                qa_rows = [
                    [
                        as_paragraph("Fråga", styles["Small"]),
                        as_paragraph("Svar", styles["Small"]),
                    ]
                ]
                found_any = False

                for _battery_name, qobj in qn.items():
                    if not isinstance(qobj, dict):
                        continue
                    questions = qobj.get("questions", [])
                    if not (isinstance(questions, list) and questions):
                        continue
                    for q in questions:
                        q_text = q.get("text", "")
                        ans = q.get("answer", {})
                        ans_text = ans.get("text", "") if isinstance(ans, dict) else ""
                        qa_rows.append(
                            [
                                as_paragraph(q_text, styles["Small"]),
                                as_paragraph(
                                    ans_text if ans_text else "(saknas)",
                                    styles["Small"],
                                ),
                            ]
                        )
                        found_any = True

                if found_any:
                    t = Table(qa_rows, colWidths=[doc.width * 0.62, doc.width * 0.38])
                    t.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                (
                                    "ROWBACKGROUNDS",
                                    (0, 1),
                                    (-1, -1),
                                    [colors.whitesmoke, colors.white],
                                ),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                                ("TOPPADDING", (0, 0), (-1, -1), 4),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                            ]
                        )
                    )
                    story.append(t)
                else:
                    story.append(Paragraph("Inga frågor hittades.", styles["Small"]))

            story.append(Spacer(1, 14))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def default_out_name(in_path: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(in_path))[0]
    return f"{base}_rapport.{ext}"


def main():
    ap = argparse.ArgumentParser(
        description="Läser risk-JSON och genererar formaterad rapport (Markdown, valfritt PDF)."
    )
    ap.add_argument("inputs", nargs="+", help="En eller flera JSON-filer.")
    ap.add_argument("-o", "--outdir", default=".", help="Ut-katalog (default: .)")
    ap.add_argument(
        "--pdf", action="store_true", help="Generera även PDF (kräver reportlab)."
    )
    ap.add_argument(
        "--no-md", action="store_true", help="Skapa inte Markdown, bara PDF (om --pdf)."
    )
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    for in_path in args.inputs:
        data = load_json(in_path)
        data_clean = sanitize(data)

        md = generate_markdown_report(data_clean, source_name=os.path.basename(in_path))
        md_path = os.path.join(args.outdir, default_out_name(in_path, "md"))

        if not args.no_md:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Skrev: {md_path}")

        if args.pdf:
            pdf_path = os.path.join(args.outdir, default_out_name(in_path, "pdf"))
            build_pdf_report(
                data_clean, pdf_path, source_name=os.path.basename(in_path)
            )
            print(f"Skrev: {pdf_path}")


if __name__ == "__main__":
    main()
