# agent_module/content_extractor.py
from dotenv import load_dotenv
import os
import asyncio
from firecrawl import FirecrawlApp # Changed import
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
import concurrent.futures # For running async code in a separate thread
import sys # For the Windows event loop policy fix

# Load environment variables
load_dotenv()

# Initialize FirecrawlApp globally or manage its lifecycle as appropriate
firecrawl_app_instance = None
SPECIALIST_AGENT_MODEL = os.getenv("SPECIALIST_AGENT_MODEL", "gemini-1.5-flash-latest")


def get_firecrawl_app():
    """Initializes and returns a FirecrawlApp instance."""
    global firecrawl_app_instance
    if firecrawl_app_instance is None:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables. "
                             "Cannot initialize Firecrawl client.")
        firecrawl_app_instance = FirecrawlApp(api_key=api_key)
    return firecrawl_app_instance

# Define the core async logic outside the main sync function
async def _crawl_and_extract_async(url: str, include_headers: bool, tool_context: ToolContext = None):
    """The core async logic for crawling using Firecrawl."""
    print(f" Async crawl started for: {url}")
    try:
        firecrawl = get_firecrawl_app()

        scrape_result = await asyncio.to_thread(
            firecrawl.scrape_url,
            url,
        )

        # More robust check for a successful scrape and presence of data
        if not scrape_result or not hasattr(scrape_result, 'success') or not scrape_result.success:
            error_message = "Firecrawl failed to scrape the URL or returned an unsuccessful status."
            if scrape_result and hasattr(scrape_result, 'error') and scrape_result.error:
                error_message = f"Firecrawl error: {scrape_result.error}"
            # If success is false, data attribute might not exist or be relevant
            print(f" Error during Firecrawl scrape for {url}: {error_message}")
            return {
                "status": "error", "url": url, "error_message": error_message,
                "title": url.split('/')[-1] if '/' in url else url,
                "markdown_content": "No content extracted due to Firecrawl error.",
                "content_length": 0, "headers":[], "word_count": 0, "has_truncated_content": False
            }

        # Explicitly check for the 'data' attribute after confirming success
        if not hasattr(scrape_result, 'data') or not scrape_result.data:
            error_message = "Firecrawl returned success but no 'data' attribute or data is empty."
            print(f" Error during Firecrawl scrape for {url}: {error_message}")
            return {
                "status": "error", "url": url, "error_message": error_message,
                "title": url.split('/')[-1] if '/' in url else url,
                "markdown_content": "No content extracted, data missing in response.",
                "content_length": 0, "headers":[], "word_count": 0, "has_truncated_content": False
            }

        # Now we can safely access scrape_result.data
        data = scrape_result.data
        metadata = data.metadata if hasattr(data, 'metadata') and data.metadata else {} # Ensure metadata is a dict
        full_markdown_content = data.markdown if hasattr(data, 'markdown') and data.markdown else "No content extracted"

        page_title = metadata.get('title') if metadata else None
        if not page_title:
            page_title = url.split('/')[-1] if '/' in url else url
            if full_markdown_content and full_markdown_content!= "No content extracted":
                lines = full_markdown_content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        page_title = line.replace('# ', '').strip()
                        break
        
        if tool_context and full_markdown_content and full_markdown_content!= "No content extracted":
            tool_context.state[f"extracted_content_{url}"] = full_markdown_content

        truncated_content = full_markdown_content[:10000]
        content_len = len(full_markdown_content)
        has_truncated = content_len > 10000

        response = {
            "status": "success",
            "title": page_title,
            "url": metadata.get('sourceURL', url) if metadata else url,
            "markdown_content": truncated_content,
            "content_length": content_len,
            "headers":[],
            "word_count": len(truncated_content.split()),
            "has_truncated_content": has_truncated
        }
        print(f" Successfully extracted content from: {url}. Title: {page_title}")
        return response

    except Exception as e:
        print(f" Error during async extraction for {url}: {e}") # This will catch other unexpected errors
        return {
            "status": "error", "url": url, "error_message": f"An unexpected error occurred: {str(e)}",
            "title": url.split('/')[-1] if '/' in url else url,
            "markdown_content": "No content extracted due to an unexpected error.",
            "content_length": 0, "headers":[], "word_count": 0, "has_truncated_content": False
        }

# Synchronous wrapper function called by ADK's FunctionTool
def extract_content_from_url(url: str, include_headers: bool = False, tool_context: ToolContext = None) -> dict:
    """
    Synchronous wrapper that extracts content from a URL using Firecrawl
    by running the async logic in a separate thread.
    """
    print(f" Sync wrapper: Attempting to extract content from: {url}")

    def run_async_task_in_thread():
        if sys.platform == "win32":
             try:
                 current_policy = asyncio.get_event_loop_policy()
                 if not isinstance(current_policy, asyncio.WindowsSelectorEventLoopPolicy):
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                    print("Applied WindowsSelectorEventLoopPolicy in thread.")
                 else:
                    print("WindowsSelectorEventLoopPolicy already active in thread context.")
             except Exception as policy_error:
                 print(f"Could not set event loop policy in thread: {policy_error}")
        try:
            return asyncio.run(_crawl_and_extract_async(url, include_headers, tool_context))
        except Exception as run_error:
            print(f" Error running asyncio.run in thread for {url}: {run_error}")
            return {
                "status": "error", "url": url, "error_message": f"Thread execution error: {str(run_error)}",
                "title": url.split('/')[-1] if '/' in url else url,
                "markdown_content": "Extraction failed due to thread execution error.",
                "content_length": 0, "headers":[], "word_count": 0, "has_truncated_content": False
            }

    result = {}
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_async_task_in_thread)
            result = future.result(timeout=60) 
            print(f" Sync wrapper: Received result from thread for {url}")
    except concurrent.futures.TimeoutError:
        print(f" Sync wrapper: Timeout occurred while waiting for extraction thread for {url}")
        result = {
            "status": "error", "url": url, "error_message": "Extraction timed out after 60 seconds.",
            "title": url.split('/')[-1] if '/' in url else url,
            "markdown_content": "Extraction failed due to timeout.", "content_length": 0, "headers":[],
            "word_count": 0, "has_truncated_content": False
        }
    except Exception as pool_error:
        print(f" Sync wrapper: Error submitting task to thread pool for {url}: {pool_error}")
        result = {
            "status": "error", "url": url, "error_message": f"Thread pool error: {str(pool_error)}",
            "title": url.split('/')[-1] if '/' in url else url,
            "markdown_content": "Extraction failed due to thread pool error.", "content_length": 0, "headers":[],
            "word_count": 0, "has_truncated_content": False
        }
    return result

def create_content_extractor_agent():
    """
    Creates an agent specialized in extracting and analyzing content from URLs using Firecrawl.
    """
    extract_content_tool = FunctionTool(func=extract_content_from_url)
    extractor_agent = Agent(
        name="content_extractor",
        model=SPECIALIST_AGENT_MODEL, # Use the model from env
        description="A specialized agent that extracts and analyzes content from web pages using Firecrawl.",
        instruction="""You are a web content analysis specialist.
        When given a URL, use the extract_content_from_url tool to fetch and analyze its content.
        After extracting content:
        1. Report the page title and basic metadata (word count, if content was truncated).
        2. Note that HTTP-like headers are not available with the current extraction method.
        3. Highlight key information found in the content that's most relevant to the user's request.
        4. Note if there were any errors during extraction.
        When extracting content from multiple URLs, organize the information clearly by URL.
        If the extraction fails, explain the error and suggest possible solutions.
        """,
        tools=[extract_content_tool]
    )
    return extractor_agent