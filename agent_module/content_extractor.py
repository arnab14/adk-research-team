# agent_module/content_extractor.py

import os
import asyncio
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from crawl4ai import AsyncWebCrawler # Ensure crawl4ai is installed

# Load environment variables from.env file
load_dotenv()

# --- Model Configuration ---
# Read the desired model name from environment variables
# Provide a sensible default if the variable is not set
SPECIALIST_AGENT_MODEL = os.getenv("SPECIALIST_AGENT_MODEL", "gemini-1.5-flash-latest")
# --- ---

async def extract_content_from_url(url: str, include_headers: bool = False, tool_context: ToolContext = None) -> dict:
    """
    Extracts the primary textual content from a given web page URL using Crawl4AI.

    This function acts as a custom tool for an ADK agent. It leverages the
    AsyncWebCrawler to fetch and parse the content, returning a structured
    dictionary containing the extracted markdown, metadata, and status.

    Args:
        url (str): The URL of the web page to crawl and extract content from.
        include_headers (bool): Whether to include extracted H1-H6 headers
                                 in the response. Defaults to False.
        tool_context (ToolContext, optional): ADK-provided context object.

    Returns:
        dict: A dictionary summarizing the extraction result.
    """
    print(f" Attempting to extract content from: {url}")
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                include_headers=include_headers
            )

            page_title = getattr(result, 'title', None)
            markdown_content = getattr(result, 'markdown', "")
            headers_list = [h.text for h in getattr(result, 'headers',)] if include_headers else []

            if not page_title:
                page_title = url.split('/')[-1] if '/' in url else url
                if markdown_content:
                    lines = markdown_content.split('\n')
                    for line in lines:
                        if line.startswith('# '):
                            page_title = line.replace('# ', '').strip()
                            break

            content_length = len(markdown_content)
            truncated_content = markdown_content[:10000]
            has_truncated = content_length > 10000

            response = {
                "status": "success",
                "title": page_title,
                "url": url,
                "markdown_content": truncated_content,
                "content_length": content_length,
                "headers": headers_list,
                "word_count": len(markdown_content.split()),
                "has_truncated_content": has_truncated
            }
            print(f" Successfully extracted content from: {url}. Title: {page_title}")

            return response

    except Exception as e:
        print(f" Error extracting content from {url}: {e}")
        return {
            "status": "error",
            "url": url,
            "title": url,
            "markdown_content": "Extraction failed.",
            "content_length": 0,
            "headers":[],
            "word_count": 0,
            "has_truncated_content": False,
            "error_message": str(e)
        }

def create_content_extractor_agent():
    """
    Creates an agent specialized in extracting and analyzing content from URLs.

    This agent uses a FunctionTool wrapping the `extract_content_from_url`
    async function, which employs the Crawl4AI library.

    Returns:
        Agent: An instance of google.adk.Agent configured for content extraction.
    """
    # Wrap the custom async function using ADK's FunctionTool
    extract_content_tool = FunctionTool(func=extract_content_from_url)

    # Define the Content Extractor Agent
    extractor_agent = Agent(
        name="content_extractor",
        # Use the model name read from the environment variable
        model=SPECIALIST_AGENT_MODEL, #
        description="A specialized agent that extracts the main textual content from web page URLs using Crawl4AI.",
        instruction="""You are a web content extraction specialist.
        Your task is to retrieve the main textual content from a given URL.
        1.  Receive a specific URL as input.
        2.  Utilize the 'extract_content_from_url' tool to fetch and process the web page.
        3.  The tool will return a dictionary containing the extracted content ('markdown_content'), page title, URL, status, and other metadata.
        4.  Present the key information from the tool's response clearly:
            - State the page Title and URL.
            - Provide the extracted 'markdown_content'.
            - Mention if the content was truncated ('has_truncated_content').
            - Report the approximate 'word_count'.
            - If the 'status' is 'error', report the 'error_message'.
        5.  Focus solely on reporting the results of the extraction process. Do not add analysis or summarization unless the tool's output itself contains it.
        6.  If asked to extract from multiple URLs, process each one individually using the tool and present the results grouped by URL.
        """,
        # Provide the ADK FunctionTool instance to the agent
        tools=[extract_content_tool]
    )
    return extractor_agent

# Example of direct instantiation (useful for testing this agent module alone)
# if __name__ == '__main__':
#     agent = create_content_extractor_agent()
#     print(f"Content Extractor Agent '{agent.name}' created successfully using model '{SPECIALIST_AGENT_MODEL}'.")
#     async def test_extraction():
#         test_url = "https://google.github.io/adk-docs/" # Example URL
#         result = await extract_content_from_url(test_url)
#         print("\n--- Direct Tool Function Test ---")
#         import json
#         print(json.dumps(result, indent=2))
#         print("-------------------------------")
#     asyncio.run(test_extraction())