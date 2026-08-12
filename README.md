# 🔬 Web Research Agent (Cloud Native Edition)

An autonomous AI research agent powered by the **DeepSeek API** (`deepseek-v4-flash`). 

You give it a research question, and it will:
1. **Plan** 4 targeted, multi-dimensional search queries.
2. **Search** DuckDuckGo for the best sources.
3. **Scrape** the URLs to extract clean text.
4. **Filter** out irrelevant, low-substance, or SEO spam pages.
5. **Synthesize** a comprehensive, adaptive markdown report using deep reasoning.

This project has been massively upgraded into a full-stack, cloud-ready application!

---

## ✨ Features

- **Full-Stack UI**: A beautiful, modern Next.js frontend built with React, Tailwind CSS, and `lucide-react`.
- **Authentication**: Secured with `NextAuth.js` credentials login. The API is protected via Backend API Keys.
- **Asynchronous Cloud Backend**: 
  - **FastAPI** provides a high-performance SSE (Server-Sent Events) API.
  - **Celery & Redis** handle long-running, concurrent web scraping tasks asynchronously.
- **Persistent Database**: Research logs and metadata are stored in a **MongoDB** database.
- **History Dashboard**: Browse past research tasks, complete with sources used, token metrics, and expandable report drops.
- **Real-Time Cost Tracking**: The UI estimates the exact API cost for every search (calculated based on DeepSeek's $0.20 per 1M token blended rate).
- **Downloadable Reports**: Instantly download any finished research report as a `.md` markdown file to your local machine.
- **Task Cancellation**: A convenient "Stop Request" button lets you forcefully terminate any active research task running in the cloud.

---

## 🏗 Architecture (The Stack)

- **Frontend**: Next.js 14 (App Router), React, Tailwind, NextAuth.js
- **API Proxy**: FastAPI, Python 3.12
- **Worker/Queue**: Celery, Redis
- **Database**: MongoDB (Motor async driver)
- **AI/Scraping Core**: OpenAI SDK, `trafilatura`, `BeautifulSoup4`, `ddgs`

---

## 🚀 Getting Started Locally

### 1. Backend Setup (Python)
Ensure you have Redis and MongoDB running locally, then:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
DEEPSEEK_API_KEY=your_api_key_here
BACKEND_API_KEY=dev-secret-key
REDIS_URL=redis://localhost:6379/0
MONGODB_URI=mongodb://localhost:27017
```

Start the Celery Worker:
```bash
celery -A worker.celery_app worker --loglevel=info -P solo
```

Start the FastAPI Server (in a separate terminal):
```bash
uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup (Node.js)
```bash
cd frontend
npm install
```

Create a `frontend/.env.local` file:
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=super-secret-key-123
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
BACKEND_API_KEY=dev-secret-key
```

Start the Next.js Dev Server:
```bash
npm run dev
```

Visit `http://localhost:3000` to log in (Default Username: `testuser`, Password: `password123`) and start researching!

---

## ☁️ Azure Container Apps Deployment

This application is designed to be deployed using a microservices architecture on **Azure Container Apps**. It runs 3 containers inside a secure VNet environment:
1. **Frontend App**: Next.js Node container (Public Ingress)
2. **FastAPI & Celery App**: Python container (Internal TCP Ingress)
3. **Mongo DB & Redis**: Managed services or sidecar containers.

*Refer to the deployment documentation for CI/CD GitHub Actions setup.*

---

## 📝 License
MIT
