# f:\Dev\AI\Agentic_AI\adk-research-team\test_runner.py
import asyncio
import sys

# --- Fix for asyncio subprocess error on Windows ---
# Apply this policy change absolutely first
if sys.platform == "win32":
    print("Applying WindowsSelectorEventLoopPolicy...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("Policy applied.")
# --- End Fix ---

# Now import the agent that uses the problematic library
from agent_module.content_extractor import create_content_extractor_agent, extract_content_from_url

async def main():
    print("Running main test function...")
    # Directly test the function causing the issue
    result = await extract_content_from_url("https://google.github.io/adk-docs/")
    print("Extraction result:", result)

if __name__ == "__main__":
    asyncio.run(main())