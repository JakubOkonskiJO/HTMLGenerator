#!/usr/bin/env python3
import argparse
import datetime as dt
import html
import pathlib
import re
from dataclasses import dataclass


@dataclass
class Metric:
    name: str
    value: str


def parse_markdown(markdown_text: str):
    lines = markdown_text.splitlines()
    title = "Generated Report"
    if lines:
        first_heading = re.match(r"^#\s+(.+)$", lines[0].strip())
        if first_heading:
            title = first_heading.group(1).strip()

    current_mode = "text"
    metrics: list[Metric] = []
    text_lines: list[str] = []

    for line in lines:
        heading = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if heading:
            heading_text = heading.group(1).strip().lower()
            if "metric" in heading_text or "kpi" in heading_text:
                current_mode = "metrics"
                continue
            if heading_text.startswith("text"):
                current_mode = "text"
                continue

        if current_mode == "metrics":
            bullet_metric = re.match(r"^\s*[-*]\s+([^:]+):\s*(.+)\s*$", line)
            if bullet_metric:
                metrics.append(Metric(bullet_metric.group(1).strip(), bullet_metric.group(2).strip()))
                continue

            bold_metric = re.match(r"^\s*\*\*([^*]+)\*\*\s*(.+)\s*$", line)
            if bold_metric:
                name = bold_metric.group(1).strip().rstrip(":")
                value = bold_metric.group(2).strip()
                if name and value:
                    metrics.append(Metric(name, value))
                    continue

            plain_metric = re.match(r"^\s*([^:]+):\s*(.+)\s*$", line)
            if plain_metric:
                metrics.append(Metric(plain_metric.group(1).strip(), plain_metric.group(2).strip()))
        elif current_mode == "text":
            text_lines.append(line)

    return title, metrics, text_lines


def render_text_section(lines: list[str]) -> str:
    output: list[str] = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        if re.match(r"^-{3,}$", stripped):
            close_list()
            continue

        heading_match = re.match(r"^(#{2,6})\s+(.+)$", stripped)
        if heading_match:
            close_list()
            level = min(len(heading_match.group(1)), 4)
            text = html.escape(heading_match.group(2).strip())
            output.append(f"<h{level}>{text}</h{level}>")
            continue

        list_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if list_match:
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{html.escape(list_match.group(1).strip())}</li>")
            continue

        close_list()
        output.append(f"<p>{html.escape(stripped)}</p>")

    close_list()
    return "\n".join(output)


def generate_html(title: str, metrics: list[Metric], text_lines: list[str]) -> str:
    metrics_html = "\n".join(
        f"<article class=\"metric-card\"><h3>{html.escape(m.name)}</h3><p>{html.escape(m.value)}</p></article>"
        for m in metrics
    )
    if not metrics_html:
        metrics_html = "<p class=\"empty\">No metrics were provided in the Metrics section.</p>"

    text_html = render_text_section(text_lines)
    if not text_html:
        text_html = "<p class=\"empty\">No narrative content was provided in the Text section.</p>"

    generated_on = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{html.escape(title)}</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f3f5ff;
        --panel: #ffffff;
        --accent: #4f46e5;
        --accent-2: #a855f7;
        --text: #111827;
        --subtle: #4b5563;
      }}
      body {{
        margin: 0;
        font-family: Inter, Segoe UI, Arial, sans-serif;
        background: linear-gradient(170deg, var(--bg), #eef2ff);
        color: var(--text);
      }}
      main {{ max-width: 960px; margin: 0 auto; padding: 2rem 1rem 4rem; }}
      .hero {{
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        color: #fff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 14px 36px rgba(79, 70, 229, 0.25);
      }}
      .hero p {{ margin: .5rem 0 0; opacity: .9; }}
      section {{ margin-top: 1.25rem; background: var(--panel); border-radius: 14px; padding: 1.25rem; }}
      h1, h2, h3, h4 {{ margin: 0; }}
      h2 {{ margin-bottom: .8rem; }}
      .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .8rem; }}
      .metric-card {{
        border: 1px solid #dbeafe;
        border-left: 5px solid var(--accent);
        border-radius: 12px;
        background: #f8faff;
        padding: .8rem;
      }}
      .metric-card h3 {{ font-size: .95rem; color: var(--subtle); margin-bottom: .35rem; }}
      .metric-card p {{ font-size: 1.4rem; font-weight: 700; margin: 0; color: var(--accent); }}
      .narrative p, .narrative li {{ color: #1f2937; line-height: 1.55; }}
      .narrative ul {{ margin-top: .3rem; padding-left: 1.25rem; }}
      .narrative h2, .narrative h3, .narrative h4 {{ margin: 1rem 0 .5rem; }}
      .empty {{ color: var(--subtle); margin: 0; }}
    </style>
  </head>
  <body>
    <main>
      <header class=\"hero\">
        <h1>{html.escape(title)}</h1>
        <p>Generated from markdown content on {generated_on}</p>
      </header>
      <section>
        <h2>Metrics & KPIs</h2>
        <div class=\"metrics-grid\">{metrics_html}</div>
      </section>
      <section class=\"narrative\">
        <h2>Text</h2>
        {text_html}
      </section>
    </main>
  </body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate report page from markdown")
    parser.add_argument("--input", required=True, help="Path to markdown input file")
    parser.add_argument("--output", required=True, help="Path to generated html output")
    args = parser.parse_args()

    markdown_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    content = markdown_path.read_text(encoding="utf-8")
    title, metrics, text_lines = parse_markdown(content)
    page = generate_html(title, metrics, text_lines)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
