# agent_module/__init__.py

# Expose the root_agent from agent.py so ADK can find it easily
# when running from the parent directory (adk-research-team).
# Example command: adk web. (runs from adk-research-team/)
# ADK will look for agent_module.agent.root_agent or similar patterns.

from.agent import root_agent

# You can optionally add other initializations or imports here if needed.
print("Agent module initialized. Root agent 'research_coordinator' is available.")