# SECUSYNC — Agent Rules

**For:** Antigravity AI Coding Agent  
**Version:** 1.0  
**These rules are NON-NEGOTIABLE and apply for the entire lifetime of this project.**

---

## RULE 0 — Read First, Code Second

Before writing a single line of code for any task:
1. Read `PRD.md` — confirm the feature you are building is in scope
2. Read `architecture.md` — confirm where the file belongs, what it is named, and what interface it must implement
3. Read `Plan.md` — confirm which sprint you are in and what is allowed in this sprint
4. Read `History.md` — check if a similar problem was solved before
5. Read `branding.md` — if producing any UI, report, or visual output, confirm it follows brand guidelines

If any of the above files are missing, STOP and report the missing file. Do not proceed.

---

## RULE 1 — Language and Naming

- All code, comments, variable names, function names, class names, and documentation must be in **English only**
- File names use `snake_case` for Python, `PascalCase` for React components, `camelCase` for TypeScript utilities
- No abbreviations in names unless they are industry-standard (e.g., `id`, `url`, `api`, `llm`, `kb`)
- Never use single-letter variable names except for loop counters (`i`, `j`) and mathematical variables

---

## RULE 2 — File and Folder Discipline

- Every new file must match the location defined in `architecture.md`
- Never create files outside the defined structure without first documenting the deviation in `History.md`
- Never delete a file without first checking if it is imported anywhere
- Configuration files (`.env`, secrets) are never committed — use `.env.example` only

---

## RULE 3 — Module Boundaries

- Each module in `backend/app/core/` must have a single, clear responsibility
- Modules must not import from each other in circular ways
- The `tllm_connector.py` must be the **only** file that communicates with external TLLM APIs
- The `semantic.py` analysis module must be the **only** file that calls the HuggingFace Inference Endpoint
- The `redactor.py` utility must be called on all TLLM raw responses **before** they are passed to any external service or logged to disk

---

## RULE 4 — Security Non-Negotiables

- **Never** log raw API keys, bearer tokens, or secrets to any file or console output
- **Never** send raw TLLM responses to any external service — always run `redactor.py` first
- **Never** hardcode credentials — all secrets must come from environment variables via `config.py`
- Every TLLM profile must have `authorized: true` checked before a scan is executed
- If a scan is started against a profile with `authorized: false`, raise a `UnauthorizedScanError` and abort

---

## RULE 5 — Test Coverage

- Every module in `backend/app/core/` must have a corresponding test file in `backend/tests/`
- Minimum test coverage target: **80%** per module
- Tests must be runnable with `pytest` from the `backend/` directory without any manual setup beyond installing requirements
- When fixing a bug, write the regression test **first**, confirm it fails, then fix the bug, then confirm it passes
- Do not ship a module without at least: one happy-path test, one edge-case test, and one failure-mode test

---

## RULE 6 — Incremental Development (Agile)

- Only implement features that belong to the **current sprint** as defined in `Plan.md`
- If a future-sprint feature is tempting to add early, note it as a `TODO(sprint-N):` comment and move on
- Each sprint must end with a working, runnable product — no half-built states at sprint boundaries
- Do not refactor code from a previous sprint unless a bug demands it — note the refactor in `History.md`

---

## RULE 7 — History.md Maintenance

Update `History.md`:
- **After completing any module** — log what was built, key decisions made, any deviations from architecture
- **After fixing any bug** — log bug type, root cause, how it was fixed (see History.md format)
- **After each sprint** — log sprint summary: what was completed, what was skipped, current known issues
- **After any architecture deviation** — log what changed and why

The agent must ask itself the following **End-of-Sprint Validation Questions** and record answers in `History.md`:
1. Does the current build satisfy all acceptance criteria listed in `PRD.md` for this sprint's features?
2. Do all new modules follow the interfaces defined in `architecture.md`?
3. Do all new API endpoints match the contract in `architecture.md` Section 5?
4. Does the frontend correctly consume all new backend endpoints?
5. Are all new modules covered by tests at ≥ 80%?
6. Are there any security violations (raw secrets logged, raw responses sent externally)?
7. Is the app runnable end-to-end right now?

