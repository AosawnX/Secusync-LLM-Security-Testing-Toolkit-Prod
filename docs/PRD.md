# SECUSYNC — Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** April 2026  
**Author:** Syed Abdullah Shah (01-134222-143)  
**Supervisor:** Mr. Raja Muhammad Shamayel Ullah  
**Institution:** Bahria University, Islamabad — Department of Computer Science  

---

## 1. Product Overview

SECUSYNC is a full-stack, web-based LLM Security Testing Toolkit. It enables testers, researchers, and developers to systematically discover, reproduce, and report runtime vulnerabilities in LLM-integrated applications (referred to throughout this document as **TLLMs** — Target LLMs).

The product must be demo-ready and defense-ready by **April 2026**, capable of producing benchmarked attack success rates, reproducible proof-of-concept (PoC) artefacts, and a side-by-side comparison against HOUYI and GPTFuzzer.

---

## 2. Goals and Non-Goals

### Goals
- Provide a structured, repeatable, mutation-driven pipeline for probing TLLMs
- Support four attack classes: Prompt Injection, System Prompt Leakage, File Poisoning, Sensitive Information Disclosure
- Produce two-layer reports: executive summaries and technical reports with PoC bundles
- Be extensible for new attack classes without core rewrites
- Be demonstrable against live or local TLLMs during the defense

### Non-Goals
- Automated remediation or patching of TLLMs
- Training-time data poisoning or side-channel attacks
- Denial-of-service (DoS) testing
- Multi-tenant / cloud-scaled deployments (Kubernetes, autoscaling)
- Reinforcement learning-based mutation optimization (future work)
- Testing of unauthorized, unapproved third-party systems

---

## 3. Users and Personas

| Persona | Description | Primary Use |
|---|---|---|
| Security Researcher | Academic or professional red-teamer | Runs adversarial campaigns, exports PoC bundles |
| Developer / Builder | Developer integrating LLMs into apps | Validates their app before deployment |
| Defense Panel / Supervisor | FYP evaluator | Views dashboard, live demo, and final reports |

---

## 4. Feature Requirements

### 4.1 TLLM Configuration Module
- User can define a target LLM profile including:
  - API provider: OpenAI, Anthropic (Claude), Local/Ollama, or Custom REST endpoint
  - System prompt (optional)
  - Whether the target has RAG integration
  - Whether the target accepts document uploads (file poisoning surface)
  - Whether the target accepts multimodal inputs
  - Authentication credentials (API key, stored securely, never logged)
- Multiple TLLM profiles can be saved, named, and reused

### 4.2 Attack Class Selection
- User selects one or more attack classes to execute:
  - **Prompt Injection** — override system instructions via user turn
  - **System Prompt Leakage** — extract the hidden system prompt
  - **File Poisoning** — indirect injection via malicious uploaded documents
  - **Sensitive Information Disclosure** — extract PII, API keys, secrets
- Each attack class has a curated baseline prompt library

### 4.3 Mutation Engine
- Takes a baseline prompt and iteratively mutates it using:
  - **Paraphrasing** — semantic rewording via HuggingFace inference endpoint
  - **Encoding / Format Switching** — Base64, ROT13, leetspeak, Unicode obfuscation
  - **Language Switching** — translate payload to another language then back
  - **Multi-Step Chaining** — split attack across multiple conversation turns
- Mutation depth (number of iterations) is configurable per run
- All generated variants are stored with parent-child lineage for traceability
- The engine uses a FAISS vector store to avoid regenerating near-duplicate prompts

### 4.4 Attack Execution Engine
- Sends mutated prompts to the configured TLLM endpoint
- Captures full request + response with timestamps
- Handles rate limiting and retries gracefully
- Stores raw outputs locally; never re-sends raw outputs to external services
- Configurable delay between requests to respect TLLM rate limits

### 4.5 Hybrid Analysis Module
- **Deterministic Layer:** regex-based detectors for:
  - API keys / secrets (patterns: `sk-`, `Bearer`, `AIza`, etc.)
  - Prompt markers / system prompt fragments
  - PII patterns (email, phone, SSN-like patterns)
- **Semantic Layer:** locally-routed LLM judge via HuggingFace Inference Endpoint
  - Classifies output as: `LEAKED | INJECTED | DISCLOSED | BENIGN | UNCERTAIN`
  - Only processes redacted/sanitized versions of outputs — no raw secrets leave local scope
- **FAISS Corroboration:** similarity search against known vulnerability pattern library
- Final verdict per prompt variant: `VULNERABLE | NOT_VULNERABLE | NEEDS_REVIEW`

### 4.6 Knowledge Base (RAG)
- FAISS-backed vector store seeded with:
  - Curated attack templates categorized by attack class
  - Historical successful exploit patterns
  - OWASP LLM Top 10 reference entries
