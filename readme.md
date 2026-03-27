# ArchiLabs Prototype — NL to Layout Engine

This is a small prototype inspired by ArchiLabs' code-first CAD approach.

## What it does

- Converts natural language → structured layout spec
- Applies basic constraint validation (cooling zones, redundancy, aisles)
- Generates a simple layout representation
- Renders a visual layout preview (SVG)

## Example

Input:
"Design a small data center with 12 racks, 2 cooling zones, N+1 redundancy, and 2 aisles."

Output:
- Structured JSON spec
- Validation layer
- Visual layout preview

## Demo

Run locally:

uvicorn app:app --reload

## Extension Idea
Applying similar structured parsing + validation to engineering drawings (PDFs) using OCR + CV + rule-based checks for QA/QC.
