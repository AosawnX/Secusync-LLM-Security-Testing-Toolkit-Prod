"""Unit tests for Redactor (Sprint 3 — secret sanitisation).

CRITICAL SECURITY CONTRACT: the Redactor stands between captured TLLM
responses and any external service (the semantic judge) or persistent
export (the Technical PDF, PoC bundle). A regression here would leak raw
secrets outside local scope, violating PRD §4.5 and §7.

Every failure path is treated as a security incident and must remain
tested forever. Do not delete these tests.
"""
from app.core.utils.redactor import Redactor


# ── Each pattern redacts its secret ───────────────────────────────────────

def test_openai_key_redacted():
    raw = "Token: sk-ABCDEF1234567890abcdef1234"
    out = Redactor.sanitize(raw)
    assert "sk-ABCDEF" not in out
    assert "[REDACTED]" in out


def test_google_key_redacted():
    raw = "API: AIzaSyBoo1hJbp3_ZbnLlCTcl5t_1SNmhoAOT68"
    out = Redactor.sanitize(raw)
    assert "AIzaSyBoo" not in out
    assert "[REDACTED]" in out


def test_bearer_token_redacted():
    raw = "Authorization: Bearer eyJhbGci.payload.sig=="
    out = Redactor.sanitize(raw)
    assert "eyJhbGci" not in out
    assert "[REDACTED]" in out


def test_password_redacted_keeps_context_label():
    raw = "Login: password: hunter2"
    out = Redactor.sanitize(raw)
    # Intentional behaviour: keep the word "password:" so the judge still
    # has context, but the value is scrubbed.
    assert "hunter2" not in out
    assert "password:" in out.lower()
    assert "[REDACTED]" in out


def test_mock_secure_flag_redacted():
    raw = "Captured flag: REF-0042-SECURE"
    out = Redactor.sanitize(raw)
    assert "REF-0042-SECURE" not in out
    assert "[REDACTED]" in out


# ── Combined / realistic inputs ───────────────────────────────────────────

def test_multiple_secrets_all_redacted_in_one_pass():
    raw = (
        "Here are creds:\n"
        "  sk-ABCDEF1234567890abcdef1234\n"
        "  AIzaSyBoo1hJbp3_ZbnLlCTcl5t_1SNmhoAOT68\n"
        "  Bearer eyJhbGci.payload.sig==\n"
        "  password: p@55word\n"
        "  flag REF-9999-SECURE"
    )
    out = Redactor.sanitize(raw)
    # Every raw secret must disappear
    assert "sk-ABCDEF" not in out
    assert "AIzaSyBoo" not in out
    assert "eyJhbGci" not in out
    assert "p@55word" not in out
    assert "REF-9999-SECURE" not in out
    # And [REDACTED] must appear at least once per secret
    assert out.count("[REDACTED]") >= 5


def test_benign_text_unchanged():
    raw = "The weather is sunny today and tomorrow."
    assert Redactor.sanitize(raw) == raw


# ── Edge cases ────────────────────────────────────────────────────────────

def test_empty_string_returns_empty():
    assert Redactor.sanitize("") == ""


def test_none_returns_empty_string():
    # Contract: Redactor must never raise on falsy input — the executor
    # passes response.text which can be None when the TLLM call fails.
    assert Redactor.sanitize(None) == ""


def test_secret_in_middle_of_sentence_redacted():
    raw = "Before text sk-ABCDEF1234567890abcdef1234 and after text."
    out = Redactor.sanitize(raw)
    assert "sk-ABCDEF" not in out
    assert "Before text" in out
    assert "and after text." in out


# ── Security invariant: idempotence ───────────────────────────────────────

def test_redaction_is_idempotent():
    raw = "sk-ABCDEF1234567890abcdef1234 and AIzaSyBoo1hJbp3_ZbnLlCTcl5t_1SNmhoAOT68"
    once = Redactor.sanitize(raw)
    twice = Redactor.sanitize(once)
    assert once == twice, "Running sanitize twice must not re-process [REDACTED]"
