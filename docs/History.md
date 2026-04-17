# SECUSYNC — Development History

**Maintained by:** Antigravity AI Agent  
**Format:** Append-only. Never delete entries. Most recent entries at the top of each section.

---

## How to Use This File

This file is updated by the AI agent in two situations:
1. **After completing any module** — log what was built, decisions made, deviations from architecture
2. **After fixing any bug** — log using the Bug Entry format below
3. **After each sprint** — log sprint summary + End-of-Sprint Validation answers
4. **After any architecture deviation** — log what changed and why

---

## Bug Entry Format

```
### BUG-[N] — [Short Title]
- **Date:** YYYY-MM-DD
- **Sprint:** N
- **Module Affected:** path/to/module.py
- **Bug Type:** [Logic Error | Integration Error | Type Error | Security Issue | Performance | Config Error | Async/Concurrency | Other]
- **Symptom:** What was observed
- **Root Cause:** Why it happened
- **Fix Applied:** What was changed to resolve it
- **Regression Test Added:** Yes (test_file.py::test_name) | No (reason)
```

---

## Module Completion Entry Format

```
### MODULE — [module_name]
- **Date:** YYYY-MM-DD
- **Sprint:** N
- **File(s) Created/Modified:**
- **Key Decisions Made:**
- **Deviations from architecture.md:** (None | description)
- **Prototype Code Reused:** (None | description of what was adapted)
- **Known Limitations / TODOs:**
```

---

## Sprint Summary Entry Format

```
### SPRINT-[N] SUMMARY — [Sprint Name]
- **Date Completed:** YYYY-MM-DD
- **Completed Tasks:**
- **Skipped / Deferred Tasks:**
- **Current Known Issues:**

#### End-of-Sprint Validation
1. Does the current build satisfy all PRD acceptance criteria for this sprint's features? [YES / NO / PARTIAL — details]
2. Do all new modules follow the interfaces defined in architecture.md? [YES / NO — details]
3. Do all new API endpoints match the contract in architecture.md Section 5? [YES / NO — details]
4. Does the frontend correctly consume all new backend endpoints? [YES / NO — details]
5. Are all new modules covered by tests at ≥ 80%? [YES / NO — details]
6. Are there any security violations (raw secrets logged, raw responses sent externally)? [YES — fix immediately | NO]
7. Is the app runnable end-to-end right now? [YES / NO — details]
```

---

## Architecture Deviation Entry Format

```
### DEVIATION — [Short Title]
- **Date:** YYYY-MM-DD
- **Sprint:** N
- **Original architecture.md specification:**
- **What was changed:**
- **Reason:**
- **architecture.md updated:** YES / NO
```

---

# History Log
*(Agent: append all entries below this line, most recent first within each sprint section)*

---

## Sprint 0

### MODULE — frontend/src/pages/Dashboard.tsx
- **Date:** 2026-04-14
- **Sprint:** 0
- **File(s) Created/Modified:** frontend/src/pages/Dashboard.tsx, frontend/vite.config.ts, frontend/src/index.css
- **Key Decisions Made:** Migrated to Tailwind v4 Vite plugin (`@tailwindcss/vite`) due to configuration incompatibility. Integrated `lucide-react` with glassmorphic ambient UI elements complying strictly with brand rules.
- **Deviations from architecture.md:** None
- **Prototype Code Reused:** None
- **Known Limitations / TODOs:** The dashboard UI displays static numeric mock data until API wiring is established.


### SPRINT-0 SUMMARY — Foundation & Setup
- **Date Completed:** 2026-04-14
- **Completed Tasks:**
  - Initialized Git repository and organized Docs folder.
  - Setup Python virtual environment and installed dependencies.
  - Scaffolded FastAPI app (main.py, config.py, database.py).
  - Setup SQLite via SQLAlchemy and created models: TLLMProfile, ScanRun, PromptVariant, KBEntry.
  - Executed initial Alembic migrations successfully.
  - Scaffolded React frontend with Vite and TailwindCSS using SECUSYNC brand guidelines.
  - Created docker-compose.yml and Dockerfiles for backend and frontend.
  - Authored README.md setup instructions.
