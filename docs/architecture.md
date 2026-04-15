# SECUSYNC — Architecture Document

**Version:** 1.0  
**Last Updated:** April 2026  

---

## 1. High-Level Architecture

SECUSYNC follows a client-server architecture with a clear separation between the React frontend, the FastAPI backend, and external/local LLM services.

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (React)                          │
│  Dashboard │ New Scan │ Live View │ Run History │ Reports │ KB  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST + WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                             │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  │
│  │  TLLM    │  │  Mutation    │  │  Hybrid    │  │  Report  │  │
│  │  Config  │  │  Engine      │  │  Analysis  │  │  Generator│  │
│  └──────────┘  └──────────────┘  └────────────┘  └──────────┘  │
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────────────┐   │
│  │  Attack Executor     │   │  Knowledge Base (FAISS)      │   │
│  └──────────────────────┘   └──────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Database  (SQLite dev / PostgreSQL-compatible schema)   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────┬────────────────────────────────┬────────────────────┘
           │                                │
   ┌───────▼──────────┐          ┌──────────▼─────────────┐
   │   Target LLM     │          │  HuggingFace Inference  │
   │   (TLLM)         │          │  Endpoint (Analysis LLM)│
   │                  │          │                         │
   │  • OpenAI API    │          │  • Semantic judge model │
   │  • Anthropic API │          │  • Paraphrase model     │
   │  • Ollama local  │          └─────────────────────────┘
   │  • Custom REST   │
   └──────────────────┘
```

---

## 2. Repository Structure

```
secusync/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Environment config (pydantic-settings)
│   │   ├── database.py              # SQLAlchemy session setup
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── tllm_profile.py
│   │   │   ├── scan_run.py
│   │   │   ├── prompt_variant.py
│   │   │   └── kb_entry.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   │   ├── tllm.py
│   │   │   ├── scan.py
│   │   │   └── kb.py
│   │   ├── routers/                 # FastAPI route handlers
│   │   │   ├── tllm.py
│   │   │   ├── scans.py
│   │   │   ├── reports.py
│   │   │   └── kb.py
│   │   ├── core/                    # Business logic modules
│   │   │   ├── tllm_connector.py    # Unified TLLM API client
│   │   │   ├── mutation_engine.py   # Prompt mutation strategies
│   │   │   ├── attack_executor.py   # Orchestrates scan pipeline
│   │   │   ├── analysis/
│   │   │   │   ├── deterministic.py # Regex-based detectors
│   │   │   │   ├── semantic.py      # HuggingFace judge client
│   │   │   │   └── hybrid.py        # Combines both layers
│   │   │   ├── knowledge_base.py    # FAISS KB interface
│   │   │   └── report_generator.py  # PDF report builder
│   │   └── utils/
│   │       ├── redactor.py          # Sanitizes sensitive output before logging
│   │       └── logger.py            # Structured logging setup
│   ├── tests/
│   │   ├── test_mutation_engine.py
│   │   ├── test_deterministic.py
│   │   ├── test_hybrid_analysis.py
│   │   ├── test_attack_executor.py
│   │   └── test_report_generator.py
│   ├── kb_data/                     # Seed data for knowledge base
│   │   └── attack_templates.json
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── NewScan.tsx
│   │   │   ├── LiveRun.tsx
│   │   │   ├── RunHistory.tsx
│   │   │   ├── RunDetail.tsx
│   │   │   ├── KnowledgeBase.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── scan/
│   │   │   ├── reports/
│   │   │   └── common/
│   │   ├── hooks/
│   │   │   ├── useScans.ts
│   │   │   ├── useLiveRun.ts        # WebSocket hook
│   │   │   └── useKB.ts
│   │   ├── store/
│   │   │   └── uiStore.ts           # Zustand UI state
│   │   ├── api/
│   │   │   └── client.ts            # Typed axios API client
│   │   └── types/
│   │       └── index.ts             # Shared TypeScript types
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── Rules.md
│   ├── Plan.md
│   └── History.md
│
├── docker-compose.yml
└── README.md
```

---

## 3. Module Specifications

### 3.1 TLLM Connector (`core/tllm_connector.py`)

**Purpose:** Unified client that abstracts over all supported TLLM providers.

**Interface:**
```python
class TLLMConnector:
    def __init__(self, profile: TLLMProfile): ...
    async def send(self, prompt: str, conversation_history: list = []) -> TLLMResponse: ...
