# Agentic Fintech Demo

An opinionated, batteries‑included **agentic system** for ideating and validating **fintech partnership ideas**.  
It combines **LLM‑powered agents**, a lightweight **RAG** (retrieval‑augmented generation) over a local knowledge base, and **short/long‑term memory** to produce structured partnership briefs.

---

## ✨ What this project does

- **Coordinator + Specialist agents** (research, strategy, compliance/risk, writer) to synthesize a partnership proposal.
- **RAG over local Markdown notes** (e.g., compliance snippets, competitive landscape) via a directory search tool.
- **Short memory**: pulls relevant snippets from `knowledge/` during a run.
- **Long‑term memory (SQLite)**: persists key facts across runs in a local SQLite database (e.g., `memory.db`).
- **Deterministic, scriptable output**: writes a Markdown report you can share.

---

## 🧱 Project layout

```
agenticfintechdemo/
├─ knowledge/                # Local notes used for RAG (md files)
│  ├─ compliance_snippets.md
│  └─ competitive_landscape.md
├─ agents.py                 # Agent roles & definitions
├─ tasks.py                  # Task templates and orchestration steps
├─ rag_tool.py               # Directory search/RAG helper
├─ memory.py                 # Short/long-term memory utilities (SQLite)
├─ config.py                 # Centralized configuration/env handling
├─ main.py                   # CLI entry point (with 'run' subcommand)
└─ requirements.txt          # Python deps
```

---

## 🔧 Requirements

- Python **3.10+**
- **Environment variables**
  - `OPENAI_API_KEY` — for LLM calls
  - `SERPER_API_KEY` — for web search via Serper (required)
- Internet access (for web search)
- (Optional) Git for cloning

---

## 🚀 Quick start

```bash
# 1) Clone and enter
git clone https://github.com/ozcankasal/agenticfintechdemo
cd agenticfintechdemo

# 2) Create & activate a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Configure environment
export OPENAI_API_KEY="sk-..."             # Windows PowerShell: setx OPENAI_API_KEY "sk-..."
export SERPER_API_KEY="serper_xxx"         # Windows PowerShell: setx SERPER_API_KEY "serper_xxx"

# 5) Run — use the explicit 'run' subcommand
python main.py run --topic "Open Banking partnerships"
```

**Output:** a Markdown report is generated (commonly `outputs/<timestamp>_partnership_report.md`).  
**State:** long‑term memory is stored in a local SQLite file (e.g., `memory.db`).

---

## 🧠 How it works (architecture)

```
                 ┌──────────────────────────────────────────────────┐
                 │                   main.py                         │
                 │     (CLI: 'run' parses args & wiring)            │
                 └─────────────────┬────────────────────────────────┘
                                   │
         ┌─────────────────────────▼─────────────────────────┐
         │                   agents.py                       │
         │  - Coordinator / Research / Strategy / Writer     │
         │  - Compliance & Risk advisors                     │
         └─────────────────────────┬─────────────────────────┘
                                   │ invokes tasks
         ┌─────────────────────────▼─────────────────────────┐
         │                    tasks.py                       │
         │  - Research market & competitor context           │
         │  - Validate compliance & risk                     │
         │  - Draft partnership pitch                        │
         └─────────────────────────┬─────────────────────────┘
                                   │ uses tools
         ┌─────────────────────────▼─────────────────────────┐
         │                    rag_tool.py                    │
         │  - Directory search over knowledge/*.md           │
         │  - Returns relevant snippets for the agents       │
         └─────────────────────────┬─────────────────────────┘
                                   │ consults memory
         ┌─────────────────────────▼─────────────────────────┐
         │                    memory.py                      │
         │  - Short memory: in-run facts/context             │
         │  - Long memory: SQLite (e.g., memory.db)          │
         └──────────────────────────────────────────────────┘
```

---

## 📚 The knowledge base

- `compliance_snippets.md` — KYC/AML, PCI‑DSS guardrails, reporting workflows  
- `competitive_landscape.md` — players, differentiators, regulatory angles

**Tip:** Keep bullets short and specific; RAG works best with atomic facts.

