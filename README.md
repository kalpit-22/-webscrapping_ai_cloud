# Web Research Agent

An autonomous web research assistant powered by the DeepSeek API. It takes a research question, plans multi-angle search queries, scrapes and filters relevant web pages, and synthesizes structured markdown reports with inline citations and full source references.

The system is built as a cloud-ready, full-stack application featuring an asynchronous Celery background queue, real-time status streaming over SSE, database persistence in MongoDB, and a Next.js web dashboard.

---

## How It Works

1. **Query Planning**: The agent breaks the user's research topic into up to 4 targeted, multi-dimensional search queries to cover definitions, recent updates, expert analysis, and edge cases.
2. **Web Search**: Executes queries on DuckDuckGo using `ddgs`, collecting candidate URLs, titles, and snippets while deduplicating links across queries.
3. **Scraping & Extraction**: Downloads page HTML using `requests` and extracts clean text using `trafilatura` (with a `BeautifulSoup4` fallback). Content is truncated to keep within LLM context limits.
4. **Relevance Filtering**: An LLM-based relevance check evaluates extracted text against the original question, filtering out SEO spam, login walls, thin content, and off-topic pages.
5. **Report Synthesis**: Generates an adaptive markdown report using only the verified sources, adding inline citations (e.g. `[1]`, `[2]`) and listing all referenced URLs in a dedicated section at the end.

---

## Key Features

- **CLI & Web Interface**: Run research tasks directly from the terminal or through the web UI.
- **Asynchronous Processing**: Uses Celery and Redis to handle long-running web scraping and synthesis workflows without blocking the API.
- **Real-Time Progress Streaming**: Streams live status updates and step completions to the browser using Server-Sent Events (SSE).
- **Task Control**: Cancel active research jobs mid-execution from the UI.
- **History & Logging**: Stores past research reports, source counts, and token usage metrics in MongoDB, accessible via a history view.
- **Token & Cost Tracking**: Tracks token consumption per query and estimates API costs.
- **Downloadable Reports**: Download any generated report directly as a `.md` markdown file.
- **Authentication & Security**: Protected by NextAuth credentials login on the frontend and API key authentication on backend endpoints.

---

## Tech Stack

- **Frontend**: Next.js (App Router), React, Tailwind CSS, NextAuth.js
- **Backend API**: FastAPI, Python 3.12, SSE Starlette
- **Worker & Queue**: Celery, Redis
- **Database**: MongoDB (Async Motor driver)
- **Scraping & Search**: Trafilatura, BeautifulSoup4, DuckDuckGo Search (`ddgs`), Requests
- **LLM Integration**: DeepSeek API via OpenAI Python SDK (`deepseek-v4-flash` model)

---

## Repository Structure

- [api.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/api.py) - FastAPI server handling SSE streaming, task cancellation, health checks, and log fetching.
- [worker.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/worker.py) - Celery background task orchestrating the research pipeline.
- [planner.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/planner.py) - Decomposes research questions into targeted search queries.
- [search.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/search.py) - DuckDuckGo search integration and URL deduplication.
- [scraper.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/scraper.py) - Page fetcher and text extractor using Trafilatura and BeautifulSoup.
- [relevance_filter.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/relevance_filter.py) - LLM relevance filter for screening scraped pages.
- [synthesizer.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/synthesizer.py) - Report generator enforcing citation rules and structured markdown output.
- [database.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/database.py) - MongoDB driver for saving and reading research logs.
- [config.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/config.py) - Shared environment configuration, model settings, and LLM client initialization.
- [main.py](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/main.py) - Standalone CLI runner.
- [docker-compose.yml](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/docker-compose.yml) - Local container orchestration setup for Redis, MongoDB, API, and Worker.
- [frontend/](file:///Users/pradhyumn/Projects/Webscrapper/-webscrapping_ai_cloud/frontend) - Next.js web application.

---

## Environment Variables

Create a `.env` file in the root directory:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
BACKEND_API_KEY=dev-secret-key
REDIS_URL=redis://localhost:6379/0
MONGO_URI=mongodb://localhost:27017
```

Create a `frontend/.env.local` file for the web UI:

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=super-secret-key-123
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
BACKEND_API_KEY=dev-secret-key
```

---

## Getting Started

### Local Development

1. **Install Python dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Ensure Redis and MongoDB are running** locally on ports `6379` and `27017`.

3. **Start the Celery worker**:
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```
   *(On Windows, add `-P solo` if running outside WSL)*

4. **Start the FastAPI backend server**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```

5. **Start the Frontend development server**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open `http://localhost:3000` in your browser. Default login credentials: `testuser` / `password123`.

### CLI Usage

To execute a research task from the terminal without the web backend or queue:

```bash
python main.py "What are the latest breakthroughs in AI agent architectures?"
```

Reports are automatically saved in the `output/` directory.

### Running with Docker Compose

To start Redis, MongoDB, the FastAPI backend, and the Celery worker using Docker:

```bash
docker-compose up --build
```

---

## API Endpoints

- `GET /api/research` - Initiates a research task and streams progress updates via Server-Sent Events (SSE). Requires `question` query parameter.
- `POST /api/research/{task_id}/stop` - Cancels an active Celery task by ID.
- `GET /api/logs` - Retrieves past research reports, timestamps, and metrics from MongoDB.
- `GET /api/health` - Basic health check endpoint.

All protected endpoints require the `api_key` query parameter or header matching `BACKEND_API_KEY`.

---

## License

MIT
