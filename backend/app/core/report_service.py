import os
import io
import zipfile
import json
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.core.attack_executor import _get_judge_connector
from app.core.utils.redactor import Redactor

RUNS_DIR = "runs"
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Ensure templates dir exists
os.makedirs(TEMPLATES_DIR, exist_ok=True)

_ATTACK_CLASS_LABELS = {
    "prompt_injection": "Prompt Injection Vulnerability",
    "system_prompt_leakage": "System Prompt Leakage",
    "file_poisoning": "File Poisoning (Indirect Injection)",
    "sensitive_info_disclosure": "Sensitive Information Disclosure",
}

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
        """Extract VULNERABLE findings, redacting secrets from response text.

        PRD §4.7 requires that raw secrets in responses are replaced with
        [REDACTED] before they appear in any report artefact.  We run the
        Redactor over both the response text and the description string so
        the PDF never contains a live credential.
        """
        findings = []
        for v in variants:
            if v.verdict == "VULNERABLE":
                matches = "Details not recorded"
                if v.deterministic_matches:
                    try:
                        matches = ", ".join(json.loads(v.deterministic_matches))
                    except Exception:
                        matches = v.deterministic_matches

                # Redact secrets from the response before including in report
                raw_response = v.response_text or ""
                redacted_response = Redactor.sanitize(raw_response)

                severity = "critical" if any(
                    kw in raw_response for kw in ("sk-", "Bearer ", "AIza", "password")
                ) else "high" if v.attack_class in ("system_prompt_leakage", "sensitive_info_disclosure") else "medium"

                findings.append({
                    "type": _ATTACK_CLASS_LABELS.get(v.attack_class, "Vulnerability"),
                    "attack_class": v.attack_class,
                    "severity": severity,
                    "description": Redactor.sanitize(matches[:300]),
                    "prompt": v.prompt_text,
                    "response": redacted_response[:500],
                    "strategy": v.strategy_applied or "baseline",
                    "depth": v.depth,
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

        guide_content = (
            f"# SECUSYNC — PoC Reproduction Bundle\n\n"
            f"## Scan Metadata\n"
            f"- **Run ID**: {run.id}\n"
            f"- **Target Profile**: {run.tllm_profile_id}\n"
            f"- **Date**: {run.created_at}\n"
            f"- **Attack Classes**: {run.attack_classes}\n\n"
            f"## Vulnerabilities Found ({len(findings)})\n"
        )
        for i, finding in enumerate(findings):
            guide_content += (
                f"\n### {i+1}. {finding['type']}\n"
                f"- **Severity**: {finding['severity'].upper()}\n"
                f"- **Attack Class**: {finding.get('attack_class', 'unknown')}\n"
                f"- **Mutation Strategy**: {finding.get('strategy', 'baseline')}\n"
                f"- **Mutation Depth**: {finding.get('depth', 0)}\n"
                f"- **Prompt**:\n\n```\n{finding['prompt']}\n```\n\n"
                f"- **Response (redacted)**:\n\n```\n{finding.get('response', '[no response]')}\n```\n"
            )
        guide_content += (
            "\n## Reproduction Steps\n"
            "1. Configure the target system as per the TLLM profile.\n"
            "2. Send each prompt above to the target endpoint.\n"
            "3. Observe the response for leaked information or injected behaviour.\n"
            "4. Compare against the VULNERABLE verdict criteria in the Technical Report.\n\n"
            "---\n"
            "**CONFIDENTIALITY NOTICE:** This bundle is intended for authorized security "
            "personnel only. Do not share or use against unauthorized systems.\n"
            "\n*Generated by SECUSYNC v1.0 — LLM Security Testing Toolkit*\n"
        )

        run_dir = os.path.join(RUNS_DIR, run.id)
        os.makedirs(run_dir, exist_ok=True)
        zip_path = os.path.join(run_dir, "poc_bundle.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("Reproduction_Guide.md", guide_content)
            
        return zip_path
