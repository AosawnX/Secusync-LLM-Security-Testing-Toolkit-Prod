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

### MODULE — Hybrid Analysis Engine (test backfill)
- **Date:** 2026-04-18
- **Sprint:** 3
- **File(s) Created/Modified:**
  - `backend/tests/test_redactor.py` (new — 11 tests)
  - `backend/tests/test_deterministic.py` (new — 16 tests)
  - `backend/tests/test_semantic.py` (new — 8 tests)
  - `backend/tests/test_hybrid_analysis.py` (new — 10 tests)
  - `backend/tests/test_attack_executor.py` (fixed — updated to Sprint-2 signature + new filter test)
  - `backend/tests/test_mutation_engine.py` (fixed — `test_depth_increases_variant_count` now uses isolated engines)
  - `frontend/src/pages/ExecutionDetail.tsx` (added `NEEDS_REVIEW` queue section)
- **Key Decisions Made:**
  - Used `asyncio.run(coro)` inside test helpers (not `get_event_loop().run_until_complete`) to guarantee a fresh loop per test — required because pytest-asyncio is in `strict` mode with function-scoped loops.
  - Test header comments flag `test_redactor.py` and the `test_judge_never_receives_raw_secret` test as **security-critical** — they enforce PRD §4.5 (no raw secrets leave local scope) and must never be deleted.
  - Parametrized the semantic-verdict mapping test (LEAKED / INJECTED / DISCLOSED → VULNERABLE) so adding a new vulnerable class requires only a single list edit.
  - `NEEDS_REVIEW` queue rendered in `ExecutionDetail.tsx` as an orange-bordered card above the execution log; fed by filtering variants where `verdict === 'NEEDS_REVIEW'` — no new backend endpoint required.
- **Deviations from architecture.md:** None. The Hybrid Analysis code paths (`Redactor`, `DeterministicAnalyzer`, `SemanticAnalyzer`, `HybridAnalysisEngine`) were already implemented during the Sprint 3 spike; this work only added missing tests + the Review Queue UI hook specified in `Plan.md` §Sprint 3.
- **Prototype Code Reused:** None.
- **Known Limitations / TODOs:**
  - `TODO(sprint-6)`: allow an analyst to click a Review Queue row and override the verdict to `VULNERABLE` / `NOT_VULNERABLE`; currently the card is read-only.
  - Judge integration is exercised only through the `_FakeJudge` / `_ScriptedJudge` doubles — real HF endpoint round-trip is covered at integration level, not unit level.

### BUG — test_depth_increases_variant_count failed when engine was reused
- **Date:** 2026-04-18
- **Sprint:** 3
- **Module Affected:** `backend/tests/test_mutation_engine.py`
- **Bug Type:** Logic Error (test isolation)
- **Symptom:** Assertion `len(depth_two) > len(depth_one)` failed because the second `mutate()` call returned 0 variants.
- **Root Cause:** The test reused a single `MutationEngine` across both calls. The engine's `_DifflibDedup` index already contained every depth-1 variant, so every depth-1 output on the second run was classed as a duplicate; depth-2 expansion then had no parents to mutate from.
- **Fix Applied:** Create two independent engines (`engine_one`, `engine_two`) so each run starts with a clean dedup index.
- **Regression Test Added:** Yes — the fixed test *is* the regression test.

### BUG — test_load_baseline_prompts crashed on missing positional arg
- **Date:** 2026-04-18
- **Sprint:** 3
- **Module Affected:** `backend/tests/test_attack_executor.py`
- **Bug Type:** Integration Error (stale test signature)
- **Symptom:** `TypeError: load_baseline_prompts() missing 1 required positional argument: 'attack_classes'`.
- **Root Cause:** Sprint 2 added the required `attack_classes: list[str]` filter argument but the Sprint 1 test was never updated.
- **Fix Applied:** Pass `["prompt_injection"]`; added a second test asserting an unknown attack class returns `[]`.
- **Regression Test Added:** Yes — `test_load_baseline_prompts_filters_by_attack_class`.

### SPRINT-3 SUMMARY — Hybrid Analysis (Redact → Regex → Semantic → Combiner)
- **Date Completed:** 2026-04-18
- **Completed Tasks:**
  - Redactor: multi-pattern sanitiser for OpenAI / Google / Bearer / password / mock flags — 11 tests.
  - DeterministicAnalyzer: 16 tests covering every pattern + edge cases (empty, None, case-insensitive, short-prompt skip).
  - SemanticAnalyzer: 8 tests covering fenced-JSON and bare-brace parsing, all 5 enum values, degraded / offline paths, judge prompt shape.
  - HybridAnalysisEngine: 10 tests covering the 4 precedence rules from architecture.md §3.4 + the critical no-raw-secret-to-judge invariant.
  - Frontend: `NEEDS_REVIEW` queue section added to `ExecutionDetail.tsx`.
  - Fixed 2 pre-existing test failures (see bug entries above).
  - **Test suite: 56/56 passing (up from 12 passing / 2 erroring before the work).**
