#!/usr/bin/env python3
"""Create and maintain a bid-editing workspace inside the Focus repo."""

from __future__ import annotations

import argparse
import csv
import json
import textwrap
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


DEFAULT_REQUESTED_EDITS = [
    "Apply the gold-line RLC bid/contract page styling once the template file is provided.",
    "Keep the company logo, but crop/remove the black square background so it fits the page background cleanly.",
    "Update the materials/pricing sheet with current supplier pricing when source files are available.",
    "Add one drywall T-square line item.",
    "Add one DeWalt laser line item suitable for drop ceilings/drywall layout.",
    "Add one box of Hilti collated drywall gun screw strips in 1-5/8 in.",
    "Add one box of Hilti collated drywall gun screw strips in 1-1/4 in.",
    "Include delivery as a separate cost line.",
    "Include a $400 Big River Disposal dumpster/trash removal line item.",
    "Calculate Quincy, Illinois commercial remodel permit fee from the final contract value.",
]

DEFAULT_EXCLUSIONS = [
    "Leave out the floor plans.",
]

DEFAULT_REQUIRED_ASSETS = [
    "Current bid PDF or editable source file",
    "Gold-line RLC template file",
    "Company logo source file with the highest available resolution",
]

DEFAULT_PRICING_ROWS = [
    {
        "item": "48 in. drywall T-square",
        "quantity": "1",
        "unit": "ea",
        "source": "Menards lookup pending",
        "unit_price": "",
        "total": "",
        "status": "pending",
        "notes": "Requested add-on for drywall/layout work.",
    },
    {
        "item": "DeWalt laser for drop ceilings/drywall",
        "quantity": "1",
        "unit": "ea",
        "source": "Current supplier lookup pending",
        "unit_price": "",
        "total": "",
        "status": "pending",
        "notes": "Use a DeWalt model suitable for ceiling and drywall layout.",
    },
    {
        "item": "Hilti collated drywall screw strips 1-5/8 in.",
        "quantity": "1",
        "unit": "box",
        "source": "Current supplier lookup pending",
        "unit_price": "",
        "total": "",
        "status": "pending",
        "notes": "One box requested for ceilings.",
    },
    {
        "item": "Hilti collated drywall screw strips 1-1/4 in.",
        "quantity": "1",
        "unit": "box",
        "source": "Current supplier lookup pending",
        "unit_price": "",
        "total": "",
        "status": "pending",
        "notes": "One box requested for ceilings.",
    },
    {
        "item": "Delivery fee",
        "quantity": "1",
        "unit": "lot",
        "source": "Supplier delivery quote pending",
        "unit_price": "",
        "total": "",
        "status": "pending",
        "notes": "Keep as separate line item.",
    },
    {
        "item": "Big River Disposal dumpster/trash removal",
        "quantity": "1",
        "unit": "lot",
        "source": "User-directed allowance",
        "unit_price": "400.00",
        "total": "400.00",
        "status": "ready",
        "notes": "Fixed amount requested by user.",
    },
    {
        "item": "Quincy, IL commercial remodel permit fee",
        "quantity": "1",
        "unit": "lot",
        "source": "City of Quincy fee schedule",
        "unit_price": "",
        "total": "",
        "status": "formula",
        "notes": "Fee = max($75, construction value x 0.005) for commercial remodeling/repairs.",
    },
]