---

## ⚙️ Configuration

Most knobs live in `config.py`. Common items:

- Model name, temperature
- Paths (e.g., `KNOWLEDGE_DIR`, `OUTPUT_DIR`, `SQLITE_DB_PATH`)
- Tool settings (RAG max results, recursion)
- Safety rails (e.g., domain allow‑list for web search)

You can override via environment variables.

---

## 🧪 Usage examples

```bash
python main.py run --topic "SME lending via embedded finance"
python main.py run --topic "Cross-border remittance corridors"
python main.py run --topic "BNPL for B2B marketplaces" --max-sources 8
```

Common flags (if implemented in `main.py`):

- `--topic "<string>"` — focus area to explore
- `--output "<path.md>"` — explicit output path
- `--max-sources <int>` — limit RAG/web sources included in context

---

## 📝 Output format (report)

The writer agent produces a Markdown brief with sections like:

- **Executive Summary**
- **Customer Journey & Value Proposition**
- **Partnership Archetype & Roles**
- **Compliance & Risk Considerations**
- **Integration Approach & Data Flows**
- **KPIs & Success Metrics**
- **Next Steps**

Edit sectioning in `tasks.py` / writer prompts to match your template.

---

## 🔒 Compliance & risk

- The **Compliance** and **Risk** agents validate proposals against `knowledge/` policy notes (KYC/AML, PCI, SAR, watchlists, etc.).
- Strengthen guardrails by:
  - Adding concrete snippets (e.g., data residency, PSD2, MAS TRM).
  - Turning “rules” into explicit checklists the agent must satisfy.

---

## 🧩 Extending the system

- **Add knowledge**: drop new `.md` files into `knowledge/` (e.g., `revenue_models.md`).
- **Add agents**: define specialized agents in `agents.py` and wire them in `tasks.py`.
- **Swap LLMs**: update `config.py` and `requirements.txt` as needed.
- **Add web search**: Serper is integrated—scope with an allow‑list; add DuckDuckGo if preferred.
- **Persistence**: use additional SQLite tables for partner/entity‑keyed facts.

---

## 🧯 Troubleshooting

- **`OPENAI_API_KEY` or `SERPER_API_KEY` not set**  
  Export them before running (see Quick start). Missing `SERPER_API_KEY` will disable/ break web search.

- **403/429 from Serper**  
  Check quota, key validity, and consider backoff/ retry logic.

- **“TypeError: unhashable type: 'dict'” (tools list)**  
  Ensure tools passed to an agent are actual tool instances (constructed objects), not raw dicts.

- **Directory RAG returns nothing**  
  Check `knowledge/` files exist and RAG points to the correct directory. Keep content concise.

- **Too repetitive answers**  
  Lower temperature, enrich `knowledge/`, and ensure web search is enabled with a valid `SERPER_API_KEY`.

---

## 🧑‍💻 Development

```bash
# Lint/format (examples; adapt to your toolchain)
pip install ruff black
ruff check .
black .

# Smoke test
python main.py run --topic "Digital identity verification"
```

---

## 📦 Dependencies

Install from `requirements.txt` (pin versions for reproducibility in CI).

---

## 🔐 Security & data handling

- Treat API keys as secrets; never commit them.
- Knowledge base may contain sensitive compliance notes; keep the repo private if needed.
- When using web search, implement an allow‑list and redact PII in outputs.

---

## 🗺️ Roadmap (suggested)

- [ ] Expand `knowledge/` (revenue models, archetypes, integration patterns)  
- [ ] Evaluation pass (self‑critique)  
- [ ] Unit tests for memory (SQLite) and RAG selection  
- [ ] Dockerfile + CI (GitHub Actions)  
- [ ] Configurable allow‑list for web domains

---

## 📝 License

Choose and add a license (MIT/Apache‑2.0/BSD‑3‑Clause). Add a `LICENSE` file.

---

## 🙌 Acknowledgements

Thanks to the open‑source agentic ecosystem and fintech compliance practitioners whose public materials inspired the structure of `knowledge/`.
