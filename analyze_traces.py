"""
Sample DuckDB analysis of telemetry traces.
Demonstrates how to query and analyze the exported trace data.
"""

import duckdb
from pathlib import Path


def analyze_traces(trace_file: str = "telemetry/test_traces.jsonl"):
    """Analyze traces using DuckDB."""

    if not Path(trace_file).exists():
        print(f"❌ Trace file not found: {trace_file}")
        print("Run `uv run python test_telemetry.py` first to generate traces")
        return

    # Connect to DuckDB
    conn = duckdb.connect()

    print(f"📊 Analyzing traces from: {trace_file}")
    print("=" * 50)

    # Load trace data
    conn.execute(f"""
        CREATE TABLE traces AS 
        SELECT * FROM read_json_auto('{trace_file}')
    """)

    # Basic trace statistics
    print("\n🔢 Basic Statistics:")
    result = conn.execute("""
        SELECT 
            COUNT(*) as total_spans,
            COUNT(DISTINCT trace_id) as unique_traces,
            MIN(start_time) as earliest_span,
            MAX(end_time) as latest_span
        FROM traces
    """).fetchone()

    print(f"  Total spans: {result[0]}")
    print(f"  Unique traces: {result[1]}")

    # Span types analysis
    print("\n📋 Span Types:")
    results = conn.execute("""
        SELECT 
            name,
            COUNT(*) as count,
            AVG(duration_ns / 1000000.0) as avg_duration_ms
        FROM traces 
        GROUP BY name 
        ORDER BY count DESC
    """).fetchall()

    for name, count, avg_duration in results:
        print(f"  {name}: {count} spans, avg {avg_duration:.2f}ms")

    # LLM call analysis
    print("\n🤖 LLM Call Analysis:")
    llm_calls = conn.execute("""
        SELECT 
            json_extract_string(attributes, '$.llm.model_name') as model,
            json_extract_string(attributes, '$.llm.provider') as provider,
            COUNT(*) as calls,
            AVG(duration_ns / 1000000.0) as avg_duration_ms,
            SUM(duration_ns / 1000000.0) as total_duration_ms
        FROM traces 
        WHERE name = 'LM.__call__'
        GROUP BY model, provider
    """).fetchall()

    for model, provider, calls, avg_duration, total_duration in llm_calls:
        print(
            f"  {provider}/{model}: {calls} calls, avg {avg_duration:.2f}ms, total {total_duration:.2f}ms"
        )

    # Token usage (if available in attributes)
    print("\n💰 Token Usage Analysis:")
    token_usage = conn.execute("""
        SELECT 
            json_extract_string(attributes, '$.llm.model_name') as model,
            json_extract_string(attributes, '$.llm.usage.prompt_tokens') as prompt_tokens,
            json_extract_string(attributes, '$.llm.usage.completion_tokens') as completion_tokens,
            json_extract_string(attributes, '$.llm.usage.total_tokens') as total_tokens
        FROM traces 
        WHERE name = 'LM.__call__' AND json_extract_string(attributes, '$.llm.usage.total_tokens') IS NOT NULL
    """).fetchall()

    if token_usage:
        for model, prompt_tokens, completion_tokens, total_tokens in token_usage:
            print(
                f"  {model}: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total tokens"
            )
    else:
        print("  No token usage data found (depends on LLM provider)")

    # Error analysis
    print("\n⚠️  Error Analysis:")
    errors = conn.execute("""
        SELECT 
            name,
            status_code,
            COUNT(*) as count
        FROM traces
        WHERE status_code != 'OK'
        GROUP BY name, status_code
    """).fetchall()

    if errors:
        for name, status_code, count in errors:
            print(f"  {name}: {count} spans with status {status_code}")
    else:
        print("  No errors found ✅")

    # Trace hierarchy
    print("\n🌳 Trace Hierarchy:")
    hierarchy = conn.execute("""
        SELECT 
            trace_id,
            name,
            parent_span_id,
            span_id,
            duration_ns / 1000000.0 as duration_ms
        FROM traces 
        ORDER BY trace_id, start_time
    """).fetchall()

    current_trace = None
    for trace_id, name, parent_span_id, span_id, duration_ms in hierarchy:
        if trace_id != current_trace:
            print(f"\n  Trace: {trace_id[:8]}...")
            current_trace = trace_id

        indent = "    " if parent_span_id else "  "
        print(f"{indent}└─ {name} ({duration_ms:.2f}ms)")

    conn.close()
    print(f"\n✅ Analysis complete for {trace_file}")


if __name__ == "__main__":
    analyze_traces()