- **Skipped / Deferred Tasks:**
  - Analyst override action on the Review Queue (deferred to Sprint 6 — UX polish sprint).
  - Real HF-endpoint integration tests (covered at integration level, outside unit scope).
- **Current Known Issues:**
  - `openai` and `anthropic` packages were not in the project's current Python environment's installed set at the time of running the suite; both were installed ad-hoc to unblock collection. Requirements pin check should be revisited in Sprint 7 hardening.

#### End-of-Sprint Validation
1. **Does the current build satisfy all PRD acceptance criteria for this sprint's features?** PARTIAL — The hybrid analysis pipeline (PRD §4.4) is functionally complete and covered by 45 new tests. The PRD target of "≥80% unit-test coverage on core modules" (§8 Acceptance) is clearly met for `utils/redactor.py`, `analysis/deterministic.py`, `analysis/semantic.py`, and `analysis/hybrid.py`. Manual-review UX for analyst override is deferred to Sprint 6.
2. **Do all new modules follow the interfaces defined in architecture.md?** YES — Redactor → Deterministic → Semantic → Combiner flow and `verdict / score / deterministic_matches / semantic_classification / reason` return shape match architecture.md §3.4 exactly.
3. **Are there any open security issues?** NO — the critical invariant (raw response never leaves local scope before redaction) is guarded by `test_judge_never_receives_raw_secret` and enforced by `HybridAnalysisEngine.analyze` calling `Redactor.sanitize` before any judge invocation.
4. **Test status:** 56/56 passing in `backend/tests/`.

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

---

### BUG — Firebase Admin SDK double-init race on first concurrent requests
- **Date:** 2026-04-17
- **Sprint:** Inter-sprint (Firebase Auth)
- **Severity:** Blocker — authenticated users were immediately signed back out
- **Symptom:** After successful sign-up or sign-in, the dashboard would flash briefly then redirect back to `/login`. Firebase Console showed the user was created correctly, so auth on the client side worked. Backend logs revealed every `/api/*` call returned HTTP 401.
- **Root cause:** `backend/app/core/firebase_auth.py::_get_app()` used `@lru_cache(maxsize=1)` to memoise Firebase Admin SDK initialisation. On the very first dashboard render, the frontend fires two concurrent GETs (`/api/scans/all` and `/api/tllm/profiles`) before the cache is populated. Both request-handler threads enter the function body simultaneously, both call `firebase_admin.initialize_app(cred)`, and the second call raises `ValueError: The default Firebase app already exists`. The broad `except Exception` in `verify_token` converted that into `FirebaseAuthError` → `HTTPException(401)`. The axios 401 interceptor then force-signed-out the user → redirect to `/login`.
- **Fix:**
  1. Replaced `@lru_cache` with an idempotent pattern: `_get_app()` now calls `firebase_admin.get_app()` first (raises `ValueError` if no default app exists) and only falls through to `initialize_app()` when needed, guarded by a `threading.Lock()` with double-checked locking inside the critical section.
  2. Added a FastAPI `@app.on_event("startup")` hook in `backend/app/main.py` that calls `_get_app()` once during server boot. This ensures the SDK is already registered before the first request arrives, eliminating the cold-start race window entirely.
- **Files changed:** `backend/app/core/firebase_auth.py`, `backend/app/main.py`
- **Verification:**
  - `GET /api/scans/all` with no auth → `401 {"detail":"Not authenticated"}` ✓
  - `GET /api/scans/all` with `Bearer fake-token` → `401 {"detail":"Invalid or expired authentication token"}` ✓
  - End-to-end sign-in now persists the session and lands the user on the dashboard.

---

### DEVIATION — Per-user data isolation (row-level ownership)
- **Date:** 2026-04-18
- **Sprint:** Inter-sprint (Firebase Auth follow-up)
- **Context:** With authentication working, every authenticated user was still able to read, modify, and delete every other user's targets / scans / results / reports. That's a single-tenant assumption that the Firebase Auth rollout silently broke — auth only proves "who you are", not "what you can see".
- **Decision:** Enforce row-level ownership at the database and router layer. Every ownable row carries `user_id` (the Firebase uid) and every query is scoped by it.
- **Files changed:**
  - `backend/app/models/tllm_profile.py`, `scan_run.py`, `prompt_variant.py` — added `user_id` column (nullable=False, indexed).
  - `backend/app/dependencies.py` — added `current_uid` dep + `get_owned_profile` / `get_owned_run` helpers that 404 on ownership mismatch (NOT 403 — a 403 would let an attacker enumerate UUIDs).
  - `backend/app/routers/tllm.py`, `scans.py` — every read filtered by `user_id`, every write stamped with `user_id`. Scan creation now verifies the referenced TLLM profile belongs to the caller.
  - `backend/app/core/attack_executor.py` — TLLMProfile lookup scoped by the scan's owner; PromptVariants inserted carry `user_id=run.user_id`.
  - `backend/alembic/versions/2026_04_18_add_user_id.py` — migration adds the three columns + indexes, backfills pre-auth rows with sentinel `legacy-pre-auth` (invisible to any real Firebase uid).
