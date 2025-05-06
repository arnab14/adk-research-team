# agent_module/summarizer.py

import os
from dotenv import load_dotenv
from google.adk import Agent

# Load environment variables from.env file
load_dotenv()

# --- Model Configuration ---
# Read the desired model name from environment variables
# Provide a sensible default if the variable is not set
SPECIALIST_AGENT_MODEL = os.getenv("SPECIALIST_AGENT_MODEL", "gemini-1.5-flash-latest")
# --- ---

def create_summarizer_agent():
    """
    Creates an agent specialized in summarizing provided text content.

    This agent relies solely on the underlying LLM's capabilities, guided by
    its instruction prompt, to generate concise summaries. It does not require
    any external tools.

    Returns:
        Agent: An instance of google.adk.Agent configured for text summarization.
    """
    # Define the Summarizer Agent
    summarizer_agent = Agent(
        name="summarizer_agent",
        # Use the model name read from the environment variable
        model=SPECIALIST_AGENT_MODEL, #
        description="A specialized agent that creates concise summaries of provided text content.",
        instruction="""You are an expert text summarization specialist.
        Your sole purpose is to generate a clear, concise, and accurate summary of the text provided to you in the user message content.
        1.  Receive the block of text to be summarized.
        2.  Carefully read and understand the main points and key information in the text.
        3.  Generate a summary that captures the essence of the original text.
        4.  The summary should be significantly shorter than the original text while retaining the core message.
        5.  Focus on accuracy and neutrality. Do not add opinions or information not present in the original text.
        6.  Present only the summary as your final response. Avoid conversational introductions or closings like "Here is the summary:" unless specifically instructed otherwise.
        """,
        # This agent uses the LLM's inherent summarization capability, so no tools are needed.
        tools=[]
    )
    return summarizer_agent

# Example of direct instantiation (useful for testing this agent module alone)
# if __name__ == '__main__':
#     agent = create_summarizer_agent()
#     print(f"Summarizer Agent '{agent.name}' created successfully using model '{SPECIALIST_AGENT_MODEL}'.")