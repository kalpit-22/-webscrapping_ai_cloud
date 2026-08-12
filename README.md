# 🔬 Web Research Agent

An autonomous AI research agent powered by the **DeepSeek API** (`deepseek-v4-flash`). 

You give it a research question, and it will:
1. **Plan** 4 targeted, multi-dimensional search queries.
2. **Search** DuckDuckGo for the best sources.
3. **Scrape** the URLs to extract clean text.
4. **Filter** out irrelevant, low-substance, or SEO spam pages.
5. **Synthesize** a comprehensive, adaptive markdown report using deep reasoning.

---

## 🏗 Architecture (The Modules)

Instead of a monolithic script, the agent is broken into 5 dedicated modules orchestrated by `main.py`:

| Module | Role | Description |
|---|---|---|
| `planner.py` | **The Brainstormer** | Breaks the main question into 4 targeted, multi-dimensional search queries. |
| `search.py` | **The Finder** | Uses DuckDuckGo (`ddgs`) to find URLs matching the queries. |
| `scraper.py` | **The Reader** | Uses `trafilatura` to extract clean article text from HTML (with BeautifulSoup fallback). |
| `relevance_filter.py` | **The Bouncer** | The fact-checker. Asks the LLM if a page contains substantive, relevant information. |
| `synthesizer.py` | **The Writer** | The heavy lifter. Uses deep reasoning to synthesize an adaptive, highly structured final report. |

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.12+**
2. A **DeepSeek API Key**

### 1. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory and add your DeepSeek API key:
```env
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. Run a Research Task
Run the orchestrator script with your research question:

```powershell
python main.py "What are the latest breakthroughs in AI agent architectures?"
```

The agent will print its progress to the console (including total token usage) and save the final Markdown report to the `output/` directory.

---

## 🧠 DeepSeek Reasoning & Adaptive Prompts

This agent heavily utilizes DeepSeek's massive context and reasoning capabilities:

- **Adaptive Synthesis**: The Synthesizer evaluates the complexity of your question first. If you ask for a recipe, it writes a simple, concise guide. If you ask for market analysis, it generates an executive briefing with deep-dives and markdown tables.
- **Deep Reasoning**: DeepSeek's native reasoning phase allows it to plan complex search strategies and evaluate conflicting sources seamlessly. Token limits are tuned (`MAX_TOKENS = 8192`) to accommodate massive context parsing.

---

## 🛡️ Data Quality & Grounding

To prevent hallucinations and outdated information, the agent employs strict data quality mechanisms:

1. **Substantive Filtering**: The Relevance Filter strictly rejects SEO spam, video descriptions without text, 404 pages, and passing mentions.
2. **Strict Citations**: The Synthesizer is forced to cite its claims using inline brackets (e.g., `[1]`) and is required to append a full **References** bibliography mapping those numbers to their source URLs at the bottom of the report, making every claim instantly verifiable.

---

## 📂 Project Structure

```text
Researcher_agent/
│
├── config.py             # Shared settings, token tracking, and LLM client
├── main.py               # The Orchestrator
├── planner.py            # Query generation module
├── relevance_filter.py   # Page relevance evaluation module
├── scraper.py            # HTML extraction module
├── search.py             # DuckDuckGo search module
│
├── requirements.txt      # Python dependencies
├── .env                  # API keys
│
└── output/               # Generated research reports (.md)
```

## 📝 License
MIT
