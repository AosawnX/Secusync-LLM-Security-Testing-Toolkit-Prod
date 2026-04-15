import json
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.tllm_profile import TLLMProfile
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.core.tllm_connector import TLLMConnector, TLLMConnectionError
from app.core.analysis.deterministic import DeterministicAnalyzer

def load_baseline_prompts():
    try:
        with open("kb_data/attack_templates.json", "r") as f:
            templates = json.load(f)
            return [t for t in templates if t.get("attack_class") == "prompt_injection"]
    except Exception as e:
        print(f"Failed to load templates: {e}")
        return []

async def execute_scan_run(run_id: str, db: Session):
    run = db.query(ScanRun).filter(ScanRun.id == run_id).first()
    if not run:
        return
        
    try:
        run.status = "RUNNING"
        db.commit()

        profile = db.query(TLLMProfile).filter(TLLMProfile.id == run.tllm_profile_id).first()
        if not profile:
            raise Exception("TLLM Profile not found")

        connector = TLLMConnector(profile)
        templates = load_baseline_prompts()
        
        vulnerabilities_found = 0
        total_sent = 0

        for template in templates:
            prompt_text = template["template"]
            attack_class = template["attack_class"]
            
            variant = PromptVariant(
                scan_run_id=run.id,
                attack_class=attack_class,
                prompt_text=prompt_text,
                verdict="UNCERTAIN"
            )
            db.add(variant)
            db.commit()
            
            total_sent += 1
            
            try:
                # Small delay to respect rate limits if any
                await asyncio.sleep(0.5)
                response = await connector.send(prompt_text)
                variant.response_text = response
                
                matches = DeterministicAnalyzer.analyze(response)
                if matches:
                    variant.verdict = "VULNERABLE"
                    variant.deterministic_matches = json.dumps(matches)
                    vulnerabilities_found += 1
                else:
                    variant.verdict = "NOT_VULNERABLE"
                    
            except Exception as e:
                variant.response_text = f"Error: {str(e)}"
                variant.verdict = "NEEDS_REVIEW"
                
            db.commit()

        run.status = "COMPLETED"
        run.completed_at = datetime.utcnow()
        run.total_prompts_sent = total_sent
        run.vulnerabilities_found = vulnerabilities_found
        db.commit()
        
    except Exception as e:
        print(f"Scan failed: {str(e)}")
        run.status = "FAILED"
        run.completed_at = datetime.utcnow()
        db.commit()
