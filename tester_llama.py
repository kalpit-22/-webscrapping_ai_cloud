import time
import re
import sys
import requests

# Fix Windows console encoding for Unicode characters (e.g., CO₂)
sys.stdout.reconfigure(encoding='utf-8')

# Pointing to your local llama.cpp server
URL = "http://localhost:8081/v1/chat/completions"

# Using /no_think tag in the user message to disable thinking mode.
# Per Qwen3 docs: add /think or /no_think to user prompts or system messages
# to switch the model's thinking mode from turn to turn.
payload = {
    "model": "qwen3-14b",
    "messages": [
        {
            "role": "user",
            "content": "Write a highly detailed summary explaining the complete process of photosynthesis, step by step. /no_think"
        }
    ],
    "max_tokens": 2048,
    "temperature": 0.3
}

headers = {
    "Content-Type": "application/json"
}

print("Firing prompt to llama.cpp via Python... (Waiting for generation)")

start_time = time.perf_counter()

try:
    response = requests.post(URL, headers=headers, json=payload)
    end_time = time.perf_counter()

    if response.status_code == 200:
        data = response.json()

        # Extract from chat completions response format
        message = data["choices"][0]["message"]
        content = message.get("content", "") or ""
        reasoning = message.get("reasoning_content", "") or ""
        completion_tokens = data["usage"]["completion_tokens"]
        total_time = end_time - start_time
        tps = completion_tokens / total_time if total_time > 0 else 0

        # Strip any <think>...</think> tags just in case
        cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        # Show reasoning if present
        if reasoning:
            print(f"\n--- [ Reasoning (first 200 chars) ] ---")
            print(reasoning.strip()[:200] + "...\n")

        print("--- [ Response Preview ] ---")
        if cleaned:
            print(cleaned + "\n")
        else:
            print("(No visible content)")
            print(f"  Content length: {len(content)} chars")
            print(f"  Reasoning length: {len(reasoning)} chars")

        print("--- [ Benchmark Results ] ---")
        print(f"Total Time:       {total_time:.2f} seconds")
        print(f"Tokens Generated: {completion_tokens} tokens")
        print(f"Throughput:       {tps:.2f} tokens/sec")

    else:
        print(f"Server returned error code {response.status_code}: {response.text}")

except Exception as e:
    print(f"Connection failed: {e}")
    print("Ensure llama-server.exe is running on port 8081!")