"""Reverse-engineer the star schema diagram from the live ecommerce_dw database.

Run from the project root: uv run python -m scripts.generate_erd
Writes docs/star_schema.dot, .svg and .png (needs Graphviz: brew install graphviz)
"""
import subprocess
from html import escape
from pathlib import Path

from sqlalchemy import inspect

from app.db import warehouse_engine

DOCS = Path(__file__).resolve().parent.parent / "docs"
OUT = DOCS / "star_schema"

FACT_COLOR = "#F4B183"
DIM_COLOR = "#9DC3E6"


def table_label(name, columns, pk, fks, is_fact):
    header = FACT_COLOR if is_fact else DIM_COLOR
    rows = [f'<TR><TD COLSPAN="3" BGCOLOR="{header}"><B>{escape(name)}</B></TD></TR>']
    for col in columns:
        c = col["name"]
        key = "PK" if c in pk else "FK" if c in fks else ""
        name_cell = f"<U>{escape(c)}</U>" if key == "PK" else escape(c)
        rows.append(
            f'<TR><TD ALIGN="LEFT" PORT="{c}">{name_cell}</TD>'
            f'<TD ALIGN="LEFT"><FONT COLOR="#555555">{escape(str(col["type"]).lower())}</FONT></TD>'
            f'<TD PORT="{c}_r">{f"<B>{key}</B>" if key else " "}</TD></TR>'
        )
    return f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">{"".join(rows)}</TABLE>>'


def build_dot():
    insp = inspect(warehouse_engine)
    tables = insp.get_table_names()
    fks = {t: insp.get_foreign_keys(t) for t in tables}
    facts = [t for t in tables if fks[t]]          # tables that reference others are facts
    dims = [t for t in tables if t not in facts]
    left, right = dims[: len(dims) // 2], dims[len(dims) // 2:]

    lines = [
        "digraph star_schema {",
        '  graph [rankdir=LR, splines=spline, nodesep=0.6, ranksep=1.5, fontname="Helvetica"];',
        '  node [shape=plaintext, fontname="Helvetica", fontsize=11];',
        '  edge [fontname="Helvetica", fontsize=11, arrowsize=1.2, labeldistance=1.8, dir=both];',
    ]
    for t in tables:
        pk = set(insp.get_pk_constraint(t)["constrained_columns"])
        fk_cols = {c for fk in fks[t] for c in fk["constrained_columns"]}
        lines.append(f"  {t} [label={table_label(t, insp.get_columns(t), pk, fk_cols, t in facts)}];")

    # left dims -> fact -> right dims puts the fact table in the middle column;
    # each edge leaves/enters the side of its key row (tee = one, crow = many)
    for fact in facts:
        for fk in fks[fact]:
            dim, fcol, dcol = fk["referred_table"], fk["constrained_columns"][0], fk["referred_columns"][0]
            if dim in left:
                lines.append(f'  {dim}:{dcol}_r:e -> {fact}:{fcol}:w '
                             f'[arrowtail=tee, arrowhead=crow, taillabel="1", headlabel="N"];')
            else:
                lines.append(f'  {fact}:{fcol}_r:e -> {dim}:{dcol}:w '
                             f'[arrowtail=crow, arrowhead=tee, taillabel="N", headlabel="1"];')
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    DOCS.mkdir(exist_ok=True)
    OUT.with_suffix(".dot").write_text(build_dot())
    for fmt in ("svg", "png"):
        args = ["dot", f"-T{fmt}", str(OUT.with_suffix(".dot")), "-o", str(OUT.with_suffix(f".{fmt}"))]
        if fmt == "png":
            args.insert(1, "-Gdpi=200")
        subprocess.run(args, check=True)
    print(f"Wrote {OUT}.dot, .svg, .png")
