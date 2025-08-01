"""
Telemetry configuration for AI Manim pipeline.
Configures Arize Phoenix with file export optimized for DuckDB analysis.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import phoenix as px
from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource


class FileSpanExporter:
    """Custom exporter that writes spans to JSONL files for DuckDB consumption."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def export(self, spans):
        """Export spans to JSONL format for DuckDB."""
        with open(self.file_path, "a", encoding="utf-8") as f:
            for span in spans:
                span_data = {
                    "trace_id": format(span.context.trace_id, "032x"),
                    "span_id": format(span.context.span_id, "016x"),
                    "parent_span_id": format(span.parent.span_id, "016x")
                    if span.parent
                    else None,
                    "name": span.name,
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                    "duration_ns": span.end_time - span.start_time
                    if span.end_time
                    else None,
                    "status_code": span.status.status_code.name
                    if span.status
                    else None,
                    "attributes": dict(span.attributes) if span.attributes else {},
                    "events": [
                        {
                            "name": event.name,
                            "timestamp": event.timestamp,
                            "attributes": dict(event.attributes)
                            if event.attributes
                            else {},
                        }
                        for event in span.events
                    ]
                    if span.events
                    else [],
                    "resource_attributes": dict(span.resource.attributes)
                    if span.resource
                    else {},
                }
                f.write(json.dumps(span_data) + "\n")
        return 0  # Success

    def shutdown(self):
        """Shutdown the exporter."""
        pass


def setup_telemetry(
    export_to_file: bool = True,
    file_path: Optional[str] = None,
    phoenix_endpoint: Optional[str] = None,
) -> Optional[TracerProvider]:
    """
    Set up telemetry with Phoenix and file export.

    Args:
        export_to_file: Whether to export traces to file
        file_path: Path for trace file (defaults to telemetry/traces/{timestamp}.jsonl)
        phoenix_endpoint: Phoenix endpoint URL (defaults to local)

    Returns:
        TracerProvider instance
    """

    # Skip if telemetry is disabled
    if os.getenv("DISABLE_TELEMETRY", "").lower() in ("true", "1", "yes"):
        return None

    # Start Phoenix session if not disabled
    if os.getenv("DISABLE_PHOENIX", "").lower() not in ("true", "1", "yes"):
        session = px.launch_app()
        print(f"Phoenix UI available at: {session.url}")

    # Set up resource
    resource = Resource.create(
        {
            "service.name": "ai-manim-pipeline",
            "service.version": "0.1.0",
        }
    )

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Add Phoenix exporter if endpoint provided
    if phoenix_endpoint or os.getenv("DISABLE_PHOENIX", "").lower() not in (
        "true",
        "1",
        "yes",
    ):
        endpoint = phoenix_endpoint or "http://localhost:6006/v1/traces"
        phoenix_exporter = OTLPSpanExporter(endpoint=endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(phoenix_exporter))

    # Add file exporter if enabled
    if export_to_file:
        if not file_path:
            file_path = "telemetry/traces.jsonl"

        file_exporter = FileSpanExporter(file_path)
        tracer_provider.add_span_processor(SimpleSpanProcessor(file_exporter))
        print(f"Telemetry traces will be saved to: {file_path}")

    # Instrument DSPy
    DSPyInstrumentor().instrument()

    return tracer_provider


def shutdown_telemetry():
    """Shutdown telemetry and clean up resources."""
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, "shutdown"):
        tracer_provider.shutdown()

    # Uninstrument DSPy
    DSPyInstrumentor().uninstrument()


# Environment-based configuration
def get_telemetry_config():
    """Get telemetry configuration from environment variables."""
    return {
        "export_to_file": os.getenv("TELEMETRY_EXPORT_FILE", "true").lower()
        in ("true", "1", "yes"),
        "file_path": os.getenv("TELEMETRY_FILE_PATH"),
        "phoenix_endpoint": os.getenv("PHOENIX_ENDPOINT"),
    }