@dataclass
class BidRequest:
    project_name: str
    project_slug: str
    location: str
    project_type: str
    status: str
    scope_summary: str
    requested_edits: list[str]
    exclusions: list[str]
    required_assets: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a Focus bid-editing workspace.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or refresh a project workspace")
    init_parser.add_argument("slug", help="Project folder slug, for example quincy-office-remodel")
    init_parser.add_argument("--project-name", required=True, help="Human-readable project name")
    init_parser.add_argument("--location", default="Quincy, IL", help="Project location")
    init_parser.add_argument(
        "--project-type",
        default="Office remodel",
        help="Short project type label",
    )
    init_parser.add_argument(
        "--scope-summary",
        default="Office remodel bid update based on the current bid package once files are supplied.",
        help="Short scope summary",
    )
    init_parser.add_argument(
        "--root",
        default="projects",
        help="Workspace root directory relative to the repo",
    )

    export_parser = subparsers.add_parser("export-pdfs", help="Export project artifacts to basic PDFs")
    export_parser.add_argument("slug", help="Project folder slug, for example quincy-office-remodel")
    export_parser.add_argument(
        "--root",
        default="projects",
        help="Workspace root directory relative to the repo",
    )
    return parser.parse_args()


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, request: BidRequest) -> None:
    content = f"""# {request.project_name}\n\n## Project snapshot\n- **Location:** {request.location}\n- **Type:** {request.project_type}\n- **Status:** {request.status}\n\n## Scope summary\n{request.scope_summary}\n\n## Requested edits\n"""
    for item in request.requested_edits:
        content += f"- {item}\n"
    content += "\n## Exclusions\n"
    for item in request.exclusions:
        content += f"- {item}\n"
    content += "\n## Required source assets\n"
    for item in request.required_assets:
        content += f"- {item}\n"
    content += "\n## Working folders\n- `input/` for client-supplied PDFs, templates, and logo files\n- `working/` for edited drafts and extracted assets\n- `output/` for final deliverables\n- `notes/` for research, assumptions, and approval notes\n"
    path.write_text(content, encoding="utf-8")


def write_checklist(path: Path) -> None:
    content = """# Bid edit checklist\n\n- [ ] Drop the current bid PDF or editable source into `input/`.\n- [ ] Drop the gold-line RLC template into `input/`.\n- [ ] Drop the highest-quality logo source into `input/`.\n- [ ] Confirm the final contract value so the Quincy permit fee can be calculated.\n- [ ] Update the pricing sheet with live supplier pricing.\n- [ ] Apply the visual template to the bid pages.\n- [ ] Remove/crop the black square around the company logo.\n- [ ] Exclude floor plan pages from the revised package.\n- [ ] Export the revised bid package into `output/`.\n"""
    path.write_text(content, encoding="utf-8")


def write_research(path: Path) -> None:
    content = """# Research notes\n\n## Quincy, Illinois permit fee\n- The City of Quincy commercial, industrial, and multi-family permit schedule states a **minimum permit fee of $75**.\n- For **commercial remodeling and repairs**, the fee is **construction value x 0.005**.\n- Working formula for this job: `permit_fee = max(75, contract_value * 0.005)`.\n\n## Known blockers\n- The source bid PDF, the gold-line template, and the original logo file are not yet present in this repository.\n- Menards product pages are bot-protected in this environment, so live pricing may need to be copied in manually or sourced from an alternate accessible quote page when the pricing pass is performed.\n- Because the current bid package is missing, material quantities from the existing estimate cannot yet be reconciled.\n\n## User-directed estimate lines to preserve\n- Include delivery as a separate line item.\n- Include **$400** for Big River Disposal dumpster/trash removal.\n- Leave out floor plans from the revised package.\n"""
    path.write_text(content, encoding="utf-8")


def wrap_text(text: str, width: int = 92) -> list[str]:
    wrapped: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=width, replace_whitespace=False) or [""])
    return wrapped


def escape_pdf_text(value: str) -> str:
    return value.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def build_pdf_bytes(title: str, lines: list[str]) -> bytes:
    page_width = 612
    page_height = 792
    margin = 50
    font_size = 11
    line_height = 14
    lines_per_page = 48

    if not lines:
        lines = [""]

    page_chunks = [lines[index:index + lines_per_page] for index in range(0, len(lines), lines_per_page)]

    objects: list[bytes] = []

    def add_object(data: str | bytes) -> int:
        payload = data.encode('latin-1') if isinstance(data, str) else data
        objects.append(payload)
        return len(objects)

    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    pages_id = add_object(b"")
    page_ids: list[int] = []

    for page_lines in page_chunks:
        text_lines = [f"({escape_pdf_text(title)}) Tj"]
        text_lines.append(f"0 -{line_height * 2} Td")
        for index, line in enumerate(page_lines):
            if index > 0:
                text_lines.append("T*")
            text_lines.append(f"({escape_pdf_text(line)}) Tj")
        stream = "BT\n/F1 {size} Tf\n1 0 0 1 {x} {y} Tm\n{body}\nET".format(
            size=font_size,
            x=margin,
            y=page_height - margin,
            body="\n".join(text_lines),
        )
        stream_bytes = stream.encode('latin-1')
        content_id = add_object(b"<< /Length %d >>\nstream\n" % len(stream_bytes) + stream_bytes + b"\nendstream")
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {page_width} {page_height}] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    pages_kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{pages_kids}] /Count {len(page_ids)} >>".encode('latin-1')
    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode('latin-1'))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode('latin-1'))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode('latin-1'))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode('latin-1')
    )
    return bytes(pdf)


