# agent_module/agent.py

import sys
import asyncio

# --- Force WindowsSelectorEventLoopPolicy globally ---
# Apply this policy change *before* any other imports or async setup
# This is more aggressive and might affect other parts of ADK if they
# rely on the default Proactor loop, but it's necessary to try for Playwright.
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print("INFO: Applied WindowsSelectorEventLoopPolicy globally.")
    except Exception as policy_error:
        print(f"WARNING: Could not set global event loop policy: {policy_error}")
# --- End Fix ---

import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

# Import the factory functions for our specialized agents
from agent_module.search_agent import create_search_agent
from agent_module.content_extractor import create_content_extractor_agent
from agent_module.summarizer import create_summarizer_agent

# Load environment variables from.env file
load_dotenv()

# --- Model Configuration ---
# Read the desired model name for the coordinator from environment variables
# Use a more powerful model for orchestration by default
COORDINATOR_AGENT_MODEL = os.getenv("COORDINATOR_AGENT_MODEL", "gemini-1.5-pro-latest")
# --- ---

# --- Define Agent Creation Logic ---
# We wrap this in a function to prevent instantiation upon module import.
# ADK typically looks for a 'root_agent' variable, so we'll provide a function
# to get it, or potentially instantiate it lazily if ADK supports that pattern.
# For now, let's assume ADK needs the 'root_agent' variable defined.

def get_research_team_agent():
    """Creates and configures the research coordinator agent and its tools."""
    print("Initializing specialist agents...")
    # --- Instantiate Specialist Agents ---
    # Create instances of each specialized agent using their factory functions.
    try:
        search_agent_instance = create_search_agent()
        extractor_agent_instance = create_content_extractor_agent()
        summarizer_agent_instance = create_summarizer_agent()
    except ValueError as e:
        print(f"Error creating specialist agents: {e}")
        print("Please ensure all required API keys (TAVILY_API_KEY, GOOGLE_API_KEY/Vertex Setup) are in your.env file.")
        raise SystemExit("Agent initialization failed due to missing configuration.")
    print("Specialist agents initialized.")

    # --- Wrap Specialists as Tools using AgentTool ---
    print("Wrapping specialists as tools...")
    search_tool = AgentTool(agent=search_agent_instance)
    extractor_tool = AgentTool(agent=extractor_agent_instance)
    summarizer_tool = AgentTool(agent=summarizer_agent_instance)
    print("Tools created.")

    # --- Define the Root Agent (Coordinator) ---
    print("Creating root agent (research_coordinator)...")
    _root_agent = Agent(
        name="research_coordinator",
        # Use the coordinator model name read from the environment variable
        model=COORDINATOR_AGENT_MODEL, #
        description="A coordinator agent that manages a team of specialized research agents (Search, Extract, Summarize) to fulfill user research requests.",
        instruction="""You are the expert coordinator of a research assistant team. Your role is to understand user research requests and delegate tasks to the appropriate specialist agent.

        Your team consists of the following specialists, available as tools:
        - **search_agent**: Use this tool when the user asks to find information, research a topic, or discover relevant web pages. Provide the research topic as input to this tool.
        - **content_extractor**: Use this tool when the user provides a specific URL and asks for its content, or when you need to get the full text from a URL found by the search_agent. Provide the URL as input to this tool.
        - **summarizer_agent**: Use this tool when the user asks for a summary of previously provided or extracted text. Provide the text to be summarized as input to this tool.

        Your workflow should be:
        1.  **Analyze the Request:** Understand the user's goal. Is it finding information, analyzing a specific page, summarizing text, or a multi-step research task?
        2.  **Delegate Appropriately:**
            - For finding information: Call `search_agent` with the topic.
            - For analyzing a URL: Call `content_extractor` with the URL.
            - For summarizing text: Call `summarizer_agent` with the text.
        3.  **Handle Multi-Step Research:** For complex requests requiring search, extraction, and summarization:
            a. Call `search_agent` first to find relevant URLs.
            b. Present the search results to the user. Ask the user which URLs to analyze further, OR use your judgment to select the most promising 1-2 URLs if the user asks for a full workflow.
            c. For each selected URL, call `content_extractor` to get the full text.
            d. Call `summarizer_agent` with the extracted text (or combined text from multiple extractions) to create a final summary.
        4.  **Synthesize and Respond:** Combine the results from the specialist agents into a single, coherent, and comprehensive final response to the user. Clearly attribute information to its source URL where appropriate. Explain the steps taken if it was a multi-step process.
        5.  **Clarify if Necessary:** If the user's request is ambiguous, ask clarifying questions before delegating.
        6.  **Error Handling:** If a specialist tool returns an error, inform the user about the issue.

        **Crucially:** You are the final interface to the user. Ensure the final response directly addresses their original request, integrating the outputs from your specialists seamlessly. Do not just forward raw tool outputs.
        """,
        # Provide the AgentTool instances to the coordinator agent
        tools=[search_tool, extractor_tool, summarizer_tool]
    )
    print("Root agent created.")
    return _root_agent



# The 'root_agent' variable is typically what ADK looks for by convention
# when running `adk web.` or `adk run agent_module` from the parent directory.

# We now call the function to instantiate the agent when ADK needs it.
# ADK's mechanism for finding the agent might need adjustment if it strictly
# requires a top-level 'root_agent' variable. If 'adk web .' fails after
# this change, we may need to investigate how ADK discovers the agent.
root_agent = get_research_team_agent()
print(f"Root agent '{root_agent.name}' initialized and ready.")