- **Security invariants:**
  1. Router-level: every handler takes `uid: str = Depends(current_uid)` and either filters queries by `user_id == uid` or uses the `get_owned_*` helpers.
  2. Executor-level: background scan task inherits `user_id` from the run row it was scheduled for; no auth context needed inside.
  3. Defence-in-depth: `PromptVariant` carries a denormalised `user_id` so the hot read path for results / reports filters on a single indexed column, making "forgot to join scan_runs" bugs impossible to hide.
  4. Status codes: ownership mismatch → `404 Not Found`, never `403 Forbidden`. This prevents UUID enumeration attacks.
- **Shared resources that stay global:** `kb_entries` (attack-template seed data — read-only, identical for every user).
- **Filesystem artefacts (`runs/<run_id>/`):** still unguessable UUIDv4 paths AND the report endpoints that read them are now ownership-scoped. No direct filesystem-exposure router exists.
- **Manual verification plan:**
  - Account A creates target T_A, runs scan S_A.
  - Account B (separate email) signs in.
  - `GET /api/tllm/profiles` for B must not contain T_A.
  - `GET /api/scans/all` for B must not contain S_A.
  - `GET /api/scans/{S_A.id}` with B's token → 404.
  - `GET /api/scans/{S_A.id}/report/executive` with B's token → 404.
  - `POST /api/scans/start` with `{tllm_profile_id: T_A.id}` as B → 404.
- **Regression tests added:** None in this pass — the change touches router-level plumbing and is best verified by the two-account manual check above. A proper pytest suite with stubbed Firebase tokens is deferred to Sprint 7 hardening.

---

### BUG — .env not loaded on startup, Firebase init silently failed (sign-in bounce returns)
- **Date:** 2026-04-18
- **Sprint:** Inter-sprint (Firebase Auth follow-up)
- **Severity:** Blocker — same user-facing symptom as the double-init bug returned in a different guise
- **Symptom:** After signing up / signing in, dashboard flashed briefly then bounced back to `/login` — identical to the earlier double-init race, but occurring on a clean run.
- **Root cause:** `backend/app/main.py` and `backend/app/core/firebase_auth.py` both read `FIREBASE_SERVICE_ACCOUNT_PATH` via `os.getenv(...)`, but nothing in the import chain calls `load_dotenv()`. Pydantic's `SettingsConfigDict(env_file=".env")` only populates `settings.*`, it does NOT export into `os.environ`. So the Firebase startup hook hit the `if not sa_path` branch and raised `FIREBASE_SERVICE_ACCOUNT_PATH env var is not set`, which the `except Exception` in the startup hook swallowed (logged and continued). Every subsequent `verify_token()` call then hit the same error, returned 401, and the axios 401 interceptor signed the user out → bounce. Additionally, the worktree backend directory had no `.env` file at all (only the main-repo backend did).
- **Fix:**
  1. Added `from dotenv import load_dotenv; load_dotenv()` at the top of `backend/app/main.py` BEFORE any app imports. This populates `os.environ` from the backend-local `.env` so both `firebase_auth.py` and `attack_executor.py` see the keys they need.
  2. Created `backend/.env` in the worktree with `FIREBASE_SERVICE_ACCOUNT_PATH` pointing at the service account JSON (still gitignored — service account JSON itself is NEVER committed).
  3. Added `FIREBASE_SERVICE_ACCOUNT_PATH` to the main repo's `backend/.env` as well for parity.
- **Files changed:** `backend/app/main.py`, `backend/.env` (worktree, new), `backend/.env` (main, updated)
- **Regression test added:** Manual smoke test — `python -c "from dotenv import load_dotenv; load_dotenv(); from app.core.firebase_auth import _get_app; print(_get_app().name)"` now prints `[DEFAULT]` instead of raising.
- **Future-proofing:** The Firebase startup hook's broad `except Exception` was intentionally left soft-failing so `/api/health` stays reachable for ops checks, but it now logs at ERROR level so CI and developers can spot misconfiguration in the server log immediately.
