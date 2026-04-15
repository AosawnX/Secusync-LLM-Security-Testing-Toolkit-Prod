# SECUSYNC — Development Plan

**Version:** 1.0  
**Methodology:** Agile–Incremental  
**Timeline:** October 2025 – April 2026  
**Developer:** Syed Abdullah Shah  
**Deadline:** April 2026 (FYP Defense)

---

## Methodology

This project follows an **Agile–Incremental** process. Each sprint produces a runnable, testable increment. No sprint ends in a broken state. Sprints are 2–3 weeks long and map directly to the milestones in the proposal.

The product grows in this order:
> Prototype → Mutation Engine → Hybrid Analysis → Knowledge Base → Reports → Refinement → Defense-Ready

---

## Sprint Overview

| Sprint | Name | Duration | Deliverable |
|---|---|---|---|
| 0 | Foundation & Setup | Oct 1–10, 2025 | Repo, dev environment, DB schema, blank app skeleton |
| 1 | TLLM Config + Basic Injection | Oct 11–31, 2025 | TLLM profile CRUD, prompt injection baseline test, basic response logging |
| 2 | Mutation Engine | Nov 1–15, 2025 | All 6 mutation strategies, deduplication, variant lineage tracking |
| 3 | Hybrid Analysis Module | Nov 16–30, 2025 | Regex detectors, HuggingFace semantic judge, hybrid combiner |
| 4 | Knowledge Base + File Poisoning | Dec 1–15, 2025 | FAISS KB seeded, all 4 attack classes active, file poisoning module |
| 5 | Report Generator | Jan 16–Feb 15, 2026 | Executive + Technical PDF reports, PoC bundle export |
| 6 | Frontend Polish + Metrics Dashboard | Feb 16–Mar 15, 2026 | Full Web UI scan cycle, live WebSocket stream, metrics display |
| 7 | Defense Prep + Final Integration | Mar 16–Apr 2026 | Benchmarks vs HOUYI/GPTFuzzer, docker-compose, Report.md completed, final docs |

> **Living documents updated every sprint:** `History.md` (per-module + sprint summary) and `Report.md` (sprint log + trade-off decisions + test coverage + benchmark data)

---

## Sprint 0 — Foundation & Setup
**Duration:** Oct 1–10, 2025  
**Goal:** Everything scaffolded and runnable, no business logic yet.

### Tasks
- [ ] Initialize Git repo with the folder structure from `architecture.md`
- [ ] Set up Python virtual environment, install base dependencies
- [ ] Set up FastAPI app with health check endpoint (`GET /api/health`)
- [ ] Set up SQLAlchemy with SQLite, create all ORM models (TLLMProfile, ScanRun, PromptVariant, KBEntry)
- [ ] Run initial Alembic migrations
- [ ] Set up React + Vite + TailwindCSS frontend with placeholder pages
- [ ] Set up `docker-compose.yml` with backend + frontend services
- [ ] Configure `config.py` with pydantic-settings for all env vars
- [ ] Create `.env.example` with all required variables documented
- [ ] Write `README.md` with setup instructions

### Exit Criteria
- `docker-compose up` starts both services without errors
- `GET /api/health` returns `{"status": "ok"}`
- Frontend renders a blank dashboard page
- Database schema created with all tables

---

## Sprint 1 — TLLM Config + Basic Prompt Injection
**Duration:** Oct 11–31, 2025  
**Goal:** End-to-end scan cycle working for Prompt Injection using baseline (non-mutated) prompts.

### Tasks
- [ ] Implement `TLLMProfile` CRUD endpoints (`POST`, `GET /api/tllm/profiles`)
- [ ] Implement `TLLMConnector` supporting all 4 providers (OpenAI, Anthropic, Ollama, Custom)
- [ ] Load baseline Prompt Injection templates from `kb_data/attack_templates.json`
- [ ] Implement `POST /api/scans/start` — runs baseline prompts only (no mutation yet)
- [ ] Store raw responses in `PromptVariant` table
- [ ] Implement basic verdict: regex check only (no semantic layer yet)
- [ ] Implement `GET /api/scans/{run_id}/results`
- [ ] Frontend: New Scan page — configure TLLM, select attack class, start scan
- [ ] Frontend: Run Detail page — show variants and verdicts (table view)
- [ ] Write tests: `test_tllm_connector.py`, `test_attack_executor.py` (baseline only)
- [ ] Seed `kb_data/attack_templates.json` with ≥ 10 Prompt Injection baseline prompts

