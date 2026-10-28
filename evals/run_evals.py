"""Score the eval set: retrieval recall@3 (search alone, no agent) and
tool-choice accuracy (the first tool the agent decides to call).

Run from the repo root: uv run python -m evals.run_evals [--retrieval-only]
"""

import json
import sys
import time
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.graph import SYSTEM_PROMPT, get_llm
from app.rag.search import search

DATASET = Path(__file__).parent / "dataset.jsonl"
# Gemini's free tier allows 5 chat requests per minute.
SECONDS_BETWEEN_CALLS = 13


def first_tool(question: str) -> str:
    # Only the agent node's first decision matters here, so call it once
    # instead of running the whole graph (tools + final reply).
    response = get_llm().invoke([SystemMessage(SYSTEM_PROMPT), HumanMessage(question)])
    return response.tool_calls[0]["name"] if response.tool_calls else "none"


def score_retrieval(cases: list[dict]) -> None:
    # Stock and handoff questions have no source document, so they only
    # count toward tool-choice accuracy.
    cases = [c for c in cases if c["expected_source"]]
    failures = []
    for case in cases:
        sources = [r["source_document"] for r in search(case["question"], k=3)]
        if case["expected_source"] not in sources:
            failures.append(f"  {case['question']} | expected {case['expected_source']}, got {sources}")
    hits = len(cases) - len(failures)
    print(f"Retrieval recall@3:   {hits}/{len(cases)} = {hits / len(cases):.0%}")
    print("\n".join(failures))


def score_tool_choice(cases: list[dict]) -> None:
    # Retrieval-only cases (expected_tool null) are left out to stay within
    # the free tier's daily chat quota.
    cases = [c for c in cases if c["expected_tool"]]
    failures = []
    for case in cases:
        tool = first_tool(case["question"])
        time.sleep(SECONDS_BETWEEN_CALLS)
        if tool != case["expected_tool"]:
            failures.append(f"  {case['question']} | expected {case['expected_tool']}, got {tool}")
    hits = len(cases) - len(failures)
    print(f"Tool-choice accuracy: {hits}/{len(cases)} = {hits / len(cases):.0%}")
    print("\n".join(failures))


def main() -> None:
    cases = [json.loads(line) for line in DATASET.read_text().splitlines() if line]
    # Retrieval runs first and prints on its own, so its result survives a
    # chat-quota error in the tool-choice half.
    score_retrieval(cases)
    if "--retrieval-only" not in sys.argv:
        score_tool_choice(cases)


if __name__ == "__main__":
    main()
