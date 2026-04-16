"""Attack Executor — orchestrates a scan run end-to-end.

Pipeline (architecture.md §3.3):
  Load Target → Load baselines → Mutate (6 strategies, depth-N, FAISS dedup)
  → Send to TLLM → Hybrid Analyze (redact → regex → semantic) → Persist verdict
"""
import json
import os
import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.tllm_profile import TLLMProfile
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.core.tllm_connector import TLLMConnector
from app.core.engine.mutation import MutationEngine, STRATEGIES
from app.core.analysis.hybrid import HybridAnalysisEngine

RUNS_DIR = "runs"


def load_baseline_prompts(attack_classes: list[str]) -> list[dict]:
    try:
        with open("kb_data/attack_templates.json", "r", encoding="utf-8") as f:
            templates = json.load(f)
    except Exception as e:
        print(f"Failed to load templates: {e}")
        return []
    return [t for t in templates if t.get("attack_class") in attack_classes]


def _get_judge_connector():
    from dotenv import load_dotenv
    load_dotenv()
    judge_api_key = os.getenv("JUDGE_API_KEY")
    if not judge_api_key:
        return None
    try:
        judge_profile = TLLMProfile(
            name="SecuSync Judge",
            provider=os.getenv("JUDGE_PROVIDER", "openai"),
            endpoint_url=os.getenv("JUDGE_BASE_URL", "https://api.openai.com/v1"),
            api_key_ref=judge_api_key.strip(),
        )
        return TLLMConnector(judge_profile)
    except Exception as e:
        print(f"Failed to load Judge LLM: {e}")
        return None


def _parse_list(value) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return [v.strip() for v in str(value).split(",") if v.strip()]


async def execute_scan_run(run_id: str, db: Session):
    run = db.query(ScanRun).filter(ScanRun.id == run_id).first()
    if not run:
        return

    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    log_path = os.path.join(run_dir, "responses.jsonl")

    try:
        run.status = "RUNNING"
        db.commit()

        profile = db.query(TLLMProfile).filter(TLLMProfile.id == run.tllm_profile_id).first()
        if not profile:
            raise Exception("TLLM Profile not found")

        connector = TLLMConnector(profile)
        judge_connector = _get_judge_connector()
        mutation_engine = MutationEngine()

        attack_classes = _parse_list(run.attack_classes) or ["prompt_injection"]
        requested_strategies = _parse_list(run.mutation_strategies)
        active_strategies = [s for s in requested_strategies if s in STRATEGIES]
        depth = run.mutation_depth if run.mutation_depth else 1

        templates = load_baseline_prompts(attack_classes)

        total_sent = 0
        vulnerabilities_found = 0

        with open(log_path, "w", encoding="utf-8") as log_file:
            for template in templates:
                baseline_text = template["template"]
                attack_class = template["attack_class"]
                source_title = template.get("title", "unknown")

                # Persist the baseline variant first — all mutants descend from it.
                baseline_variant = PromptVariant(
                    scan_run_id=run.id,
                    parent_id=None,
                    attack_class=attack_class,
                    strategy_applied="baseline",
                    depth=0,
                    prompt_text=baseline_text,
                    verdict="UNCERTAIN",
                )
                db.add(baseline_variant)
                db.commit()
                db.refresh(baseline_variant)

                variants_to_run: list[PromptVariant] = [baseline_variant]

                if active_strategies:
                    mutated = await mutation_engine.mutate(
                        baseline=baseline_text,
                        strategies=active_strategies,
                        depth=depth,
                    )
                    parent_map: dict[str, str] = {baseline_text: baseline_variant.id}
                    for mv in mutated:
                        parent_id = parent_map.get(mv.parent_text, baseline_variant.id)
                        row = PromptVariant(
                            scan_run_id=run.id,
                            parent_id=parent_id,
                            attack_class=attack_class,
                            strategy_applied=mv.strategy,
                            depth=mv.depth,
                            prompt_text=mv.text,
                            verdict="UNCERTAIN",
                        )
                        db.add(row)
                        db.commit()
                        db.refresh(row)
                        parent_map[mv.text] = row.id
                        variants_to_run.append(row)

                for variant in variants_to_run:
                    total_sent += 1
                    try:
                        await asyncio.sleep(0.5)
                        response = await connector.send(variant.prompt_text)
                        variant.response_text = response

                        analysis = await HybridAnalysisEngine.analyze(
                            raw_response=response,
                            judge_connector=judge_connector,
                            original_prompt=variant.prompt_text,
                            system_prompt=profile.system_prompt,
                        )
                        variant.verdict = analysis["verdict"]
                        variant.deterministic_matches = analysis["deterministic_matches"]
                        variant.semantic_classification = analysis["semantic_classification"]
                        if analysis["verdict"] == "VULNERABLE":
                            vulnerabilities_found += 1

                        log_file.write(json.dumps({
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "variant_id": variant.id,
                            "parent_id": variant.parent_id,
                            "strategy": variant.strategy_applied,
                            "depth": variant.depth,
                            "attack_class": variant.attack_class,
                            "source_template": source_title,
                            "prompt": variant.prompt_text,
                            "response": response,
                            "analysis": analysis,
                        }) + "\n")
                        log_file.flush()
                    except Exception as e:
                        variant.response_text = f"Error: {str(e)}"
                        variant.verdict = "NEEDS_REVIEW"
                    db.commit()

        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        run.total_prompts_sent = total_sent
        run.vulnerabilities_found = vulnerabilities_found
        db.commit()

    except Exception as e:
        print(f"Scan failed: {str(e)}")
        run.status = "FAILED"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
