"""
main.py — The Orchestrator

Ties all modules together into a single autonomous research loop.

Usage:
    python main.py "What are the latest breakthroughs in AI agent architectures?"
"""

import os
import sys
import time
from datetime import datetime

# Fix Windows console encoding for Unicode characters
sys.stdout.reconfigure(encoding='utf-8')

from config import OUTPUT_DIR
from planner import generate_queries
from search import search
from scraper import scrape_urls
from relevance_filter import filter_relevant
from synthesizer import synthesize


def run_research(question: str) -> str:
    """
    Run the full research pipeline:
    Question → Planner → Search → Scrape → Filter → Synthesize → Report
    """
    start_time = time.perf_counter()
    
    print("=" * 60)
    print(f"🔬 Web Research Agent")
    print(f"=" * 60)
    print(f"📌 Question: {question}\n")
    
    # ── Step 1: Plan search queries ──────────────────────────────
    print("─" * 40)
    print("🧠 Step 1: Generating search queries...")
    print("─" * 40)
    queries = generate_queries(question)
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    print()
    
    # ── Step 2: Run searches ─────────────────────────────────────
    print("─" * 40)
    print(f"🔍 Step 2: Searching DuckDuckGo ({len(queries)} queries)...")
    print("─" * 40)
    all_results = []
    seen_urls = set()
    for q in queries:
        print(f"\n  Query: \"{q}\"")
        results = search(q)
        for r in results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                all_results.append(r)
                print(f"    → {r.title[:60]}")
    print(f"\n  Total unique URLs: {len(all_results)}\n")
    
    # ── Step 3: Scrape pages ─────────────────────────────────────
    print("─" * 40)
    print(f"📄 Step 3: Scraping {len(all_results)} pages...")
    print("─" * 40)
    urls = [r.url for r in all_results]
    pages = scrape_urls(urls)
    successful = [p for p in pages if p.success]
    print(f"\n  Successfully scraped: {len(successful)}/{len(pages)}\n")
    
    # ── Step 4: Filter for relevance ─────────────────────────────
    print("─" * 40)
    print(f"🚪 Step 4: Filtering {len(successful)} pages for relevance...")
    print("─" * 40)
    relevant = filter_relevant(successful, question)
    print(f"\n  Relevant pages: {len(relevant)}/{len(successful)}\n")
    
    if not relevant:
        print("❌ No relevant pages found. Cannot generate report.")
        return ""
    
    # ── Step 5: Synthesize report ────────────────────────────────
    print("─" * 40)
    print(f"📝 Step 5: Synthesizing report from {len(relevant)} sources...")
    print("   (using /think for deep reasoning — this may take a minute)")
    print("─" * 40)
    report = synthesize(question, relevant)
    
    elapsed = time.perf_counter() - start_time
    
    # Calculate token stats
    from config import llm_metrics
    total_tokens = llm_metrics.total_prompt_tokens + llm_metrics.total_completion_tokens
    cache_hit_rate = (llm_metrics.total_cached_tokens / llm_metrics.total_prompt_tokens * 100) if llm_metrics.total_prompt_tokens > 0 else 0
    
    last_step_tokens = llm_metrics.last_prompt_tokens + llm_metrics.last_completion_tokens
    last_cache_hit_rate = (llm_metrics.last_cached_tokens / llm_metrics.last_prompt_tokens * 100) if llm_metrics.last_prompt_tokens > 0 else 0
    
    print(f"\n{'=' * 60}")
    print(f"✅ Research complete in {elapsed:.1f} seconds")
    print(f"   Sources used: {len(relevant)}")
    print(f"   Report length: {len(report)} chars")
    print(f"   LLM Total Time: {llm_metrics.total_time_seconds:.1f}s")
    print(f"   Tokens Total: {total_tokens:,} (Prompt: {llm_metrics.total_prompt_tokens:,} | Completion: {llm_metrics.total_completion_tokens:,})")
    print(f"   Cache Hits Total: {llm_metrics.total_cached_tokens:,} ({cache_hit_rate:.1f}%)\n")
    print(f"   [Synthesizer Step Only]")
    print(f"   LLM Time: {llm_metrics.last_time_seconds:.1f}s")
    print(f"   Tokens: {last_step_tokens:,} (Prompt: {llm_metrics.last_prompt_tokens:,} | Completion: {llm_metrics.last_completion_tokens:,})")
    print(f"   Cache Hits: {llm_metrics.last_cached_tokens:,} ({last_cache_hit_rate:.1f}%)")
    print(f"{'=' * 60}\n")
    
    return report


def save_report(question: str, report: str) -> str:
    """Save the report to the output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create a filename from the question
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c == " " else "" for c in question)
    safe_name = safe_name[:50].strip().replace(" ", "_")
    filename = f"{timestamp}_{safe_name}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Write the report with a header
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Research Report\n\n")
        f.write(f"**Question:** {question}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"---\n\n")
        f.write(report)
    
    return filepath


# ─── Main Entry Point ───────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"Your research question here\"")
        print("Example: python main.py \"What are the latest breakthroughs in AI agent architectures?\"")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    
    report = run_research(question)
    
    if report:
        # Print the report
        print(report)
        print()
        
        # Save to file
        filepath = save_report(question, report)
        print(f"💾 Report saved to: {filepath}")