### Exit Criteria
- User can configure a TLLM profile via Web UI
- User can start a Prompt Injection scan via Web UI
- Results (prompt sent, response received, regex verdict) appear in Run Detail page
- All tests pass

### Prototype Reference
- Reuse logic from prototype's `backend/` for the OpenAI connector pattern
- Reuse prompt injection templates from prototype if present

---

## Sprint 2 — Mutation Engine
**Duration:** Nov 1–15, 2025  
**Goal:** Mutation Engine produces measurably diverse variants from baseline prompts.

### Tasks
- [ ] Implement `HFClient` — wrapper for HuggingFace Inference Endpoint calls
- [ ] Implement `mutation_engine.py` with all 6 strategies:
  - `paraphrase` (via HuggingFace)
  - `encode_b64`
  - `encode_rot13`
  - `encode_unicode`
  - `lang_switch` (via HuggingFace translation)
  - `chain` (multi-turn split)
- [ ] Implement FAISS deduplication check (cosine similarity > 0.95 → discard)
- [ ] Track parent-child lineage in `PromptVariant.parent_id`
- [ ] Update `AttackExecutor` to use `MutationEngine` before sending prompts
- [ ] Expose mutation strategy + depth configuration in `POST /api/scans/start`
- [ ] Frontend: New Scan page — add mutation strategy multi-select + depth slider
- [ ] Write tests: `test_mutation_engine.py` covering all 6 strategies + dedup logic

### Exit Criteria
- A scan with depth=2 produces noticeably different prompt variants
- Deduplication discards near-identical variants (test verified)
- Parent-child lineage is stored and queryable
- All tests pass at ≥ 80% coverage

---

## Sprint 3 — Hybrid Analysis Module
**Duration:** Nov 16–30, 2025  
**Goal:** Both layers of analysis (regex + semantic) working and combined.

### Tasks
- [ ] Implement `deterministic.py` with all regex patterns from `architecture.md` Section 3.4
- [ ] Implement `redactor.py` — replaces detected secrets with `[REDACTED]` before external calls
- [ ] Implement `semantic.py` — sends redacted response to HuggingFace judge endpoint
- [ ] Implement `hybrid.py` — combiner logic producing final verdict
- [ ] Update `AttackExecutor` to run hybrid analysis on every response
- [ ] Store `deterministic_matches` and `semantic_classification` in `PromptVariant`
- [ ] Frontend: Run Detail page — show verdict badge (VULNERABLE / NOT_VULNERABLE / NEEDS_REVIEW) with evidence
- [ ] Write tests: `test_deterministic.py`, `test_hybrid_analysis.py`
- [ ] Add `NEEDS_REVIEW` queue in Run Detail — list items needing manual review

### Exit Criteria
- Regex layer correctly flags API key patterns and system prompt echoes
- Semantic layer returns valid classification for test responses
- Hybrid combiner logic verified by unit tests
- Redactor confirmed to never pass raw secrets to external services (test verified)

---

## Sprint 4 — Knowledge Base + Remaining Attack Classes
**Duration:** Dec 1–15, 2025  
**Goal:** All 4 attack classes functional; FAISS KB seeded and integrated.

### Tasks
- [ ] Implement `knowledge_base.py` with FAISS index + SQLite metadata
- [ ] Implement `seed_from_file()` — load `attack_templates.json` into FAISS on startup
- [ ] Seed KB with ≥ 10 templates per attack class (40+ total):
  - Prompt Injection
  - System Prompt Leakage
  - File Poisoning
  - Sensitive Information Disclosure
- [ ] Implement File Poisoning: accept document upload (PDF/TXT), inject prompt into document, send to TLLM
- [ ] Implement System Prompt Leakage: baseline + mutated extraction prompts
- [ ] Update `MutationEngine` to use KB for guided prompt generation
- [ ] Implement KB CRUD endpoints (`GET`, `POST`, `DELETE /api/kb/entries`)
- [ ] Frontend: Knowledge Base Manager page — browse, add, delete entries
- [ ] Write tests for all new components

### Exit Criteria
- All 4 attack classes produce verdicts in scan runs
- KB returns relevant templates for given attack class queries
- File upload → poisoning flow works end-to-end
- KB Manager page functional in Web UI

---

## Sprint 5 — Report Generator
**Duration:** Jan 16–Feb 15, 2026  
**Goal:** Both PDF reports fully generated per scan run.

