# 🔬 Web Research Agent

An autonomous, fully local AI research agent powered by **Qwen3-14B** and **llama.cpp**. 

You give it a research question, and it will:
1. **Plan** 3-4 targeted search queries.
2. **Search** DuckDuckGo for the best sources.
3. **Scrape** the URLs to extract clean text.
4. **Filter** out irrelevant pages to prevent hallucinations.
5. **Synthesize** a comprehensive, well-formatted markdown report using deep reasoning (`/think`).

Everything runs locally on your machine—no API keys, no subscriptions, no cloud telemetry.

---

## 🏗 Architecture (The Modules)

Instead of a monolithic script, the agent is broken into 5 dedicated modules orchestrated by `main.py`:

| Module | Role | Description |
|---|---|---|
| `planner.py` | **The Brainstormer** | Breaks the main question into targeted search queries. |
| `search.py` | **The Finder** | Uses DuckDuckGo to find URLs matching the queries. |
| `scraper.py` | **The Reader** | Uses `trafilatura` to extract clean article text from HTML. |
| `relevance_filter.py` | **The Bouncer** | Asks the LLM if a page is actually relevant to the question. |
| `synthesizer.py` | **The Writer** | The heavy lifter. Uses deep reasoning to synthesize the final report. |

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.12+**
2. **llama.cpp** (with a compiled `llama-server.exe`)
3. A Qwen3-14B GGUF model (e.g., `Qwen3-14B-Q4_K_M.gguf`)

### 1. Install Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the LLM Backend
Start the local `llama-server`. An optimized startup script is provided (`start_server.ps1`) which configures a 16K context window and Flash Attention to fit nicely into 12GB VRAM.

```powershell
.\start_server.ps1
```

### 3. Run a Research Task
Run the orchestrator script with your research question:

```powershell
python main.py "What are the latest breakthroughs in AI agent architectures?"
```

The agent will print its progress to the console and save the final Markdown report to the `output/` directory.

---

## 🧠 Qwen3 Thinking Modes (`/think` vs `/no_think`)

This agent heavily utilizes Qwen3's dual modes to balance **speed** and **quality**:

- **`/no_think` (Fast mode)**: Used by the **Planner** and **Relevance Filter**. These tasks require quick, straightforward outputs (e.g., a simple YES/NO or a list of queries). Disabling thinking saves massive amounts of time and tokens.
- **`/think` (Deep reasoning mode)**: Used exclusively by the **Synthesizer**. Writing the final report requires synthesizing multiple sources, handling contradictions, and structuring the output. The model is allowed to "think" out loud before generating the report.

*(For a deep dive into how we tamed the thinking models during development, see [field_notes.md](field_notes.md))*

---

## 🛡️ Data Quality & Grounding

To prevent hallucinations and outdated information, the agent employs two strict data quality mechanisms:

1. **Recency Enforcer (Double Filter)**: If your question implies you want new information (e.g., "latest", "newest"), the Planner automatically injects the current year into search queries. Then, the Bouncer strictly rejects any scraped pages that appear outdated.
2. **Strict Citations**: The Synthesizer is forced to cite its claims using inline brackets (e.g., `[1]`) and is required to append a full **References** bibliography mapping those numbers to their source URLs at the bottom of the report, making every claim instantly verifiable.

---

## 📂 Project Structure

```text
Researcher_agent/
│
├── config.py             # Shared settings and LLM client initialization
├── main.py               # The Orchestrator
├── planner.py            # Query generation module
├── relevance_filter.py   # Page relevance evaluation module
├── scraper.py            # HTML extraction module
├── search.py             # DuckDuckGo search module
│
├── requirements.txt      # Python dependencies
├── start_server.ps1      # llama.cpp server launch script
├── field_notes.md        # Dev log & technical insights
│
└── output/               # Generated research reports (.md)
```

## 📝 License
MIT
