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