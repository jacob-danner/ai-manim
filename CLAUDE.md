# AI Manim Visualization

## Vision

Two-stage approach to automated Manim code generation:

### Stage 1: Reference Diagram -> Manim Code (in progress)
- Input: Reference diagram (image)
- Output: Working Manim code that recreates the diagram

### Stage 2: Text Description -> Manim Code
- Input: Text description of desired animation
- Output: Working Manim code that reflects the input text

## Development Commands
- `uv run ruff check .` - Lint code
- `uv run ruff format .` - Format code
- `uv run manim -s visualization.py` - Run manim

## Telemetry Commands
- `uv run python test_telemetry.py` - Test telemetry setup and instrumentation
- `uv run python main.py` - Run pipeline with telemetry (traces saved to `telemetry/traces/`)
- `uv run python analyze_traces.py` - Analyze traces with DuckDB

### Telemetry Configuration (Environment Variables)
- `DISABLE_TELEMETRY=true` - Disable all telemetry
- `DISABLE_PHOENIX=true` - Disable Phoenix UI (keep file export)
- `TELEMETRY_FILE_PATH=path/to/traces.jsonl` - Custom trace file path
- `PHOENIX_ENDPOINT=http://localhost:6006/v1/traces` - Custom Phoenix endpoint