### Tasks
- [ ] Choose and integrate PDF library (evaluate `reportlab` vs `weasyprint`)
- [ ] Implement `report_generator.py`
- [ ] Generate Executive Report PDF (all sections from architecture)
- [ ] Generate Technical Report PDF (all sections including PoC bundles)
- [ ] Implement redaction in Technical Report (secrets shown as `[REDACTED]`)
- [ ] Add responsible disclosure notice to all PoC bundles
- [ ] Implement `GET /api/reports/{run_id}/executive` and `technical` endpoints
- [ ] Frontend: Reports page — list runs, download executive and technical PDF buttons
- [ ] Write tests: `test_report_generator.py`

### Exit Criteria
- Both PDFs generate without errors for a completed scan run
- Executive PDF contains risk matrix and top findings
- Technical PDF contains full variant table, PoC bundles, and redacted responses
- PDFs downloadable from Web UI

---

## Sprint 6 — Frontend Polish + Metrics Dashboard
**Duration:** Feb 16–Mar 15, 2026  
**Goal:** Full Web UI scan cycle with no terminal interaction; all defense metrics visible.

### Tasks
- [ ] Implement WebSocket stream: `WS /api/scans/{run_id}/stream`
- [ ] Frontend: Live Run View — real-time progress (variants sent, verdicts received, % complete)
- [ ] Frontend: Dashboard — stats cards (total runs, total vulnerabilities, ASR by attack class)
- [ ] Implement metrics computation:
  - Attack Success Rate (ASR)
  - Mutation Efficiency (avg mutations to first success)
  - Detection Precision and Recall
  - Baseline vs Mutant ASR Delta
- [ ] Store computed metrics in `ScanRun` table
- [ ] Display metrics in Run Detail page and Dashboard
- [ ] Frontend: Run History page — filterable/sortable list with status badges
- [ ] Frontend: Settings page — configure HuggingFace endpoint, default mutation settings
- [ ] UI polish: consistent design, loading states, error states, empty states

### Exit Criteria
- Complete scan cycle (configure → start → watch live → view results → download reports) works via Web UI only
- All 6 metrics from PRD Section 5 computed and displayed
- WebSocket stream updates UI in real-time during active scan

---

## Sprint 7 — Defense Prep + Final Integration
**Duration:** Mar 16–Apr 2026  
**Goal:** Defense-ready. Benchmarks documented. Docker clean. All docs final.

### Tasks
- [ ] Build and test synthetic vulnerable TLLM harness for repeatable demo
- [ ] Run full benchmark: compute ASR for baseline vs mutated prompts across all 4 attack classes
- [ ] Document HOUYI / GPTFuzzer comparison table (included in Technical Report)
- [ ] Verify all 14 Rules are satisfied (Rules.md compliance check)
- [ ] Verify all 9 PRD Acceptance Criteria are met
- [ ] Run all tests — achieve ≥ 80% coverage across all modules
- [ ] `docker-compose up` cold-start in < 2 minutes
- [ ] Final `History.md` update with full project retrospective
- [ ] Final `README.md` with demo instructions
- [ ] Prepare defense demo script (5-minute walkthrough of full scan cycle)

### Exit Criteria (= PRD Acceptance Criteria)
- [ ] All 4 attack classes produce detectable, reproducible findings
- [ ] Mutation Engine ASR > baseline ASR (with numbers)
- [ ] Executive and Technical PDFs generate without errors
- [ ] Web UI full scan cycle works without terminal
- [ ] All 6 metrics displayed on dashboard
- [ ] HOUYI/GPTFuzzer comparison documented
- [ ] All modules ≥ 80% test coverage
- [ ] `docker-compose up` works

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| HuggingFace Inference Endpoint rate limits | Medium | High | Cache responses; add configurable delay; fallback to local Ollama for analysis |
| Semantic judge misclassifies benign outputs | Medium | Medium | Hybrid approach means regex layer is deterministic anchor; flag UNCERTAIN for manual review |
| File Poisoning complex to implement | Medium | Medium | Scope to PDF and TXT only in Sprint 4; skip image/audio formats |
| Sprint overrun | Medium | High | Strict scope per sprint; defer polish to Sprint 6; core functionality prioritized |
| No GPU for large local models | Low | Low | All inference via HuggingFace endpoints; Ollama models chosen to be CPU-capable |

---

## Dependency Map

```
Sprint 0 (Foundation)
    └── Sprint 1 (TLLM + Basic Injection)
            └── Sprint 2 (Mutation Engine)
                    └── Sprint 3 (Hybrid Analysis)
                            └── Sprint 4 (KB + All Attack Classes)
                                    └── Sprint 5 (Reports)
                                            └── Sprint 6 (Frontend + Metrics)
                                                        └── Sprint 7 (Defense Prep)
```

Each sprint strictly depends on the previous. No sprint can begin until its predecessor's Exit Criteria are met.
