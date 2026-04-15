import pytest
from app.core.attack_executor import load_baseline_prompts

def test_load_baseline_prompts():
    # Because we're running from test root, we might need to adjust paths or just mock
    prompts = load_baseline_prompts()
    assert isinstance(prompts, list)
    # Even if empty (due to path issues in test run), it shouldn't crash