```

**Supported providers (selected via `profile.provider`):**
- `openai` — uses `openai` Python SDK
- `anthropic` — uses `anthropic` Python SDK
- `ollama` — uses Ollama REST API (`http://localhost:11434`)
- `custom` — uses `httpx` to POST to `profile.endpoint_url`

**Error handling:** All providers raise a unified `TLLMConnectionError` on failure.

---

### 3.2 Mutation Engine (`core/mutation_engine.py`)

**Purpose:** Takes a baseline prompt and generates N mutated variants.

**Strategies (applied in order, configurable):**

| Strategy ID | Name | Method |
|---|---|---|
| `paraphrase` | Semantic Paraphrase | HuggingFace Inference Endpoint (paraphrase model) |
| `encode_b64` | Base64 Encoding | stdlib `base64` |
| `encode_rot13` | ROT13 | stdlib `codecs` |
| `encode_unicode` | Unicode Obfuscation | character substitution map |
| `lang_switch` | Language Switching | HuggingFace translation endpoint |
| `chain` | Multi-Step Chaining | Splits payload across 2-3 turns |

**Interface:**
```python
class MutationEngine:
    def __init__(self, kb: KnowledgeBase, hf_client: HFClient): ...
    async def mutate(self, baseline: str, strategies: list[str], depth: int) -> list[PromptVariant]: ...
```

**Each `PromptVariant` tracks:** parent prompt ID, strategy applied, generation depth.

**Deduplication:** FAISS cosine similarity check — if a new variant is > 0.95 similar to an existing one, it is discarded.

---

### 3.3 Attack Executor (`core/attack_executor.py`)

**Purpose:** Orchestrates the full pipeline for a scan run.

**Pipeline:**
```
1. Load TLLM profile
2. Load baseline prompts for selected attack classes from KB
3. For each baseline prompt:
   a. Run Mutation Engine → list of variants
   b. For each variant:
      i.  Send to TLLM via TLLMConnector
      ii. Store raw response (locally)
      iii. Run Hybrid Analysis on response
      iv. Store verdict + evidence
      v.  Stream update to frontend via WebSocket
4. Aggregate results for run
5. Trigger Report Generator
```

**Rate limiting:** configurable `delay_ms` between requests, default 500ms.

---

### 3.4 Hybrid Analysis (`core/analysis/`)

#### Deterministic Layer (`deterministic.py`)
Regex patterns checked against every TLLM response:

| Pattern Name | Regex / Logic | Maps To |
|---|---|---|
| API Key (OpenAI) | `sk-[A-Za-z0-9]{20,}` | Sensitive Disclosure |
| API Key (Google) | `AIza[A-Za-z0-9_-]{35}` | Sensitive Disclosure |
| Bearer Token | `Bearer\s+[A-Za-z0-9\-._~+/]+=*` | Sensitive Disclosure |
| System Prompt Echo | Match against known system prompt (if provided) | Prompt Leakage |
| PII — Email | Standard RFC 5322 email regex | Sensitive Disclosure |
| PII — Phone | Common phone number patterns | Sensitive Disclosure |
| Injection Confirmation | Configurable marker strings per attack class | Prompt Injection |

#### Semantic Layer (`semantic.py`)
- Sends **redacted** response to HuggingFace Inference Endpoint
- System prompt to judge: classifies into `LEAKED | INJECTED | DISCLOSED | BENIGN | UNCERTAIN`
- Never sends raw secrets — redactor runs before this step

#### Hybrid Combiner (`hybrid.py`)
- If deterministic = MATCH → verdict is `VULNERABLE` regardless of semantic
- If deterministic = NO_MATCH and semantic = `LEAKED/INJECTED/DISCLOSED` → verdict is `VULNERABLE`
- If both = negative → `NOT_VULNERABLE`
- If semantic = `UNCERTAIN` → `NEEDS_REVIEW`

---

### 3.5 Knowledge Base (`core/knowledge_base.py`)

**Storage:** FAISS index on disk + SQLite metadata table.

**Interface:**
```python
class KnowledgeBase:
    def search(self, query: str, top_k: int = 5) -> list[KBEntry]: ...
    def add(self, entry: KBEntry) -> None: ...
    def seed_from_file(self, path: str) -> None: ...
```