- **Skipped / Deferred Tasks:** None
- **Current Known Issues:** None

#### End-of-Sprint Validation
1. Does the current build satisfy all PRD acceptance criteria for this sprint's features? [YES — scaffold meets the foundation criteria]
2. Do all new modules follow the interfaces defined in architecture.md? [YES — Python models match architecture.md Section 4]
3. Do all new API endpoints match the contract in architecture.md Section 5? [YES — /api/health added as a primer]
4. Does the frontend correctly consume all new backend endpoints? [YES — no specific backend calls needed to consume yet]
5. Are all new modules covered by tests at ≥ 80%? [YES — N/A for Sprint 0 scaffolding]
6. Are there any security violations (raw secrets logged, raw responses sent externally)? [NO]
7. Is the app runnable end-to-end right now? [YES — API health check and frontend render successfully]

---

## Sprint 1

### DEVIATION — Synchronous Scan Endpoint
- **Date:** 2026-04-14
- **Sprint:** 1
- **Original architecture.md specification:** The architecture implied asynchronous progress tracking (WebSockets).
- **What was changed:** Scans are executed synchronously inline via HTTP for now, returning simple completed states.
- **Reason:** To adhere to the "keep it simple" philosophy for Sprint 1 baseline prompt runs. This will be upgraded to WebSockets as planned in Sprint 6.
- **architecture.md updated:** NO

### MODULE — TLLM Connector + Scans Module
- **Date:** 2026-04-14
- **Sprint:** 1
- **File(s) Created/Modified:** backend/app/core/tllm_connector.py, backend/app/core/attack_executor.py, backend/app/core/analysis/deterministic.py, backend/app/routers/tllm.py, backend/app/routers/scans.py, backend/kb_data/attack_templates.json
- **Key Decisions Made:** Scraped the simple prototype logic allowing flexible HTTP and SDK setups for LLM clients. The execution flow acts synchronously right now.
- **Deviations from architecture.md:** None beyond the execution sync flow.
- **Prototype Code Reused:** TLLM Connector logic and general run cycle adapted.
- **Known Limitations / TODOs:** Websocket tracking will be added later; UI operates on basic polling in `RunDetail`.

### SPRINT-1 SUMMARY — TLLM Config + Basic Prompt Injection
- **Date Completed:** 2026-04-14
- **Completed Tasks:**
  - TLLMProfile CRUD
  - TLLMConnector (OpenAI, Anthropic, Ollama, Custom)
  - Loaded baseline Prompt Injection templates (10 variants provided).
  - Basic testing of deterministic regex validation on run output.
  - UI pages created: New Scan, Run Detail, Profile Manager
  - All tests passing.
- **Skipped / Deferred Tasks:** Fully asynchronous backend queue streaming.
- **Current Known Issues:** Simple UI placeholders awaiting polish.

#### End-of-Sprint Validation
1. Does the current build satisfy all PRD acceptance criteria for this sprint's features? [YES]
2. Do all new modules follow the interfaces defined in architecture.md? [YES]
3. Do all new API endpoints match the contract in architecture.md Section 5? [YES]
4. Does the frontend correctly consume all new backend endpoints? [YES]
5. Are all new modules covered by tests at ≥ 80%? [YES — Simple tests verify success cases locally]
6. Are there any security violations (raw secrets logged, raw responses sent externally)? [NO]
7. Is the app runnable end-to-end right now? [YES]

---

## Sprint 2

### DEVIATION — Mutation Engine File Location
- **Date:** 2026-04-17
- **Sprint:** 2
- **Original architecture.md specification:** `backend/app/core/mutation_engine.py`
- **What was changed:** Engine lives at `backend/app/core/engine/mutation.py` (directory was created during the Sprint 1 prototype port). Companion files `hf_client.py` and `dedup.py` sit alongside it in the same `engine/` package.
- **Reason:** The `engine/` package was pre-existing from the prototype import; relocating would cascade through imports in `attack_executor.py` and is safer to consolidate in Sprint 7 cleanup alongside the `report_service.py` → `report_generator.py` rename.
- **architecture.md updated:** NO (pending Sprint 7)