- Used by the Mutation Engine to guide prompt generation
- Used by the Analysis Module to corroborate findings
- Updatable: new entries can be added via admin panel or bulk import

### 4.7 Report Generator
- **Executive Report (PDF):**
  - Summary of vulnerabilities found
  - Risk rating per finding (Critical / High / Medium / Low)
  - Business impact description
  - Recommended remediations
- **Technical Report (PDF):**
  - Full logs per attack run
  - Reproducible PoC artefacts (prompt + TLLM config + expected response)
  - Redacted outputs (secrets replaced with `[REDACTED]`)
  - Diff view: baseline prompt vs successful mutant
- Both reports branded with SECUSYNC header
- Reports downloadable from the dashboard per run

### 4.8 Web Dashboard (Frontend)
- **Pages / Views:**
  - Home / Dashboard: recent runs, quick stats (total runs, vulnerabilities found)
  - New Scan: TLLM configuration + attack class selection + mutation settings
  - Live Run View: real-time progress of active scan (WebSocket stream)
  - Run History: list of all past runs with status and summary
  - Run Detail: per-run breakdown — prompt variants, verdicts, analysis trace
  - Knowledge Base Manager: browse/add/delete KB entries
  - Reports: download executive and technical PDF per run
  - Settings: global configuration (API keys, analysis model endpoint)
- **Tech:** React (Vite) + TypeScript + TailwindCSS
- **State Management:** React Query for server state, Zustand for UI state
- **Real-time:** WebSocket connection to backend for live run streaming

### 4.9 Backend API
- **Tech:** Python 3.10+ with FastAPI
- **Key endpoints:**
  - `POST /tllm/profiles` — create/update TLLM profile
  - `POST /scans/start` — initiate a scan run
  - `GET /scans/{run_id}/stream` — WebSocket stream for live updates
  - `GET /scans/{run_id}/results` — full results for a completed run
  - `GET /reports/{run_id}/executive` — download executive PDF
  - `GET /reports/{run_id}/technical` — download technical PDF
  - `GET /kb/entries` — list knowledge base entries
  - `POST /kb/entries` — add new KB entry
- **Database:** SQLite (development) → PostgreSQL-compatible schema (production-ready)
- **Task Queue:** background tasks via FastAPI BackgroundTasks (or Celery if needed)

---

## 5. Attack Success Metrics (Defense Requirements)

The following metrics must be measurable and presentable at defense:

| Metric | Description |
|---|---|
| Attack Success Rate (ASR) | % of mutant prompts that achieved a successful exploit per attack class |
| Mutation Efficiency | Average number of mutations needed before a successful exploit |
| Detection Precision | % of flagged outputs that are true positives (manual validation) |
| Detection Recall | % of actual vulnerabilities that were flagged |
| Coverage | Number of distinct vulnerability types detected across test runs |
| Baseline vs Mutant Delta | ASR of baseline prompts vs mutated prompts (shows mutation value) |

These metrics must be visible in the dashboard and included in the technical report.

---

## 6. Comparison Benchmarks (Defense Requirements)

SECUSYNC must include a documented comparison against:
- **HOUYI** (Liu et al., 2024) — black-box three-part prompt injection framework
- **GPTFuzzer** (Zhang et al., 2024) — fuzzing-based vulnerability detection

Comparison dimensions: mutation strategy, semantic analysis, runtime traceability, reproducibility, attack class coverage.

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Security | All API keys encrypted at rest; raw TLLM outputs never sent to external services |
| Ethical compliance | Only tested against sandbox TLLMs or explicitly authorized endpoints |
| Reproducibility | Every finding must include a self-contained PoC bundle re-runnable by a third party |
| Modularity | Each module (Mutation, Analysis, Reporting) must be independently testable |
| Auditability | All scan runs logged with full request/response trace and timestamps |
| Performance | A 20-prompt scan run should complete within 5 minutes on standard hardware |

---

## 8. Constraints

- No GPU required — all local model inference routed through HuggingFace Inference Endpoints
- No cloud deployment required — must run fully locally on a single machine
- Defense demo must work offline-capable (local TLLM via Ollama as fallback)
- No RL-based mutation in this version

---

## 9. Acceptance Criteria

The product is considered complete when:

1. All 4 attack classes produce detectable, reproducible findings against a test TLLM
2. The Mutation Engine demonstrably improves ASR over baseline (raw) prompts
3. Executive and Technical PDF reports are generated per run without errors
4. The Web UI allows a full scan cycle without touching the terminal
5. Benchmarked metrics (Section 5) are displayed in the dashboard
6. The HOUYI/GPTFuzzer comparison table is documented in the technical report
7. All modules pass their unit tests with ≥ 80% coverage
