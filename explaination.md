# 🚀 Project Evolution: From Script to Cloud-Native Agent

This document serves as a comprehensive breakdown of the entire architectural evolution we performed on the DeepResearch AI agent. We took a powerful local Python script and scaled it into a robust, full-stack, cloud-hosted microservice application.

---

## 1. The Core Problem
Originally, the research agent was a synchronous local Python script (`main.py`). While powerful, running it required a local terminal, and the massive scraping + DeepSeek reasoning tasks could take 2–3 minutes to complete. A standard web request would timeout waiting for it.

## 2. Frontend Modernization (Next.js & Tailwind)
We started by giving the agent a face. We built a sleek, dark-mode-first Next.js 14 web application:
- **Streaming UI:** We implemented Server-Sent Events (SSE) so the frontend receives real-time text updates (like "Searching DuckDuckGo...", "Scraping 5 sources...") dynamically without polling.
- **Aesthetic Design:** Utilizing `lucide-react` for iconography, Tailwind CSS for glassmorphism effects, and dynamic CSS animations (like pulsing dots and glowing borders) to make the UI feel premium and alive.

## 3. Asynchronous Backend Architecture (FastAPI + Celery + Redis)
To solve the 3-minute timeout issue, we decoupled the architecture:
- **FastAPI:** Acts as the API gateway. When a user requests research, FastAPI immediately returns an SSE stream connection.
- **Celery & Redis:** Instead of executing the heavy scraping natively, FastAPI offloads the `run_research_task` to a Celery worker. Redis acts as the message broker passing states back and forth. The worker processes the scraping autonomously in the background and pushes state updates which FastAPI streams to the frontend.

## 4. Deployment on Azure Container Apps
We completely containerized the application for the cloud:
- **Dockerization:** We wrote separate Dockerfiles for the `frontend` (Node.js), the `backend` (FastAPI), and the `worker` (Python Celery). 
- **Cloud Infrastructure:** We deployed these containers using Azure Container Apps. We configured the backend to be internal (only accessible within the Azure VNet) to protect it from the public web, while exposing the Next.js frontend to the world.

## 5. Security & Authentication (NextAuth)
To prevent unauthorized API spam (and massive DeepSeek bills), we secured the app:
- **Frontend Auth:** Integrated `NextAuth.js` with a custom Credentials login screen (username/password).
- **Backend API Keys:** Configured NextAuth to inject a secure `BACKEND_API_KEY` into the authenticated session. The frontend securely attaches this key to every API request it makes, ensuring the internal FastAPI backend rejects unauthorized traffic.
- **Iframe Embedding:** We modified NextAuth's internal cookie policies (`SameSite="none"`, `Secure=true`) so that you could cleanly embed the app inside your personal `github.io` portfolio using an `<iframe>`.

## 6. Persistence (MongoDB)
To make the application genuinely useful over time, we added database persistence:
- **Motor (Async MongoDB):** We spun up a Mongo database and integrated it directly into the Celery worker. Every time a research task completes successfully, the worker saves the user's prompt, the full markdown report, the sources cited, and the exact token usage to the database.

## 7. Quality of Life Pro-Features
With the foundational architecture solid, we shipped several premium upgrades:
- **History Dashboard:** A dedicated `/history` page in the UI that fetches past logs from MongoDB, rendering them as beautifully expandable, responsive cards.
- **Cost Tracker:** We built a formula that multiplies the API `total_tokens_used` by DeepSeek's blended rate ($0.20 / 1M tokens) to show you exactly what each deep-dive costs in real-time.
- **Download Button:** We utilized native browser Blob APIs to let you instantly download the completed markdown report as a `.md` file.
- **Task Revocation (Stop Button):** We added a "Stop Request" button that hits a new FastAPI endpoint (`POST /api/research/{id}/stop`). This endpoint actively reaches into the Celery cluster via Redis and forcefully kills (`SIGKILL`) the running Python worker if you change your mind mid-search!

---
**Conclusion:** We successfully transformed a single-file Python script into a robust, secure, asynchronous, cloud-hosted SaaS platform.
