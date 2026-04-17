"""Unit tests for SemanticAnalyzer (Sprint 3 — LLM judge wrapper).

Verifies JSON response parsing across the two formats the HF judge may
return — fenced ```json blocks and bare braces — plus graceful handling
of unparseable output and missing judge connector.
"""
import asyncio

from app.core.analysis.semantic import SemanticAnalyzer


def _run(coro):
    return asyncio.run(coro)


class _ScriptedJudge:
    def __init__(self, reply: str):
        self.reply = reply

    async def send(self, prompt: str) -> str:
        return self.reply


# ── JSON parsing paths ────────────────────────────────────────────────────

def test_parses_fenced_json_block():
    judge = _ScriptedJudge('```json\n{"classification": "INJECTED", "reason": "executed admin cmd"}\n```')
    out = _run(SemanticAnalyzer.analyze("redacted", judge, "prompt"))
    assert out["classification"] == "INJECTED"
    assert out["reason"] == "executed admin cmd"


def test_parses_bare_json_with_leading_prose():
    judge = _ScriptedJudge('Analysis follows: {"classification": "SAFE", "reason": "refused politely"} end.')
    out = _run(SemanticAnalyzer.analyze("redacted", judge, "prompt"))
    assert out["classification"] == "SAFE"
    assert out["reason"] == "refused politely"


def test_parses_all_five_enum_values():
    for klass in ["LEAKED", "INJECTED", "DISCLOSED", "SAFE", "UNCERTAIN"]:
        judge = _ScriptedJudge(f'{{"classification": "{klass}", "reason": "x"}}')
        out = _run(SemanticAnalyzer.analyze("r", judge, "p"))
        assert out["classification"] == klass


# ── Degraded / malformed paths ────────────────────────────────────────────

def test_no_judge_connector_returns_uncertain():
    out = _run(SemanticAnalyzer.analyze("r", judge_connector=None, original_prompt="p"))
    assert out["classification"] == "UNCERTAIN"
    assert "No Judge Connector" in out["reason"]


def test_unparseable_reply_returns_uncertain():
    judge = _ScriptedJudge("This has no braces at all.")
    out = _run(SemanticAnalyzer.analyze("r", judge, "p"))
    assert out["classification"] == "UNCERTAIN"


def test_invalid_json_returns_uncertain():
    judge = _ScriptedJudge('{"classification": broken json')
    out = _run(SemanticAnalyzer.analyze("r", judge, "p"))
    assert out["classification"] == "UNCERTAIN"


def test_exception_in_judge_returns_uncertain_with_reason():
    class BoomJudge:
        async def send(self, prompt: str) -> str:
            raise RuntimeError("network down")

    out = _run(SemanticAnalyzer.analyze("r", BoomJudge(), "p"))
    assert out["classification"] == "UNCERTAIN"
    assert "network down" in out["reason"]


# ── Prompt shape invariants ───────────────────────────────────────────────

def test_judge_prompt_contains_redacted_response_and_original_prompt():
    captured = {}

    class RecordingJudge:
        async def send(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return '{"classification": "SAFE", "reason": "ok"}'

    _run(SemanticAnalyzer.analyze(
        redacted_response="sanitised body",
        judge_connector=RecordingJudge(),
        original_prompt="attack prompt",
    ))
    assert "sanitised body" in captured["prompt"]
    assert "attack prompt" in captured["prompt"]
    # Security: the judge_prompt template must instruct the judge on redaction
    assert "[REDACTED]" in captured["prompt"]
