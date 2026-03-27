import os
import json
import math
from typing import List, Optional, Literal
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="ArchiLabs Prototype")


class LayoutSpec(BaseModel):
    project_type: Literal["data_center"] = "data_center"
    racks: int = Field(..., ge=1, le=1000)
    cooling_zones: int = Field(..., ge=1, le=100)
    redundancy: str
    aisles: int = Field(..., ge=1, le=100)
    constraints: List[str] = []
    notes: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]


class RackBox(BaseModel):
    rack_id: str
    x: int
    y: int
    width: int
    height: int
    aisle_after: bool


class RenderedLayout(BaseModel):
    rows: int
    cols: int
    rack_boxes: List[RackBox]
    svg: str


class ParseResponse(BaseModel):
    parsed_spec: LayoutSpec
    validation: ValidationResult
    rendered_layout: RenderedLayout


class PromptInput(BaseModel):
    user_prompt: str


def validate_layout(spec: LayoutSpec) -> ValidationResult:
    issues = []

    if spec.racks < 4 and spec.cooling_zones > 2:
        issues.append("Cooling zones seem too high for a very small rack count.")

    if spec.aisles > spec.racks:
        issues.append("Aisles cannot exceed racks in this simplified model.")

    if spec.redundancy.strip().lower() not in {"n", "n+1", "2n", "none"}:
        issues.append("Redundancy must be one of: N, N+1, 2N, none.")

    if spec.racks >= 20 and spec.cooling_zones < 2:
        issues.append("Larger layouts should usually have at least 2 cooling zones.")

    return ValidationResult(
        is_valid=len(issues) == 0,
        issues=issues
    )


def prompt_llm(user_prompt: str) -> dict:
    system_prompt = """
You are an assistant that converts natural language data center design requests
into a strict JSON object.

Return ONLY valid JSON with this schema:
{
  "project_type": "data_center",
  "racks": integer,
  "cooling_zones": integer,
  "redundancy": string,
  "aisles": integer,
  "constraints": [string],
  "notes": string or null
}

Rules:
- project_type must always be "data_center"
- infer reasonable defaults if values are missing
- default redundancy to "N+1"
- default cooling_zones to 2
- default aisles to 2
- default constraints to []
- do not include markdown
- do not include explanations
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    text = response.output_text.strip()
    return json.loads(text)


def render_layout(spec: LayoutSpec) -> RenderedLayout:
    rack_width = 70
    rack_height = 120
    gap_x = 25
    gap_y = 30
    aisle_gap = 70
    margin = 30

    cols = min(6, spec.racks)
    rows = math.ceil(spec.racks / cols)

    rack_boxes = []
    svg_parts = []

    total_width = margin * 2 + cols * rack_width + (cols - 1) * gap_x + aisle_gap
    total_height = margin * 2 + rows * rack_height + (rows - 1) * gap_y + 60

    svg_parts.append(
        f'<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">'
    )
    svg_parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')
    svg_parts.append('<text x="30" y="20" font-size="16" font-family="Arial" fill="#111827">Data Center Layout Preview</text>')

    aisle_column = max(1, cols // 2)

    for i in range(spec.racks):
        row = i // cols
        col = i % cols

        extra_gap = aisle_gap if col >= aisle_column else 0
        x = margin + col * (rack_width + gap_x) + extra_gap
        y = margin + 20 + row * (rack_height + gap_y)

        rack_id = f"R{i+1}"
        aisle_after = col == aisle_column - 1

        rack_boxes.append(
            RackBox(
                rack_id=rack_id,
                x=x,
                y=y,
                width=rack_width,
                height=rack_height,
                aisle_after=aisle_after
            )
        )

        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="{rack_width}" height="{rack_height}" '
            f'fill="#cbd5e1" stroke="#334155" stroke-width="2" rx="6" />'
        )
        svg_parts.append(
            f'<text x="{x + 18}" y="{y + 65}" font-size="16" font-family="Arial" fill="#111827">{rack_id}</text>'
        )

    aisle_x = margin + aisle_column * (rack_width + gap_x) + (aisle_gap / 2) - 15
    svg_parts.append(
        f'<text x="{int(aisle_x)}" y="{total_height - 15}" font-size="14" font-family="Arial" fill="#dc2626">Aisle</text>'
    )

    svg_parts.append("</svg>")

    return RenderedLayout(
        rows=rows,
        cols=cols,
        rack_boxes=rack_boxes,
        svg="".join(svg_parts)
    )


@app.get("/")
def home():
    return {"message": "ArchiLabs prototype is running"}


@app.post("/parse", response_model=ParseResponse)
def parse_prompt(data: PromptInput):
    parsed = prompt_llm(data.user_prompt)
    spec = LayoutSpec(**parsed)
    validation = validate_layout(spec)
    rendered_layout = render_layout(spec)

    return ParseResponse(
        parsed_spec=spec,
        validation=validation,
        rendered_layout=rendered_layout
    )

@app.post("/preview", response_class=HTMLResponse)
def preview_prompt(data: PromptInput):
    parsed = prompt_llm(data.user_prompt)
    spec = LayoutSpec(**parsed)
    rendered_layout = render_layout(spec)

    html = f"""
    <html>
        <head>
            <title>ArchiLabs Layout Preview</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f8fafc;
                    padding: 24px;
                    color: #111827;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                    max-width: 900px;
                    margin: auto;
                }}
                .meta {{
                    margin-bottom: 16px;
                    line-height: 1.6;
                }}
                .label {{
                    font-weight: bold;
                }}
                .svg-wrap {{
                    overflow-x: auto;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 12px;
                    background: #ffffff;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>ArchiLabs Layout Preview</h2>
                <div class="meta">
                    <div><span class="label">Project Type:</span> {spec.project_type}</div>
                    <div><span class="label">Racks:</span> {spec.racks}</div>
                    <div><span class="label">Cooling Zones:</span> {spec.cooling_zones}</div>
                    <div><span class="label">Redundancy:</span> {spec.redundancy}</div>
                    <div><span class="label">Aisles:</span> {spec.aisles}</div>
                </div>
                <div class="svg-wrap">
                    {rendered_layout.svg}
                </div>
            </div>
        </body>
    </html>
    """
    return html

@app.get("/preview-demo", response_class=HTMLResponse)
def preview_demo():
    prompt = "Design a small data center with 12 racks, 2 cooling zones, N+1 redundancy, and 2 aisles."

    parsed = prompt_llm(prompt)
    spec = LayoutSpec(**parsed)
    rendered_layout = render_layout(spec)

    html = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2>ArchiLabs Demo</h2>
            <p><b>Prompt:</b> {prompt}</p>
            {rendered_layout.svg}
        </body>
    </html>
    """
    return html