# AI Workflow Prototypes

This repo contains small AI-native workflow prototypes inspired by startup use cases in operations, voice, and design systems.

## 1. ArchiLabs-style AI CAD Prototype
- Converts natural language into a structured layout spec
- Validates constraints
- Renders a visual rack layout
- Endpoints:
  - `/parse`
  - `/preview`
  - `/preview-demo`

## 2. Revion-style Service Workflow Prototype
- Converts technician/customer service notes into structured service data
- Extracts:
  - issue category
  - priority
  - vehicle
  - customer need
  - recommended action
  - service tags
- Endpoints:
  - `/service-agent`
  - `/service-demo`

## Why this matters
These prototypes explore a common AI systems pattern:

**unstructured input → structured representation → operational action**

This pattern is useful across:
- automotive operations
- logistics voice agents
- layout/CAD systems

## Tech
- FastAPI
- Python
- OpenAI API
- Pydantic
- HTML/SVG demo rendering

## Run locally

```bash
uvicorn app:app --reload