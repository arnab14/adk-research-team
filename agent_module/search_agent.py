# agent_module/search_agent.py

import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import TavilySearchResults

# Load environment variables from.env file
load_dotenv()

# --- Model Configuration ---
# Read the desired model name from environment variables
# Provide a sensible default if the variable is not set
SPECIALIST_AGENT_MODEL = os.getenv("SPECIALIST_AGENT_MODEL", "gemini-1.5-flash-latest")
# --- ---

def create_search_agent():
    """
    Creates an agent specialized in web searching using the Tavily Search API.

    This agent utilizes LangChain's TavilySearchResults tool, wrapped by ADK's
    LangchainTool for seamless integration. Its primary function is to execute
    web searches based on user queries and return structured results.

    Returns:
        Agent: An instance of google.adk.Agent configured for web search.

    Raises:
        ValueError: If the TAVILY_API_KEY environment variable is not set.
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables. Please set it in your.env file.")

    # Instantiate the Tavily Search tool from LangChain
    tavily_tool_instance = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=False, # Set to False as we have a dedicated extractor
        include_images=False
    )

    # Wrap the LangChain tool using ADK's LangchainTool adapter
    adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)

    # Define the Search Agent using google.adk.Agent (LlmAgent)
    search_agent = Agent(
        name="search_agent",
        # Use the model name read from the environment variable
        model=SPECIALIST_AGENT_MODEL, #
        description="A specialized agent that searches the web for information using the Tavily Search API.",
        instruction="""You are a highly efficient web research specialist.
        Your primary goal is to find relevant information online based on the user's query.
        1.  Receive the user's research topic or question.
        2.  Formulate the most effective search query based on the topic.
        3.  Utilize the 'TavilySearchResults' tool to execute the web search.
        4.  Analyze the search results returned by the tool. The results may include a direct answer and a list of web pages with titles, links, and snippets.
        5.  Present the findings in a clear, structured format:
            - If a direct answer is provided by Tavily, present that first.
            - List the top search results (up to the configured limit). For each result, include:
                - Title
                - URL (Link)
                - A brief snippet or preview of the content.
        6.  Highlight the most relevant results based on the original user query.
        7.  If the search yields no relevant results, state that clearly and perhaps suggest alternative search terms or approaches.
        8.  Crucially, DO NOT invent information. Only report what is found in the search results provided by the tool.
        9.  Ensure the output focuses solely on the search findings. Do not add conversational filler unless specifically asked to elaborate.
        """,
        # Provide the ADK-wrapped tool to the agent
        tools=[adk_tavily_tool]
    )
    return search_agent

# Example of direct instantiation (useful for testing this agent module alone)
# if __name__ == '__main__':
#     agent = create_search_agent()
#     print(f"Search Agent '{agent.name}' created successfully using model '{SPECIALIST_AGENT_MODEL}'.")