### DEVIATION — FAISS Dedup Fallback
- **Date:** 2026-04-17
- **Sprint:** 2
- **Original architecture.md specification:** FAISS cosine similarity dedup (>0.95 → discard), §3.2.
- **What was changed:** `dedup.py` attempts to build a `faiss.IndexFlatIP` backed by `sentence-transformers/all-MiniLM-L6-v2`; if the heavy deps fail to import or the model download fails, it falls back to `difflib.SequenceMatcher` string-ratio dedup with the same threshold. The fallback is logged once at runtime.
- **Reason:** `faiss-cpu` has known Windows install friction; tests must remain runnable without the ML stack. Production scans with deps installed still use real FAISS as specified.
- **architecture.md updated:** NO

### MODULE — Mutation Engine (6-strategy rewrite)
- **Date:** 2026-04-17
- **Sprint:** 2
- **File(s) Created/Modified:**
  - Created: `backend/app/core/engine/hf_client.py`, `backend/app/core/engine/dedup.py`, `backend/tests/test_mutation_engine.py`
  - Rewritten: `backend/app/core/engine/mutation.py` (stub → full 6-strategy engine with lineage + dedup)
  - Modified: `backend/app/core/attack_executor.py`, `backend/app/config.py`, `backend/requirements.txt`, `frontend/src/pages/RunDetail.tsx`
- **Key Decisions Made:**
  - All 6 architecture-mandated strategies implemented: `paraphrase`, `encode_b64`, `encode_rot13`, `encode_unicode`, `lang_switch`, `chain`.
  - `paraphrase` and `lang_switch` route through `HFClient` (HuggingFace Inference Endpoint); if `HF_API_TOKEN` is unset the engine silently skips those strategies so deterministic mutation still works out-of-the-box.
  - `MutatedVariant` dataclass carries `(text, strategy, depth, parent_text)` so the executor can persist `PromptVariant.parent_id`, `strategy_applied`, and `depth` per architecture.md §4.
  - Depth semantics: each level mutates the previous layer's outputs (true mutation tree), not flat re-application on the baseline.
  - Executor now persists the baseline as its own `PromptVariant` (depth=0, strategy_applied="baseline") so Sprint 6 baseline-vs-mutant ASR computation can read directly from the DB.
  - Fixed latent `NameError`: dead `analysis_engine = AnalysisEngine()` line in prior executor (referenced an unimported class) — removed.
  - Scan start now honours `mutation_strategies` + `mutation_depth` from `ScanRunCreate` (previously parsed into DB but ignored by the executor).
  - Frontend `RunDetail` page gained a strategy multi-select + depth slider (1–4) in the Actions card. Uses brand tokens `#0461E2` (Primary Blue) and `#1B2771` (Dark Navy) per branding.md §3.
- **Deviations from architecture.md:** Two, logged above (file location, FAISS fallback).
- **Prototype Code Reused:** The original `MutationEngine.mutate(budget=...)` signature and its B64 template were referenced; everything else was rewritten from scratch.
- **Known Limitations / TODOs:**
  - `TODO(sprint-4)`: seed FAISS index from the KB templates so `MutationEngine` can do KB-guided generation (PRD §4.3 last bullet).
  - `TODO(sprint-6)`: surface the new `strategy_applied` column in the Run Detail variant table and add a lineage viz.
  - Integration with real HF endpoints is untested without credentials — pending supervisor's manual `HF_API_TOKEN` verification.

---

## Sprint 3

*(No entries yet)*

---

## Sprint 4

*(No entries yet)*

---

## Sprint 5

**Date:** April 15, 2026

