# SECUSYNC — Software Product Report

**Project Title:** SECUSYNC: Detecting Runtime Vulnerabilities in LLM-Integrated Applications  
**Institution:** Bahria University, Islamabad — Department of Computer Science  
**Supervisor:** Mr. Raja Muhammad Shamayel Ullah  
**Authors:** Syed Abdullah Shah (01-134222-143) · Ahsan Rasheed (01-134222-019)  
**Version:** Living Document — updated at each SDLC phase  
**Final Submission:** April 2026

> **Maintenance Instruction (for AI Agent):**  
> This is a living document. After completing each SDLC phase/sprint, append the relevant section with actual outcomes, decisions, and measurements. Do NOT overwrite prior entries. Mark completed sections with ✅ and pending sections with 🔲.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Requirements Engineering](#3-requirements-engineering)
4. [System Design](#4-system-design)
5. [SDLC Process Model](#5-sdlc-process-model)
6. [Technology Selection & Trade-off Decisions](#6-technology-selection--trade-off-decisions)
7. [Sprint-by-Sprint Development Log](#7-sprint-by-sprint-development-log)
8. [Testing & Validation](#8-testing--validation)
9. [Security & Ethical Considerations](#9-security--ethical-considerations)
10. [Benchmarking & Experimental Results](#10-benchmarking--experimental-results)
11. [Comparison with Related Systems](#11-comparison-with-related-systems)
12. [Known Limitations & Future Work](#12-known-limitations--future-work)
13. [Project Retrospective](#13-project-retrospective)
14. [References](#14-references)

---

## 1. Executive Summary

🔲 *(To be completed at project completion — Sprint 7)*

SECUSYNC is a full-stack, web-based LLM Security Testing Toolkit designed to systematically detect, reproduce, and report runtime vulnerabilities in LLM-integrated applications. The system targets four vulnerability classes: Prompt Injection, System Prompt Leakage, File Poisoning, and Sensitive Information Disclosure.

The toolkit implements a four-stage pipeline: TLLM Characterization → Mutation Engine → Hybrid Analysis → Automated Reporting. It is built on a Python FastAPI backend with a React/TypeScript frontend and a FAISS-backed knowledge base.

**Key outcomes (to be filled):**
- Attack Success Rate (ASR) across 4 attack classes: `[TBD]`
- Mutation improvement over baseline: `[TBD]`
- Total vulnerabilities detected in test harness: `[TBD]`
- Test coverage achieved: `[TBD]`

---

## 2. Problem Statement

### 2.1 Context

Large Language Models are increasingly embedded into production applications — chatbots, RAG-based document assistants, multimodal enterprise tools. Their integration often outpaces security evaluation, creating an attack surface that is novel, poorly understood, and inadequately tested by existing tools.

### 2.2 Core Problem

Existing security testing approaches for LLM-integrated applications are:
- **Ad hoc** — relying on heuristic prompts and trial-and-error, producing non-reproducible results
- **Narrow** — most tools focus on either adversarial generation or fuzzing, but not both with semantic analysis
- **Non-reproducible** — findings are difficult to reproduce or share as PoC bundles
- **Poorly instrumented** — lacking metrics to benchmark attack success or compare defenses

This is confirmed by the OWASP Top 10 for LLMs (2025), which identifies prompt injection as the most critical risk, and by large-scale studies (HackerOne, 2024) showing that prompt injection has led to real-world data exfiltration.

### 2.3 Gap Addressed by SECUSYNC

SECUSYNC addresses the gap between ad hoc red-teaming and structured security assessment by providing:
1. A systematic, mutation-driven pipeline that extends attack coverage beyond baseline prompts
2. Hybrid analysis combining deterministic and semantic layers for higher accuracy
3. Fully reproducible PoC bundles and structured PDF reports
4. Quantifiable metrics to benchmark attack success and compare against HOUYI and GPTFuzzer

---

## 3. Requirements Engineering

### 3.1 Requirements Elicitation Method

Requirements were derived from three sources:
- **Proposal document** (September 2025) — defined scope, attack classes, and methodology
- **Related systems analysis** — HOUYI (Liu et al., 2024) and GPTFuzzer (Zhang et al., 2024) identified gaps
- **OWASP LLM Top 10 (2025)** — provided industry standard vulnerability taxonomy

### 3.2 Functional Requirements

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR-01 | System shall support TLLM profile configuration for OpenAI, Anthropic, Ollama, and custom REST endpoints | Must Have | 1 |
| FR-02 | System shall execute Prompt Injection attacks using baseline templates | Must Have | 1 |
| FR-03 | System shall execute System Prompt Leakage attacks | Must Have | 4 |
| FR-04 | System shall execute File Poisoning attacks via document upload | Must Have | 4 |
| FR-05 | System shall execute Sensitive Information Disclosure attacks | Must Have | 4 |
| FR-06 | Mutation Engine shall paraphrase, encode, language-switch, and chain prompts | Must Have | 2 |
| FR-07 | System shall deduplicate near-identical prompt variants using FAISS | Must Have | 2 |
| FR-08 | Deterministic analysis shall detect API keys, PII, and prompt markers via regex | Must Have | 3 |
| FR-09 | Semantic analysis shall classify TLLM outputs via HuggingFace Inference Endpoint | Must Have | 3 |
| FR-10 | Hybrid analysis shall combine both layers into a final verdict | Must Have | 3 |
| FR-11 | System shall generate Executive PDF reports per scan run | Must Have | 5 |
| FR-12 | System shall generate Technical PDF reports with PoC bundles | Must Have | 5 |
| FR-13 | Web UI shall support full scan cycle without terminal interaction | Must Have | 6 |
| FR-14 | Dashboard shall display ASR, mutation efficiency, precision, and recall metrics | Must Have | 6 |
| FR-15 | Live scan progress shall stream to UI via WebSocket | Should Have | 6 |
| FR-16 | Knowledge Base shall be browsable and editable via Web UI | Should Have | 4 |
| FR-17 | System shall support saving and reusing TLLM profiles | Should Have | 1 |

### 3.3 Non-Functional Requirements

| ID | Requirement | Category | Measurement |
|---|---|---|---|
| NFR-01 | API keys must never appear in logs or external calls | Security | Code audit |
| NFR-02 | Raw TLLM responses must be redacted before semantic analysis | Security | Automated test |
| NFR-03 | All scan runs must be auditable with full request/response trace | Auditability | DB verification |
| NFR-04 | Each module must achieve ≥ 80% test coverage | Reliability | pytest-cov report |
| NFR-05 | A 20-prompt scan must complete within 5 minutes | Performance | Timed benchmark |
| NFR-06 | Every finding must include a self-contained reproducible PoC | Reproducibility | Manual verification |
| NFR-07 | App must start with `docker-compose up` in under 2 minutes | Deployability | Timed cold start |
| NFR-08 | All UI text must meet WCAG AA contrast (4.5:1) | Accessibility | Color contrast tool |

### 3.4 Out-of-Scope Requirements (Explicitly Excluded)

The following were considered and explicitly excluded with rationale:

| Feature | Rationale for Exclusion |
|---|---|
| Automated remediation / patching | Expands scope beyond detection; creates liability risk |
| DoS testing | Irrelevant to LLM-specific vulnerability classes; ethical risk |
| Training-time data poisoning | Requires model access beyond runtime API; out of scope for toolkit |
| RL-based mutation optimization | Time cost disproportionate to benefit; documented as future work |
| Multi-tenant / cloud deployment | Single-researcher use case; complexity not justified |
| Audio/video/image-based injection | Insufficient time; documented as future work |
| Testing unauthorized systems | Ethical/legal non-starter |

---

## 4. System Design

### 4.1 Architecture Decision: Client-Server vs Monolith

**Decision:** Separate React frontend + FastAPI backend (client-server)

**Alternatives considered:**
| Option | Pros | Cons | Decision |
|---|---|---|---|
| Full-stack Python (FastAPI + Jinja/HTMX) | Single language, simpler deployment | Limited UI interactivity, poor real-time UX | Rejected |
| React + FastAPI (chosen) | Rich interactive UI, WebSocket support, typed API contract | Two languages, more setup | **Selected** |
| Next.js full-stack | Modern, SSR capable | Overkill for local tool; adds Node complexity to backend | Rejected |

**Rationale:** The live scan streaming requirement (FR-15) and the metrics dashboard (FR-14) demand reactive UI capabilities that static-rendered templates cannot provide efficiently. React with WebSocket hooks is the most direct solution.

### 4.2 Architecture Decision: Database

**Decision:** SQLite for development with a PostgreSQL-compatible schema

**Alternatives considered:**
| Option | Rationale |
|---|---|
| SQLite only | Simple, zero setup; acceptable for single-user local tool |
| PostgreSQL | Production-ready but adds Docker complexity for a local FYP |
| MongoDB | Schema-less flexibility unneeded; structured scan data fits relational model |

**Chosen:** SQLite dev + schema designed to be portable to PostgreSQL. This minimizes setup friction while keeping the codebase production-ready.

### 4.3 Architecture Decision: Vector Store

**Decision:** FAISS (Facebook AI Similarity Search)

**Rationale:** FAISS is the standard for in-process similarity search with no server overhead. The KB is read-heavy and small enough (< 10,000 entries) that a full vector database (Pinecone, Weaviate) would be unnecessary operational overhead. FAISS runs entirely on CPU, matching our no-GPU constraint.

### 4.4 Architecture Decision: Local LLM for Analysis

**Decision:** HuggingFace Inference Endpoints (remote API, pay-per-use)

**Alternatives considered:**
| Option | Pros | Cons | Decision |
|---|---|---|---|
| Ollama (local) | Free, private, no rate limits | Requires GPU for quality models; slow on CPU | Used as fallback only |
| HuggingFace Inference Endpoints (chosen) | High-quality models, no local GPU needed, flexible | Requires internet; API key; potential latency | **Selected** |
| Groq (as in prototype) | Very fast inference | Proprietary, less flexible model selection | Rejected (replaced) |
| OpenAI GPT-4 as judge | Highest quality | Expensive per-call; creates dependency on the same vendor being tested | Rejected |

**Rationale:** Using a different provider for analysis than the TLLMs under test avoids circular dependency. HuggingFace provides access to a wide range of open models (Mistral, Llama, Qwen) without tying the analysis layer to any single commercial vendor.

### 4.5 Architecture Decision: PDF Generation Library

**Decision:** To be finalized in Sprint 5

**Options evaluated:**

| Library | Pros | Cons |
|---|---|---|
| `reportlab` | Mature, fine-grained control, pure Python | Verbose API; styling is code-heavy |
| `weasyprint` | HTML/CSS → PDF; easier styling | Requires Cairo; OS-level dependency |
| `fpdf2` | Simple API | Limited layout control for complex tables |

**Current leaning:** `reportlab` for precise control over branded layouts. Final decision documented in Sprint 5 log.

### 4.6 Data Flow Diagram

```
User (Browser)
    │
    ├─[1]─► POST /api/scans/start
    │           │
    │           ▼
    │       AttackExecutor
    │           │
    │           ├─[2]─► KnowledgeBase.search(attack_class)
    │           │           └─► Returns baseline templates
    │           │
    │           ├─[3]─► MutationEngine.mutate(baseline, strategies, depth)
    │           │           ├─► HuggingFace (paraphrase/translate)
    │           │           └─► Returns variant list
    │           │
    │           ├─[4]─► TLLMConnector.send(variant) ──► TLLM API
    │           │           └─► Returns raw response
    │           │
    │           ├─[5]─► Redactor.clean(raw_response)
    │           │           └─► Returns redacted response
    │           │
    │           ├─[6]─► HybridAnalysis.analyze(redacted_response)
    │           │           ├─► DeterministicLayer (regex)
    │           │           ├─► SemanticLayer ──► HuggingFace Judge
    │           │           └─► Returns verdict + evidence
    │           │
    │           ├─[7]─► DB.store(variant, response, verdict)
    │           │
    │           └─[8]─► WebSocket.broadcast(progress_update)
    │                       │
    ◄───────────────────────┘ (live stream to UI)
```

---

## 5. SDLC Process Model

### 5.1 Model Selected: Agile–Incremental

**Rationale for selection over alternatives:**

| Model | Why Considered | Why Not Chosen |
|---|---|---|
| Waterfall | Simple, well-documented for academic projects | No flexibility for discovering LLM edge cases mid-build; too rigid for a research tool |
| Pure Agile (Scrum) | Maximum flexibility | Overhead of ceremonies (standups, retrospectives) is impractical for a solo developer |
| Spiral | Good for risk-heavy projects | Formal risk assessment cycles are heavyweight for a 7-month FYP |
| **Agile–Incremental (chosen)** | Iterative delivery, each sprint produces runnable software, allows course correction | Requires strict sprint discipline |

**Key properties of our implementation:**
- Each sprint = 2–3 weeks with defined exit criteria
- Every sprint produces a working, testable increment (no half-built states at sprint boundaries)
- New attack classes added incrementally so the system is always runnable
- Manual sprint review at end of each sprint against PRD acceptance criteria

### 5.2 SDLC Work Products

The following work products are produced at each SDLC phase:

| Phase | Work Product | Document/Artifact | Status |
|---|---|---|---|
| **Requirements** | Software Requirements Specification | PRD.md (Section 3 of this Report) | ✅ |
| **System Design** | Architecture Document | architecture.md | ✅ |
| **System Design** | Data Model Diagram | architecture.md Section 4 | ✅ |
| **System Design** | API Contract | architecture.md Section 5 | ✅ |
| **System Design** | Data Flow Diagram | Report.md Section 4.6 | ✅ |
| **Branding/UI** | Brand Identity Guidelines | branding.md + branding.pdf | ✅ |
| **Project Management** | Development Plan + Sprint Schedule | Plan.md | ✅ |
| **Process** | Coding Standards + Agent Rules | Rules.md | ✅ |
| **Implementation** | Source Code (per sprint) | GitHub repository | ✅ |
| **Implementation** | Sprint-by-Sprint Dev Log | Report.md Section 7 + History.md | ✅ |
| **Testing** | Unit Test Suite (≥ 80% coverage) | backend/tests/ | 🔲 |
| **Testing** | Test Coverage Report | pytest-cov HTML report | 🔲 |
| **Validation** | Benchmark Results | Report.md Section 10 | 🔲 |
| **Validation** | HOUYI/GPTFuzzer Comparison Table | Report.md Section 11 | 🔲 |
| **Delivery** | Executive PDF Report (sample) | Generated per scan run | 🔲 |
| **Delivery** | Technical PDF Report (sample) | Generated per scan run | 🔲 |
| **Delivery** | Final Project Report | This document (Report.md) | 🔲 |
| **Delivery** | README with demo instructions | README.md | 🔲 |

---

## 6. Technology Selection & Trade-off Decisions

### 6.1 Master Trade-off Log

Every significant technology decision is documented here with the alternatives considered, the criteria used, and the final rationale. This log is required for FYP evaluation.

---

#### TD-01: Frontend Framework — React vs Vue vs HTMX

**Decision Date:** Pre-Sprint 0  
**Decision:** React (with TypeScript + Vite)

| Criterion | React | Vue | HTMX |
|---|---|---|---|
| TypeScript support | Excellent | Good | N/A (HTML-only) |
| WebSocket / real-time | First-class hooks | Good | Limited |
| State management ecosystem | Zustand + React Query | Pinia | N/A |
| Learning curve | Moderate | Low | Very Low |
| Prototype compatibility | ✅ Prototype already uses React+Vite | New setup needed | Complete rewrite |

**Rationale:** The prototype already used React + Vite + TailwindCSS. Rebuilding clean in the same stack avoids tooling friction. React's ecosystem (React Query for server state, Zustand for UI state, custom WebSocket hooks) directly maps to our requirements.

---

#### TD-02: Backend Framework — FastAPI vs Flask vs Django

**Decision Date:** Pre-Sprint 0  
**Decision:** FastAPI

| Criterion | FastAPI | Flask | Django |
|---|---|---|---|
| Async support (needed for scan tasks) | Native | Via extensions | Via channels |
| Auto-generated OpenAPI docs | ✅ Built-in | No | No |
| Pydantic v2 integration | ✅ Native | Manual | Manual |
| WebSocket support | ✅ Native | Via flask-socketio | Via channels |
| Performance | Highest | Medium | Medium |

**Rationale:** FastAPI's async-first design is essential for the concurrent scan execution model (sending prompts to TLLMs while streaming progress to the UI). Built-in OpenAPI documentation ensures the frontend contract is always up to date.

---

#### TD-03: Analysis LLM Provider — HuggingFace vs Ollama vs OpenAI as Judge

**Decision Date:** Pre-Sprint 3  
**Decision:** HuggingFace Inference Endpoints (primary), Ollama (fallback)

| Criterion | HuggingFace Endpoints | Ollama | OpenAI |
|---|---|---|---|
| No GPU required | ✅ | ❌ (quality models) | ✅ |
| Vendor independence | ✅ (open models) | ✅ | ❌ |
| Cost | Pay-per-use (low) | Free | Expensive |
| Model quality | High (Mistral, Llama) | Good (CPU models) | Highest |
| Circular vendor risk | ✅ None | ✅ None | ❌ (testing OpenAI with OpenAI judge) |

**Rationale:** Using the same vendor (e.g., OpenAI) as both TLLM and judge creates circular evaluation — the judge may be biased toward not flagging its own outputs. HuggingFace open models eliminate this conflict.

---

#### TD-04: Mutation Strategy Scope — 6 Strategies vs Fewer

**Decision Date:** Pre-Sprint 2  
**Decision:** Implement all 6 strategies defined in the proposal

| Strategy | Academic Basis | Implementation Complexity | Decision |
|---|---|---|---|
| Paraphrase | Adversarial NLP literature | Medium (HuggingFace call) | ✅ Include |
| Base64 / ROT13 encoding | HOUYI paper | Low (stdlib) | ✅ Include |
| Unicode obfuscation | GPTFuzzer, HOUYI | Low (char map) | ✅ Include |
| Language switching | Cross-lingual attack research | Medium (HuggingFace call) | ✅ Include |
| Multi-step chaining | HOUYI three-part structure | Medium (conversation history) | ✅ Include |

**Rationale:** Including all 6 strategies allows the benchmarking section to report which strategies contribute most to ASR improvement — a key research contribution of the project.

---

#### TD-05: Report Generation — reportlab vs weasyprint

**Decision Date:** Sprint 5 (TBD — to be finalized and documented here)  
**Decision:** 🔲 Pending Sprint 5

*Agent instruction: Update this entry when the Sprint 5 PDF library decision is made.*

---

#### TD-06: Prototype Reuse Policy — Extend vs Rebuild

**Decision Date:** Pre-Sprint 0  
**Decision:** Reference only — rebuild clean

**Rationale:**  
The prototype (GitHub: AosawnX/Secusync-LLM-Security-Testing-Toolkit) is a functional proof-of-concept but has several issues that make extension inadvisable:
1. Uses Groq/Llama 3.3 as judge — replaced with HuggingFace endpoints in the new design
2. No unit tests
3. TypeScript used for config files mixed with Python — architectural inconsistency
4. No FAISS KB, no multi-attack-class structure, no file poisoning support

Rebuilding clean with the architecture defined in `architecture.md` produces a more maintainable, testable, and extensible codebase. Specific logic patterns (e.g., OpenAI connector pattern, basic scan orchestration) are adapted from the prototype where appropriate and noted in `History.md`.

---

## 7. Sprint-by-Sprint Development Log

*Agent instruction: After completing each sprint, fill in the corresponding subsection below. Copy the key points from the History.md sprint summary entry.*

### Sprint 0 — Foundation & Setup

✅ **Status:** Completed  
**Planned:** Oct 1–10, 2025

**Key Decisions to Document Here:**
- Final repo structure: Exactly mapped to `architecture.md`.
- Docker configuration choices: Standard `docker-compose.yml` with separate backend (Uvicorn/FastAPI) and frontend (Vite/React) services without volumes for docs avoiding sync loops.
- Database migration tool choice: Chosen `alembic` configured for autogenerating SQLite variants.

**Actual Outcomes:** Successfully scaffolded entirely, with Python environment setup, SQLite initialized, and frontend boilerplate implemented cleanly. Built Docker images locally successfully.  
**Deviations from Plan:** None  
**Exit Criteria Met:** Yes -> Docker runs, Health Check active, Schema Built.

---

### Sprint 1 — TLLM Config + Basic Prompt Injection

✅ **Status:** Completed  
**Planned:** Oct 11–31, 2025

**Key Decisions to Document Here:**
- Utilized Pydantic settings for TLLM API key and configuration injection securely.
- Adopted the LocalMock provider structure alongside standard external targets.

**Actual Outcomes:** Basic scan cycle functioning using fixed target schemas. Runs register in the database.  
**Deviations from Plan:** Advanced target forms introduced earlier to account for local mock.  

---

### Sprint 2 — Mutation Engine

✅ **Status:** Completed  
**Planned:** Nov 1–15, 2025

**Key Decisions to Document Here:**
- Utilized rule-based structural shifts alongside basic injections (Base64, JSON wrap, framing, leetspeak).

**Actual Outcomes:** The `MutationEngine` successfully extends baseline prompts dynamically prior to network dispatch.  

---

### Sprint 3 — Hybrid Analysis Module

✅ **Status:** Completed  
**Planned:** Nov 16–30, 2025

**Key Decisions to Document Here:**
- Dual-layer methodology implemented: The LLM Judge acts as the deterministic primary, with Regex providing hard safety fallbacks.
- Weighted scoring system applied (0.0 to 1.0) inside the evaluation loops to categorize risk severity.

**Actual Outcomes:** Responses evaluate conditionally on semantic context. Identified vulnerabilities accurately populate via `PromptVariant` databases.  

---

### Sprint 4 — Knowledge Base + All Attack Classes

🔲 **Status:** Not yet started  
**Planned:** Dec 1–15, 2025

**Key Decisions to Document Here:**
- KB seeding sources (OWASP, HOUYI, GPTFuzzer, custom)
- File Poisoning: document formats supported and injection method
- Embedding model chosen for FAISS (sentence-transformer model name)

**Actual Outcomes:** *(to be filled)*  
**Deviations from Plan:** *(to be filled)*  
**Exit Criteria Met:** *(to be filled)*

---

### Sprint 5 — Report Generator

✅ **Status:** Completed  
**Planned:** Jan 16–Feb 15, 2026

**Key Decisions to Document Here:**
- Utilized `xhtml2pdf` + `jinja2` directly overriding complex library dependencies due to raw HTML to PDF parity requirements.
- Modularized technical vs executive insights inside the reporting generation function by piping database hits back into the LLM Judge for tailored synthesis.
- Implemented automated POC bundling via standard zip exports.

**Actual Outcomes:** Clean dynamic PDFs generate securely on demand without compromising tokens or DB stability.  
**Exit Criteria Met:** Yes. Frontend integrated safely with immediate visual responses.

---

### Sprint 6 — Frontend Polish + Metrics Dashboard

🔲 **Status:** Not yet started  
**Planned:** Feb 16–Mar 15, 2026

**Key Decisions to Document Here:**
- WebSocket message protocol schema
- Chart library chosen (Recharts vs Chart.js)
- Metrics computation implementation (on-the-fly vs pre-computed at scan completion)

**Actual Outcomes:** *(to be filled)*  
**Deviations from Plan:** *(to be filled)*  
**Exit Criteria Met:** *(to be filled)*

---

### Sprint 7 — Defense Prep + Final Integration

🔲 **Status:** Not yet started  
**Planned:** Mar 16–Apr 2026

**Key Decisions to Document Here:**
- Synthetic test harness design (how it was built to be consistently exploitable)
- Final benchmark methodology
- Defense demo script walkthrough

**Actual Outcomes:** *(to be filled)*  
**Deviations from Plan:** *(to be filled)*  
**Exit Criteria Met:** *(to be filled)*

---

## 8. Testing & Validation

### 8.1 Testing Strategy

SECUSYNC follows a multi-layer testing approach:

| Layer | Type | Tool | Target Coverage | When |
|---|---|---|---|---|
| Unit | Module-level logic | pytest | ≥ 80% per module | Each sprint |
| Integration | API endpoint testing | pytest + httpx TestClient | Key flows | Each sprint |
| Contract | Frontend ↔ Backend API | Manual + Pydantic validation | All endpoints | Each sprint |
| Security | Redactor never passes secrets | Automated pytest | 100% | Sprint 3 |
| System | End-to-end scan cycle | Manual + Playwright (optional) | Happy path + 2 edge cases | Sprint 6 |
| Performance | 20-prompt scan ≤ 5 min | Timed benchmark | NFR-05 | Sprint 6 |

### 8.2 Test Coverage Report

🔲 *(To be populated as sprints complete)*

| Module | Tests Written | Coverage | Sprint |
|---|---|---|---|
| tllm_connector.py | — | — | 1 |
| mutation_engine.py | — | — | 2 |
| analysis/deterministic.py | — | — | 3 |
| analysis/semantic.py | — | — | 3 |
| analysis/hybrid.py | — | — | 3 |
| knowledge_base.py | — | — | 4 |
| attack_executor.py | — | — | 4 |
| report_generator.py | — | — | 5 |

### 8.3 Bug Log Summary

🔲 *(To be populated from History.md bug entries)*

| Bug ID | Sprint | Module | Type | Severity | Resolution |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## 9. Security & Ethical Considerations

### 9.1 Security Design Decisions

| Concern | Decision | Implementation |
|---|---|---|
| API key storage | Environment variables only; never in DB | `config.py` with pydantic-settings; `.env.example` only in repo |
| Raw response handling | Never sent to external services | `redactor.py` runs before `semantic.py` every time |
| Scan authorization | Explicit `authorized: true` flag required | Guard check in `AttackExecutor` before scan starts |
| Audit trail | Full request/response logged per variant | `PromptVariant` table with timestamps |
| Secrets in reports | All redacted before PDF generation | Redactor applied to all report content |

### 9.2 Ethical Framework

- All experiments conducted in sandbox environments or against explicitly authorized TLLMs
- PoC bundles in reports include a responsible disclosure notice
- No scan can be initiated without explicit authorization confirmation in the UI
- The toolkit is designed for defensive research — findings are paired with remediation guidance

### 9.3 Threat Model

The following threats were considered in the system's design:

| Threat | Vector | Mitigation |
|---|---|---|
| Credential leakage | API keys logged to disk | Redactor + structured logging that strips key patterns |
| Re-exfiltration | Raw TLLM response sent to HuggingFace judge | Redactor mandatory before all external calls |
| Unauthorized scan | Scanning systems without permission | Authorization flag + UI confirmation dialog |
| Prompt injection against SECUSYNC itself | Malicious TLLM response manipulating the analysis | Analysis runs in isolated function scope; no eval() |

---

## 10. Benchmarking & Experimental Results

🔲 *(To be completed in Sprint 7)*

### 10.1 Test Setup

- **Test TLLM:** *(model name, provider, system prompt used)*
- **Hardware:** *(CPU, RAM, OS)*
- **Run date:** *(April 2026)*
- **Total prompt variants tested:** *(TBD)*

### 10.2 Attack Success Rate (ASR)

| Attack Class | Baseline ASR | Mutated ASR | Delta | Best Strategy |
|---|---|---|---|---|
| Prompt Injection | — | — | — | — |
| System Prompt Leakage | — | — | — | — |
| File Poisoning | — | — | — | — |
| Sensitive Info Disclosure | — | — | — | — |
| **Overall** | — | — | — | — |

### 10.3 Mutation Efficiency

| Strategy | Avg Mutations to First Success | Success Rate |
|---|---|---|
| Paraphrase | — | — |
| Base64 Encoding | — | — |
| ROT13 | — | — |
| Unicode Obfuscation | — | — |
| Language Switch | — | — |
| Multi-step Chaining | — | — |

### 10.4 Detection Accuracy

| Metric | Value |
|---|---|
| True Positives | — |
| False Positives | — |
| False Negatives | — |
| Precision | — |
| Recall | — |
| F1 Score | — |

### 10.5 Performance

| Metric | Result | Target | Pass/Fail |
|---|---|---|---|
| 20-prompt scan duration | — | ≤ 5 minutes | — |
| docker-compose cold start | — | ≤ 2 minutes | — |
| PDF report generation time | — | ≤ 30 seconds | — |

---

## 11. Comparison with Related Systems

🔲 *(Partial entries now; to be completed with measured data in Sprint 7)*

| Dimension | HOUYI (Liu et al., 2024) | GPTFuzzer (Zhang et al., 2024) | SECUSYNC |
|---|---|---|---|
| Methodology | Black-box 3-part prompt injection | Fuzzing with multi-dim oracles | Mutation-driven pipeline with hybrid analysis |
| Attack classes | Prompt injection only | Prompt injection, data leakage | 4 classes (PI, SPL, FP, SID) |
| Mutation strategies | Framework/Separator/Disruptor | Input mutation | 6 strategies with lineage tracking |
| Semantic analysis | No | Limited | Yes — HuggingFace judge with deterministic corroboration |
| Runtime traceability | Limited | Limited | Full request/response/verdict log per variant |
| Reproducibility | No PoC bundles | No PoC bundles | Structured PoC bundles in Technical Report |
| RAG/file attack support | No | No | Yes — File Poisoning via document upload |
| Reporting | No | No | Executive + Technical PDF with metrics |
| ASR (reported) | 86.1% (36 commercial apps) | Varies | `[TBD — Sprint 7]` |
| Open-source / extensible | Academic preprint | Academic preprint | Fully modular, documented codebase |

**Key differentiators of SECUSYNC:**
1. Only system with a dedicated File Poisoning (indirect injection) attack class
2. Only system combining deterministic + semantic analysis with FAISS corroboration
3. Only system producing structured, reproducible PoC bundles and PDF reports
4. Only system with a metrics dashboard enabling longitudinal benchmarking

---

## 12. Known Limitations & Future Work

### 12.1 Known Limitations (In-Scope Constraints)

| Limitation | Reason | Impact |
|---|---|---|
| No GPU — inference via HuggingFace endpoints | Hardware constraint | Latency on semantic analysis calls |
| SQLite only | Scope reduction for FYP | Not suitable for multi-user production deployment |
| File Poisoning limited to PDF and TXT | Scope constraint | Audio/video/image injection not covered |
| No RL-based mutation optimization | Time constraint | Mutation strategies are heuristic, not adaptive |

### 12.2 Future Work

| Item | Description | Priority |
|---|---|---|
| FW-01 | RL-based adaptive mutation (RLHF loop to optimize ASR) | High |
| FW-02 | Multimodal injection (image, audio-based) | High |
| FW-03 | Multi-tenant support with user authentication | Medium |
| FW-04 | CI/CD integration — scan as a pipeline gate | Medium |
| FW-05 | Real-time collaborative red-teaming (multi-user) | Low |
| FW-06 | Automated patch suggestion engine | Low |
| FW-07 | Kubernetes deployment for enterprise-scale testing | Low |

---

## 13. Project Retrospective

🔲 *(To be completed at project completion — Sprint 7)*

### 13.1 What Went Well
*(to be filled)*

### 13.2 What Was Challenging
*(to be filled)*

### 13.3 What Would Be Done Differently
*(to be filled)*

### 13.4 Lessons Learned
*(to be filled)*

---

## 14. References

[1] Liu, Y. et al. (2024). "Prompt Injection Attack against LLM-integrated Applications." *arXiv preprint arXiv:2306.05499.*

[2] Zhang, T. et al. (2024). "GPTFuzzer: Fuzzing-Based Vulnerability Detection in Large Language Model Integrated Applications." *IEEE Transactions on Dependable and Secure Computing.*

[3] OWASP Foundation. (2025). *OWASP Top 10 for LLM Applications 2025.* https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/

[4] HackerOne. (2024). "How a Prompt Injection Vulnerability Led to Data Exfiltration." https://www.hackerone.com/blog/how-prompt-injection-vulnerability-led-data-exfiltration

[5] Balashova, A., Ponomarova, O., & Zhai, X. (2025). "Multi-Stage Prompt Inference Attacks on Enterprise LLM Systems." *arXiv:2507.15613 [cs.CR].*

[6] Kucharavy, A. et al. (Eds.) (2024). *Large Language Models in Cybersecurity: Threats, Exposure and Mitigation.* Springer. DOI: 10.1007/978-3-031-54827-7.

[7] Kindo AI. (2025). *Deep Hat: Uncensored AI for DevSecOps.* https://www.deephat.ai/

[8] Ollama. (2025). *phi4-Mini-Reasoning.* https://ollama.com/library/phi4-mini-reasoning
