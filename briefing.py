# briefing.py
from pathlib import Path
from collections import defaultdict
import re


def _mini_summary(title: str) -> str:
    """
    Simple cleaning.
    (If you want true summarization, plug in an LLM API later.)
    """
    t = re.sub(r"\s+", " ", title).strip()
    t = re.sub(r"\s-\s.*$", "", t)  # remove trailing " - Source"
    return t


def write_briefing(rows: list[dict], out_md: Path, out_txt: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)

    grouped = defaultdict(list)
    for r in rows:
        grouped[r["source"]].append(r)

    md_lines = []
    txt_lines = []

    md_lines.append("# Daily News Briefing\n")
    txt_lines.append("DAILY NEWS BRIEFING\n")

    for source, items in grouped.items():
        md_lines.append(f"## {source}\n")
        txt_lines.append(f"\n{source}\n" + "-" * len(source))

        for it in items[:30]:
            bullet = _mini_summary(it["title"])
            md_lines.append(f"- **{bullet}**  \n  {it['url']}\n")
            txt_lines.append(f"- {bullet}\n  {it['url']}")

        md_lines.append("\n")

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    out_txt.write_text("\n".join(txt_lines), encoding="utf-8")
