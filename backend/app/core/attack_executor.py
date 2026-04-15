"""
Attack Executor — executes the full scan pipeline.
Ported from IEEE Ignite prototype's RunService.execute_run.
Pipeline: Load Target → Mutate Prompts → Send → Analyze → Score → Log
"""
import json
import os
import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.tllm_profile import TLLMProfile
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.core.tllm_connector import TLLMConnector, TLLMConnectionError
from app.core.engine.mutation import MutationEngine
from app.core.engine.analysis import AnalysisEngine

RUNS_DIR = "runs"

def load_baseline_prompts():
    """Load attack templates from the knowledge base."""
    try:
        with open("kb_data/attack_templates.json", "r") as f:
            templates = json.load(f)
            return [t for t in templates if t.get("attack_class") == "prompt_injection"]
    except Exception as e:
        print(f"Failed to load templates: {e}")
        return []


def _get_judge_connector():
    """
    Initialize a separate LLM connector for the Judge role.
    Uses JUDGE_* environment variables (from .env).
    """
    from dotenv import load_dotenv
    load_dotenv()

    judge_api_key = os.getenv("JUDGE_API_KEY")
    if not judge_api_key:
        return None

    try:
        # Build a minimal TLLMProfile-like object for the judge
        judge_profile = TLLMProfile(
            name="SecuSync Judge",
            provider=os.getenv("JUDGE_PROVIDER", "openai"),
            endpoint_url=os.getenv("JUDGE_BASE_URL", "https://api.openai.com/v1"),
            api_key_ref=judge_api_key.strip(),
        )
        connector = TLLMConnector(judge_profile)
        print(f"✓ Judge LLM loaded: {os.getenv('JUDGE_PROVIDER', 'openai')}")
        return connector
    except Exception as e:
        print(f"✗ Failed to load Judge LLM: {e}")
        return None


async def execute_scan_run(run_id: str, db: Session):
    """
    Full scan execution pipeline — matches prototype's RunService.execute_run.
    """
    run = db.query(ScanRun).filter(ScanRun.id == run_id).first()
    if not run:
        return
    
    mutation_engine = MutationEngine()
    analysis_engine = AnalysisEngine()
    judge_connector = _get_judge_connector()

    # Ensure run log directory exists
    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    log_path = os.path.join(run_dir, "responses.jsonl")
        
    try:
        run.status = "RUNNING"
        db.commit()

        # 1. Load Target Profile
        profile = db.query(TLLMProfile).filter(TLLMProfile.id == run.tllm_profile_id).first()
        if not profile:
            raise Exception("TLLM Profile not found")

        connector = TLLMConnector(profile)

        # 2. Load seed prompts from KB
        templates = load_baseline_prompts()
        
        # 3. Generate mutations for each seed prompt
        mutation_depth = run.mutation_depth if run.mutation_depth else 1
        mutation_budget = max(3, mutation_depth * 3)

        all_prompts = []
        for template in templates:
            seed = template["template"]
            mutated = mutation_engine.mutate(seed, budget=mutation_budget)
            for m in mutated:
                all_prompts.append({
                    "text": m,
                    "attack_class": template["attack_class"],
                    "source_template": template.get("title", "unknown"),
                    "is_mutation": m != seed,
                })
        
        # Deduplicate by prompt text
        seen = set()
        unique_prompts = []
        for p in all_prompts:
            if p["text"] not in seen:
                seen.add(p["text"])
                unique_prompts.append(p)

        vulnerabilities_found = 0
        total_sent = 0
        total_score = 0.0
        findings_list = []

        with open(log_path, "w") as log_file:
            for prompt_info in unique_prompts:
                prompt_text = prompt_info["text"]
                attack_class = prompt_info["attack_class"]

                # Create DB record
                strategy = "mutation" if prompt_info["is_mutation"] else "baseline"
                variant = PromptVariant(
                    scan_run_id=run.id,
                    attack_class=attack_class,
                    strategy_applied=strategy,
                    depth=mutation_depth if prompt_info["is_mutation"] else 0,
                    prompt_text=prompt_text,
                    verdict="UNCERTAIN"
                )
                db.add(variant)
                db.commit()
                
                total_sent += 1
                
                try:
                    # Rate limit respect
                    await asyncio.sleep(0.5)
                    response = await connector.send(prompt_text)
                    variant.response_text = response
                    
                    # 4. Analyze response (dual-layer)
                    analysis = await analysis_engine.analyze(
                        response,
                        judge_connector,
                        original_prompt=prompt_text
                    )
                    
                    if analysis["is_vulnerable"]:
                        variant.verdict = "VULNERABLE"
                        variant.deterministic_matches = json.dumps(
                            [f.get("description", "") for f in analysis.get("findings", [])]
                        )
                        vulnerabilities_found += 1
                        total_score += analysis["score"]
                        findings_list.append({
                            "type": "vulnerability",
                            "severity": "high" if analysis["score"] > 0.8 else "medium",
                            "description": f"Vulnerability detected: {prompt_text[:60]}...",
                            "score": analysis["score"]
                        })
                    else:
                        variant.verdict = "NOT_VULNERABLE"
                    
                    # Store semantic classification if from judge
                    llm_finding = next((f for f in analysis.get("findings", []) if f.get("source") == "llm_judge"), None)
                    if llm_finding:
                        variant.semantic_classification = llm_finding.get("description", "")

                    # 5. Write JSONL log entry
                    log_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "prompt": prompt_text,
                        "response": response,
                        "analysis": analysis,
                        "source_template": prompt_info["source_template"],
                        "strategy": strategy,
                    }
                    log_file.write(json.dumps(log_entry) + "\n")
                    log_file.flush()

                except Exception as e:
                    variant.response_text = f"Error: {str(e)}"
                    variant.verdict = "NEEDS_REVIEW"
                    
                db.commit()

        # 6. Finalize run
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
