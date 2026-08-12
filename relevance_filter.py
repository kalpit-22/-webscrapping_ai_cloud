"""
relevance_filter.py — Relevance Filter Module (The Bouncer)

Feeds scraped text to the LLM and asks if it's relevant to the
original research question. Filters out garbage pages.

Usage:
    python relevance_filter.py
"""

import sys

from config import llm_chat
from scraper import ScrapedPage

sys.stdout.reconfigure(encoding='utf-8')


RELEVANCE_PROMPT = """You are a strict relevance judge. Determine if the following web page content is relevant to answering the research question.

Research Question: {question}

Web Page Title: {title}
Web Page Content (first 1500 chars):
---
{text}
---

Rules for relevance:
1. The page must actually contain information that helps answer the question.
2. If the question implies recency (e.g., using words like "latest", "new", "2024", "current"), you MUST REJECT pages that appear to be outdated or discuss old versions of the topic.
3. If the page is just a generic marketing page, navigation menu, or irrelevant article, reject it.

Is this page relevant and up-to-date enough to answer the research question?
Reply with EXACTLY one word: YES or NO
/no_think"""


def check_relevance(page: ScrapedPage, question: str) -> bool:
    """
    Ask the LLM whether a scraped page is relevant to the research question.
    
    Args:
        page: A ScrapedPage object with extracted text.
        question: The original research question.
    
    Returns:
        True if the page is relevant, False otherwise.
    """
    if not page.success or not page.text.strip():
        return False
    
    messages = [
        {"role": "user", "content": RELEVANCE_PROMPT.format(
            question=question,
            title=page.title,
            text=page.text[:1500],  # Send only first 1500 chars for speed
        )}
    ]
    
    response = llm_chat(messages, max_tokens=16, temperature=0.1)
    
    # Check if the response contains YES
    return "YES" in response.upper()


def filter_relevant(pages: list[ScrapedPage], question: str) -> list[ScrapedPage]:
    """
    Filter a list of scraped pages, keeping only relevant ones.
    
    Args:
        pages: List of ScrapedPage objects.
        question: The original research question.
    
    Returns:
        Filtered list of relevant ScrapedPage objects.
    """
    relevant = []
    for page in pages:
        if not page.success:
            print(f"  ⏭ Skipping (failed scrape): {page.url}")
            continue
        
        is_relevant = check_relevance(page, question)
        status = "✅" if is_relevant else "❌"
        print(f"  {status} {page.title[:60]}")
        
        if is_relevant:
            relevant.append(page)
    
    return relevant


# ─── Standalone Test ────────────────────────────────────────────
if __name__ == "__main__":
    # Quick test with fake data
    test_pages = [
        ScrapedPage(
            url="https://example.com/ai-agents",
            title="AI Agents: A Comprehensive Guide",
            text="AI agents are autonomous systems that can perceive their environment, "
                 "make decisions, and take actions to achieve specific goals. Modern AI agents "
                 "use large language models as their reasoning backbone...",
            success=True,
        ),
        ScrapedPage(
            url="https://example.com/cooking",
            title="Best Pasta Recipes 2024",
            text="Looking for the perfect pasta recipe? Try our creamy garlic parmesan "
                 "pasta with fresh herbs and a crispy breadcrumb topping...",
            success=True,
        ),
    ]
    
    question = "What are the latest breakthroughs in AI agent architectures?"
    print(f"🚪 Filtering pages for: \"{question}\"\n")
    
    relevant = filter_relevant(test_pages, question)
    
    print(f"\n{len(relevant)}/{len(test_pages)} pages passed the relevance filter.")
