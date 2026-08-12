"""
Shared configuration for the Web Research Agent.
All modules import their LLM client and settings from here.
"""

import time
from dataclasses import dataclass
from openai import OpenAI

# ─── LLM Backend ───────────────────────────────────────────────
LLM_BASE_URL = "http://localhost:8081/v1"
LLM_MODEL = "qwen3-14b"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 4096

# ─── Search & Scraping ─────────────────────────────────────────
SEARCH_MAX_RESULTS = 5          # Results per search query
SCRAPE_TIMEOUT = 10             # Seconds per page download
SCRAPE_MAX_CHARS = 5000         # Truncate scraped text to fit context

# ─── Output ────────────────────────────────────────────────────
OUTPUT_DIR = "output"

# ─── Shared LLM Client ─────────────────────────────────────────
# The openai library is API-compatible with llama.cpp's /v1 endpoint.
# All modules use this single client instance.
client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key="not-needed"        # llama.cpp doesn't require an API key
)


# ─── LLM Metrics Tracking ──────────────────────────────────────
@dataclass
class LLMMetrics:
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cached_tokens: int = 0
    total_time_seconds: float = 0.0
    
    # Specific tracking for the very last call (e.g. the Synthesizer)
    last_prompt_tokens: int = 0
    last_completion_tokens: int = 0
    last_cached_tokens: int = 0
    last_time_seconds: float = 0.0

llm_metrics = LLMMetrics()


def llm_chat(messages: list[dict], max_tokens: int = MAX_TOKENS,
             temperature: float = DEFAULT_TEMPERATURE) -> str:
    """
    Send a chat completion request to the local LLM.
    Returns the assistant's response content as a string.
    """
    start_time = time.perf_counter()
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    elapsed = time.perf_counter() - start_time
    
    # Update global metrics
    llm_metrics.total_time_seconds += elapsed
    llm_metrics.last_time_seconds = elapsed
    
    if response.usage:
        llm_metrics.total_prompt_tokens += response.usage.prompt_tokens
        llm_metrics.total_completion_tokens += response.usage.completion_tokens
        llm_metrics.last_prompt_tokens = response.usage.prompt_tokens
        llm_metrics.last_completion_tokens = response.usage.completion_tokens
        
        if response.usage.prompt_tokens_details and response.usage.prompt_tokens_details.cached_tokens:
            llm_metrics.total_cached_tokens += response.usage.prompt_tokens_details.cached_tokens
            llm_metrics.last_cached_tokens = response.usage.prompt_tokens_details.cached_tokens
        else:
            llm_metrics.last_cached_tokens = 0
            
    return response.choices[0].message.content or ""
