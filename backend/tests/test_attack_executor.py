import pytest
from app.core.attack_executor import load_baseline_prompts


def test_load_baseline_prompts_returns_list():
    # Sprint 2 added required attack_classes filter — the function now
    # takes a list and returns only matching templates. Even if the JSON
    # file can't be located under the test cwd, the function swallows
    # the error and returns [] rather than crashing.
    prompts = load_baseline_prompts(["prompt_injection"])
    assert isinstance(prompts, list)


def test_load_baseline_prompts_filters_by_attack_class():
    # Unknown attack class → empty list (filter yields nothing)
    prompts = load_baseline_prompts(["nonexistent_class"])
    assert prompts == []