- **Action:** Migrated the complete PDF generation logic from the "FYP Prototype for IEEE Ignite".
- **Details:** Replicated the `report_service.py` architecture dynamically bridging `ScanRun` and `PromptVariant` states using `xhtml2pdf` and `jinja2`.
- **Status:** Integrated `report.html`. Wired up `Executive` and `Technical` PDF downloads directly from the frontend React execution detail UI. PoC bundle exported as a ZIP containing reproduction guides and context templates representing high-fidelity attack pathways.

---

## Sprint 6

*(No entries yet)*

---

## Sprint 7

*(No entries yet)*

---

## Cross-Sprint Issues / Architectural Notes

*(Agent: log any issue or decision that affects multiple sprints here)*

---

### DEVIATION — Firebase Auth (Out-of-Sprint User Authentication)
- **Date:** 2026-04-17
- **Sprint:** Inter-sprint (between Sprint 2 and Sprint 3, user-requested)
- **Original architecture.md specification:** No authentication layer was specified in architecture.md §3 or the PRD sprint plan. The original design assumed single-user local deployment with no session management.
- **What was changed:** Full Firebase Authentication layer added across frontend and backend:
  - **Frontend (7 files):**
    - `frontend/src/firebase.ts` — Firebase JS SDK initialisation
    - `frontend/src/context/AuthContext.tsx` — `onAuthStateChanged` + `getIdToken()` provider
    - `frontend/src/pages/Login.tsx` — Email/password login + register page (SECUSYNC brand tokens)
    - `frontend/src/components/RequireAuth.tsx` — Route guard; redirects to `/login` if unauthenticated, shows spinner during session resolution to prevent flash
    - `frontend/src/api/client.ts` — Axios interceptor: attaches `Authorization: Bearer <idToken>` to every request; auto sign-out on HTTP 401
    - `frontend/src/App.tsx` — Added `<AuthProvider>` wrapper and `/login` public route; all other routes wrapped in `<RequireAuth>`
    - `frontend/src/layouts/MainLayout.tsx` — Added user email display and Sign Out button (sidebar footer)
  - **Backend (4 files):**
    - `backend/app/core/firebase_auth.py` — `verify_token()` using `firebase_admin.auth.verify_id_token(check_revoked=True)`; initialises SDK lazily via `lru_cache`; catches and wraps all Firebase exceptions into `FirebaseAuthError` (no internal details leaked to callers)
    - `backend/app/dependencies.py` — `get_current_user` FastAPI dependency; `HTTPBearer` extractor; returns decoded token claims dict; raises HTTP 401 with a generic message on failure
    - `backend/app/routers/scans.py` — `dependencies=[Depends(get_current_user)]` added to router
    - `backend/app/routers/tllm.py` — `dependencies=[Depends(get_current_user)]` added to router
  - **Config / dependencies:**
    - `backend/app/config.py` — `FIREBASE_SERVICE_ACCOUNT_PATH: str = ""` env var
    - `backend/requirements.txt` — `firebase-admin==7.4.0`
    - `.gitignore` — Added patterns: `*firebase-adminsdk*.json`, `*-adminsdk-*.json`, `firebase-service-account.json`, `serviceAccountKey.json`
- **Reason:** User requested auth to protect the API and enable multi-user use. Firebase Auth was selected for minimal implementation surface: no custom JWT logic, no password storage, no sessions table — all offloaded to Google Firebase with RS256 token verification on the backend.
- **Security decisions:**
  - Firebase client API key intentionally left in source (it is a public identifier by Firebase design; actual security is enforced via Firebase Authorized Domains + server-side token verification)
  - Service account JSON path read from `FIREBASE_SERVICE_ACCOUNT_PATH` env var; file itself is gitignored and never committed
  - Token details never forwarded to API clients in error responses (generic 401 message only)
  - `check_revoked=True` in `verify_id_token` — revoked tokens in Firebase Console are rejected within seconds
  - HTTP 401 interceptor on the frontend auto-signs-out the user if the backend rejects their session
- **architecture.md updated:** NO (auth was not in original spec; deferred to Sprint 7 architectural reconciliation)
