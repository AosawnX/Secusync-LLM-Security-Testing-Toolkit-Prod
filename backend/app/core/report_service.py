import os
import io
import zipfile
import json
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.core.attack_executor import _get_judge_connector

RUNS_DIR = "runs"
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Ensure templates dir exists
os.makedirs(TEMPLATES_DIR, exist_ok=True)

class ReportService:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    def _convert_html_to_pdf(self, source_html, output_filename):
        with open(output_filename, "wb") as result_file:
            pisa_status = pisa.CreatePDF(
                source_html,
                dest=result_file
            )
        return pisa_status.err

    def _extract_findings(self, variants):
        findings = []
        for v in variants:
            if v.verdict == "VULNERABLE":
                matches = "Details not recorded"
                if v.deterministic_matches:
                    try:
                         # deterministic_matches is a JSON list of matches
                         matches = ", ".join(json.loads(v.deterministic_matches))
                    except:
                         matches = v.deterministic_matches

                findings.append({
                    "type": "Prompt Injection Vulnerability",
                    "severity": "high" if "sk-" in str(v.response_text) else "medium",
                    "description": matches[:200],
                    "prompt": v.prompt_text
                })
        return findings

    async def generate_technical_report(self, run: ScanRun, variants: list[PromptVariant]) -> str:
        findings = self._extract_findings(variants)
        findings_text = "\n".join([f"- [{f['severity']}] {f['description']}" for f in findings])
        
        judge_connector = _get_judge_connector()
        technical_summary = "No findings to analyze or Judge LLM not configured."
        
        if findings and judge_connector:
            try:
                technical_prompt = f"""
                You are a Senior Security Engineer.
                Analyze the following vulnerability findings from a technical perspective.
                
                1. Explain the ROOT CAUSE of the vulnerabilities (e.g., Prompt Injection, Information Leakage).
                2. Provide specific REMEDIATION steps for developers.
                3. Explain WHY these are dangerous.
                
                Findings:
                {findings_text}
                """
                technical_summary = await judge_connector.send(technical_prompt)
            except Exception as e:
                technical_summary = f"Could not generate insights: {e}"

        template = self.env.get_template("report.html")
        html_content = template.render(
            run=run, 
            report_type="Technical Report",
            technical_summary=technical_summary,
            is_technical=True,
            is_executive=False,
            findings=findings
        )
        
        run_dir = os.path.join(RUNS_DIR, run.id)
        os.makedirs(run_dir, exist_ok=True)
        report_path = os.path.join(run_dir, "technical_report.pdf")
        
        self._convert_html_to_pdf(html_content, report_path)
        return report_path

    async def generate_executive_report(self, run: ScanRun, variants: list[PromptVariant]) -> str:
        findings = self._extract_findings(variants)
        findings_text = "\n".join([f"- [{f['severity']}] {f['description']}" for f in findings])
        
        judge_connector = _get_judge_connector()
        executive_summary = "No findings to summarize or Judge LLM not configured."
        
        if findings and judge_connector:
            try:
                summary_prompt = f"""
                You are a Cyber Security Executive Consultant. 
                Summarize the following security findings for a C-Level Executive.
                Focus on Business Impact, Risk Level, and Strategic Recommendations.
                Keep it professional, concise, and actionable.

                Findings:
                {findings_text}
                """
                executive_summary = await judge_connector.send(summary_prompt)
            except Exception as e:
                executive_summary = f"Could not generate summary: {e}"

        template = self.env.get_template("report.html")
        html_content = template.render(
            run=run, 
            report_type="Executive Report",
            executive_summary=executive_summary,
            is_executive=True,
            is_technical=False,
            findings=findings
        )
        
        run_dir = os.path.join(RUNS_DIR, run.id)
        os.makedirs(run_dir, exist_ok=True)
        report_path = os.path.join(run_dir, "executive_report.pdf")
        
        self._convert_html_to_pdf(html_content, report_path)
        return report_path

    def generate_poc_bundle(self, run: ScanRun, variants: list[PromptVariant]) -> str:
        findings = self._extract_findings(variants)
        if not findings:
            return None

        guide_content = f"# Reproduction Guide for Run {run.id}\n\n## Target Information\n- **Target ID**: {run.tllm_profile_id}\n- **Date**: {run.created_at}\n\n## Vulnerabilities Found\n"
        
        for i, finding in enumerate(findings):
             guide_content += f"\n### {i+1}. {finding['type']}\n"
             guide_content += f"- **Severity**: {finding['severity']}\n"
             guide_content += f"- **Prompt**: `{finding['prompt']}`\n"
        
        guide_content += "\n## Reproduction Steps\n1. Configure the target system as per the profile.\n2. Send the prompts listed above.\n3. Observe the response for leaked information.\n"
        guide_content += "\n\n**CONFIDENTIALITY NOTICE:** This information is intended for authorized security personnel only."

        run_dir = os.path.join(RUNS_DIR, run.id)
        os.makedirs(run_dir, exist_ok=True)
        zip_path = os.path.join(run_dir, "poc_bundle.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("Reproduction_Guide.md", guide_content)
            
        return zip_path