---

## RULE 8 — API Contract Compliance

- Every backend endpoint must match the method, path, and response shape defined in `architecture.md` Section 5
- Never change an existing endpoint's path or response schema without updating `architecture.md` first
- All request/response schemas must be defined as Pydantic models in `backend/app/schemas/`
- The frontend API client (`frontend/src/api/client.ts`) must always reflect the current backend contract

---

## RULE 9 — No Silent Failures

- All async functions in the backend must have `try/except` blocks with meaningful error messages
- All TLLM connector errors must raise typed exceptions (`TLLMConnectionError`, `TLLMRateLimitError`, etc.)
- The frontend must display user-visible error states for all failed API calls — never fail silently
- Background scan tasks must update the `ScanRun.status` to `FAILED` with an error message if they crash

---

## RULE 10 — Prototype Reference Policy

The prototype at `https://github.com/AosawnX/Secusync-LLM-Security-Testing-Toolkit` is a **reference only**.
- You may read its logic and adapt patterns
- You may NOT copy-paste code blocks directly without reviewing them for correctness and security
- The prototype used Groq/Llama 3.3 as the judge — the new system uses HuggingFace Inference Endpoints
- The prototype used TypeScript for the backend config files — the new system uses Python FastAPI only
- Any pattern reused from the prototype must be noted in `History.md`

---

## RULE 11 — Ethical Testing Guard

- Never generate scan configurations or attack prompts targeting systems the user does not own or have written authorization for
- The system must display an explicit authorization acknowledgment before any scan starts
- All PoC bundles in reports must include a responsible disclosure notice

---

## RULE 12 — Commit Hygiene

- Commit messages follow: `[SPRINT-N] <module>: <short description>`
  - Example: `[SPRINT-2] mutation_engine: add base64 encoding strategy`
- One logical change per commit — no "fixed stuff" commits
- Never commit broken code to `main` — use feature branches per sprint

---

## RULE 13 — Dependency Discipline

- Add a dependency to `requirements.txt` only when it is actually used
- Before adding a new Python package, check if the functionality already exists in the stdlib or an already-installed package
- Pin all dependency versions in `requirements.txt`
- Document why each non-obvious dependency was chosen in a comment next to it

---

## RULE 15 — Report.md Maintenance

`Report.md` is the living FYP software product report. The agent must:
- After completing each sprint, fill in the corresponding subsection in **Section 7** of `Report.md` with actual outcomes, decisions made, and deviations from plan
- When a trade-off decision is made (e.g., choosing a library, picking a model), add an entry to **Section 6.1** (Master Trade-off Log) immediately — not retroactively
- When a sprint's Exit Criteria are met, update **Section 5.2** (SDLC Work Products table) to mark the relevant rows ✅
- When tests are written, update **Section 8.2** (Test Coverage Report) with the actual coverage numbers
- When benchmarks are run (Sprint 7), populate **Section 10** with real measured data
- Never delete or overwrite prior entries — this is an append-only log
- Sections marked 🔲 are pending; sections marked ✅ are complete

## RULE 16 — Branding Compliance

All visual outputs must follow `branding.md`:
- UI components use the exact color hex values from branding.md Section 3
- Verdict badges use the exact color combinations from branding.md Section 5
- PDF reports use the layout, typography, and color rules from branding.md Sections 7
- The SECUSYNC logo (mark + wordmark) appears on all report cover pages
- No new colors, fonts, or icon libraries may be introduced without updating branding.md first

Before the final sprint (Sprint 7), verify:
- [ ] All 4 attack classes produce findings against the test TLLM harness
- [ ] Mutation Engine ASR > baseline ASR (documented with numbers)
- [ ] Executive and Technical PDF reports generate without errors
- [ ] Dashboard displays all metrics from PRD Section 5
- [ ] HOUYI/GPTFuzzer comparison table exists in the technical report
- [ ] The full scan cycle works via Web UI with zero terminal interaction
- [ ] The app runs with `docker-compose up` in under 2 minutes
