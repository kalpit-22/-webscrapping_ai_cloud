"""
synthesizer.py — Report Generator Module

Takes all approved scraped text and writes a comprehensive,
well-formatted research report answering the original question.

This module uses /think to enable the model's reasoning mode,
since report synthesis benefits from deep thinking.

Usage:
    python synthesizer.py
"""

import sys

from config import llm_chat, MAX_TOKENS
from scraper import ScrapedPage

sys.stdout.reconfigure(encoding='utf-8')


SYNTHESIZER_PROMPT = """You are a senior research analyst. Using ONLY the source material provided below, write a comprehensive, well-structured research report that answers the following question.

Research Question: {question}

Source Material:
{sources}

Instructions:
- Write a detailed, well-organized report with clear sections and headings
- Use markdown formatting (headers, bold, bullet points, etc.)
- Cite which source each key finding comes from using inline brackets (e.g., [1], [2])
- Include a brief summary/conclusion at the end
- ONLY use information from the provided sources — do NOT make up facts
- If the sources don't fully answer the question, acknowledge the gaps
- VERY IMPORTANT: You must include a "References" section at the very end of the report that lists every source used, along with its full URL provided in the source material block.
/think"""


def _format_sources(pages: list[ScrapedPage]) -> str:
    """Format scraped pages into a numbered source block for the prompt."""
    parts = []
    for i, page in enumerate(pages, 1):
        parts.append(
            f"--- Source [{i}]: {page.title} ---\n"
            f"URL: {page.url}\n"
            f"{page.text}\n"
        )
    return "\n".join(parts)


def synthesize(question: str, pages: list[ScrapedPage]) -> str:
    """
    Generate a research report from the approved scraped pages.
    
    Args:
        question: The original research question.
        pages: List of relevant ScrapedPage objects.
    
    Returns:
        The formatted research report as a string.
    """
    if not pages:
        return "❌ No relevant sources found. Cannot generate a report."
    
    sources_text = _format_sources(pages)
    
    messages = [
        {"role": "user", "content": SYNTHESIZER_PROMPT.format(
            question=question,
            sources=sources_text,
        )}
    ]
    
    # Use higher max_tokens for the report — this is the heavy lifter
    response = llm_chat(messages, max_tokens=MAX_TOKENS, temperature=0.3)
    
    return response.strip()


# ─── Standalone Test ────────────────────────────────────────────
if __name__ == "__main__":
    test_pages = [
        ScrapedPage(
            url="https://example.com/ai-agents",
            title="AI Agents: A Comprehensive Guide",
            text="AI agents are autonomous systems that can perceive their environment, "
                 "make decisions, and take actions to achieve specific goals. Modern AI agents "
                 "use large language models (LLMs) as their reasoning backbone. Key architectures "
                 "include ReAct (Reasoning + Acting), Chain-of-Thought prompting, and tool-augmented "
                 "agents. Recent breakthroughs include multi-agent collaboration frameworks where "
                 "multiple specialized agents work together on complex tasks.",
            success=True,
        ),
        ScrapedPage(
            url="https://example.com/agent-frameworks",
            title="Top AI Agent Frameworks in 2024",
            text="Popular frameworks for building AI agents include LangChain, CrewAI, and AutoGen. "
                 "LangChain provides a modular toolkit for building LLM-powered applications with tools. "
                 "CrewAI specializes in multi-agent orchestration. AutoGen by Microsoft enables "
                 "conversational AI agents that can collaborate on tasks.",
            success=True,
        ),
    ]
    
    question = "What are the latest breakthroughs in AI agent architectures?"
    print(f"📝 Synthesizing report for: \"{question}\"\n")
    print("(This may take a minute — using /think for deep reasoning...)\n")
    
    report = synthesize(question, test_pages)
    print(report)