**Entry schema:**
```json
{
  "id": "uuid",
  "attack_class": "prompt_injection | system_prompt_leakage | file_poisoning | sensitive_disclosure",
  "title": "string",
  "template": "string (the prompt template)",
  "tags": ["owasp", "rag", ...],
  "source": "OWASP | HOUYI | GPTFuzzer | custom"
}
```

---

### 3.6 Report Generator (`core/report_generator.py`)

**Library:** `reportlab` or `weasyprint` (to be decided during Sprint 4).

**Executive Report sections:**
1. Cover page (run ID, date, TLLM profile name)
2. Executive Summary (vulnerability count by class, overall risk rating)
3. Risk Matrix (Critical/High/Medium/Low breakdown)
4. Top Findings (max 5, plain-language descriptions)
5. Recommended Remediations

**Technical Report sections:**
1. Cover page
2. Methodology (attack classes, mutation strategies used)
3. Metrics (ASR, mutation efficiency, detection precision/recall)
4. Full findings table (variant ID, attack class, strategy, verdict, evidence)
5. Reproducible PoC bundles per finding
6. Redacted raw responses
7. HOUYI / GPTFuzzer comparison table

---

## 4. Data Models

### ScanRun
```
id: UUID
tllm_profile_id: UUID
status: PENDING | RUNNING | COMPLETED | FAILED
attack_classes: list[str]
mutation_strategies: list[str]
mutation_depth: int
created_at: datetime
completed_at: datetime | null
total_prompts_sent: int
vulnerabilities_found: int
```

### PromptVariant
```
id: UUID
scan_run_id: UUID
parent_id: UUID | null
attack_class: str
strategy_applied: str
depth: int
prompt_text: str
response_text: str (stored, never externally transmitted raw)
verdict: VULNERABLE | NOT_VULNERABLE | NEEDS_REVIEW
deterministic_matches: list[str]
semantic_classification: str
created_at: datetime
```

### TLLMProfile
```
id: UUID
name: str
provider: openai | anthropic | ollama | custom
endpoint_url: str | null
api_key_ref: str (reference to encrypted store, not raw key)
system_prompt: str | null
has_rag: bool
accepts_documents: bool
accepts_multimodal: bool
created_at: datetime
```

---

## 5. API Contract (Key Endpoints)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/tllm/profiles` | Create TLLM profile |
| `GET` | `/api/tllm/profiles` | List all profiles |
| `POST` | `/api/scans/start` | Start a new scan run |
| `GET` | `/api/scans/{run_id}` | Get run status + summary |
| `WS` | `/api/scans/{run_id}/stream` | Live WebSocket stream of run progress |
| `GET` | `/api/scans/{run_id}/results` | Full results (all variants + verdicts) |
| `GET` | `/api/reports/{run_id}/executive` | Download executive PDF |
| `GET` | `/api/reports/{run_id}/technical` | Download technical PDF |
| `GET` | `/api/kb/entries` | List KB entries |
| `POST` | `/api/kb/entries` | Add KB entry |
| `DELETE` | `/api/kb/entries/{id}` | Remove KB entry |

---

## 6. Frontend State Architecture

```
Server State (React Query):
  - tllmProfiles
  - scanRuns (list)
  - scanRun (detail by ID)
  - kbEntries

UI State (Zustand):
  - activeScanRunId
  - sidebarOpen
  - currentPage

WebSocket State (custom hook):
  - liveRunEvents[]   ← streamed from backend during active scan
  - connectionStatus
```

---

## 7. Security Architecture

- API keys stored in environment variables only, never in database
- API key references in DB are opaque tokens resolved at runtime
- Raw TLLM responses stored in backend DB, never forwarded externally
- Redactor runs on all responses before semantic analysis
- All scan logs redact secrets before writing to disk
- Ethical guard: TLLM profiles require explicit `authorized: true` flag before a scan can start

---

## 8. Technology Stack Summary

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Zustand, React Query |
| Backend | Python 3.10+, FastAPI, SQLAlchemy, Pydantic v2 |
| Database | SQLite (dev), PostgreSQL-compatible schema |
| Vector Store | FAISS |
| LLM Clients | openai SDK, anthropic SDK, httpx (Ollama/custom) |
| Analysis LLM | HuggingFace Inference Endpoints |
| NLP Utilities | sentence-transformers, NLTK |
| PDF Reports | reportlab / weasyprint |
| Containerization | Docker + docker-compose |
| Testing | pytest (backend), Vitest (frontend) |