def write_pdf(path: Path, title: str, body: str) -> None:
    lines = wrap_text(body)
    path.write_bytes(build_pdf_bytes(title, lines))


def format_csv_as_text(path: Path) -> str:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    columns = list(rows[0].keys()) if rows else []
    widths = {column: len(column) for column in columns}
    for row in rows:
        for column in columns:
            widths[column] = min(max(widths[column], len(row[column])), 40)
    header = " | ".join(column.ljust(widths[column]) for column in columns)
    divider = "-+-".join("-" * widths[column] for column in columns)
    lines = [header, divider]
    for row in rows:
        lines.append(" | ".join(row[column][: widths[column]].ljust(widths[column]) for column in columns))
    return "\n".join(lines)


def export_pdfs(args: argparse.Namespace) -> list[Path]:
    repo_root = Path.cwd()
    project_root = repo_root / args.root / args.slug
    output_root = project_root / "output"
    ensure_dirs([output_root])

    exports = [
        (
            project_root / "README.md",
            output_root / "project_overview.pdf",
            f"{args.slug} project overview",
        ),
        (
            project_root / "output" / "package_edit_pass.md",
            output_root / "package_edit_pass.pdf",
            f"{args.slug} package edit pass",
        ),
        (
            project_root / "notes" / "research.md",
            output_root / "research_notes.pdf",
            f"{args.slug} research notes",
        ),
        (
            project_root / "notes" / "checklist.md",
            output_root / "checklist.pdf",
            f"{args.slug} checklist",
        ),
    ]

    created: list[Path] = []
    for source_path, pdf_path, title in exports:
        if source_path.exists():
            write_pdf(pdf_path, title, source_path.read_text(encoding="utf-8"))
            created.append(pdf_path)

    pricing_source = project_root / "materials_pricing.csv"
    if pricing_source.exists():
        write_pdf(
            output_root / "materials_pricing.pdf",
            f"{args.slug} materials pricing",
            format_csv_as_text(pricing_source),
        )
        created.append(output_root / "materials_pricing.pdf")

    request_source = project_root / "request.json"
    if request_source.exists():
        pretty_request = json.dumps(json.loads(request_source.read_text(encoding="utf-8")), indent=2)
        write_pdf(output_root / "request_snapshot.pdf", f"{args.slug} request snapshot", pretty_request)
        created.append(output_root / "request_snapshot.pdf")

    return created


def init_workspace(args: argparse.Namespace) -> Path:
    repo_root = Path.cwd()
    project_root = repo_root / args.root / args.slug
    ensure_dirs(
        [
            project_root / "input",
            project_root / "working",
            project_root / "output",
            project_root / "notes",
        ]
    )

    request = BidRequest(
        project_name=args.project_name,
        project_slug=args.slug,
        location=args.location,
        project_type=args.project_type,
        status="intake-created",
        scope_summary=args.scope_summary,
        requested_edits=DEFAULT_REQUESTED_EDITS,
        exclusions=DEFAULT_EXCLUSIONS,
        required_assets=DEFAULT_REQUIRED_ASSETS,
    )

    write_json(project_root / "request.json", asdict(request))
    write_markdown(project_root / "README.md", request)
    write_checklist(project_root / "notes" / "checklist.md")
    write_research(project_root / "notes" / "research.md")
    write_csv(project_root / "materials_pricing.csv", DEFAULT_PRICING_ROWS)

    return project_root


def main() -> int:
    args = parse_args()
    if args.command == "init":
        project_root = init_workspace(args)
        print(f"Created bid workspace at {project_root}")
        return 0
    if args.command == "export-pdfs":
        created = export_pdfs(args)
        for pdf_path in created:
            print(pdf_path)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
