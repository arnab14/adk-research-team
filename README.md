# **ADK Multi-Agent Research Assistant Team**

## **Description**

This project demonstrates the construction and orchestration of a multi-agent research assistant team built **entirely using the Google Agent Development Kit (ADK)**. It exemplifies how ADK facilitates the creation of modular, collaborative AI systems by breaking down a complex research task into specialized agent roles. The team comprises of:

1.  **Search Agent:** Locates relevant web resources using the Tavily Search API.
2.  **Content Extractor Agent:** Fetches and extracts the primary textual content from specific URLs using the Crawl4AI library.
3.  **Summarizer Agent:** Generates concise summaries of provided text using the core capabilities of a Gemini LLM.  
4.  **Research Coordinator Agent:** Acts as the central orchestrator, receiving user requests, delegating tasks to the appropriate specialist agent using ADK’s AgentTool, synthesizing results, and
    delivering the final response.

This repository serves as a practical, code-first tutorial for developers aiming to leverage ADK’s features for building sophisticated, multi-agent applications. ADK promotes a development experience akin to traditional software engineering, emphasizing modularity, testability, and control.

## **Key Feature Highlight: ADK Multi-Agent Orchestration with AgentTool**

A primary objective of this example is to showcase ADK’s robust capabilities for orchestrating interactions within a multi-agent system. This is achieved through several core ADK features working in concert: 

-   **Modular Agent Design:** The overall research task is decomposed into distinct, specialized agents (search_agent, content_extractor, summarizer_agent). Each agent is implemented as a separate Python module and defined using ADK’s fundamental Agent class (an alias for LlmAgent). This modularity enhances code organization, promotes reusability, and allows for focused development and testing of each specialist’s function.  
-   **Coordinator Pattern:** A dedicated research_coordinator agent (agent.py) serves as the central point of contact and decision-maker. It interprets the user’s high-level goal and manages the workflow.
-   **Explicit Delegation via AgentTool:** This is the cornerstone of the orchestration pattern demonstrated here. The coordinator agent utilizes ADK’s AgentTool to wrap each specialist agent instance (search_agent_instance, extractor_agent_instance, summarizer_agent_instance). This wrapping mechanism is crucial: 
    -   It presents the specialist agents to the coordinator’s underlying LLM as if they were standard callable tools (like FunctionTool or LangchainTool).  
    -   The description field defined within each specialist agent (search_agent.py, etc.) becomes the primary information the coordinator’s LLM uses to determine *which* specialist “tool” is appropriate for a given sub-task. 
    -   When the coordinator’s LLM decides to invoke a specialist (e.g., generating a function call for search_agent), the ADK framework intercepts this and executes the corresponding AgentTool.
    -   The AgentTool then internally calls the run_async method of the wrapped specialist agent, effectively executing that agent’s logic.
    -   Upon completion, the specialist agent’s final response is captured by the AgentTool and returned to the coordinator agent as the output of the “tool” call.
    -   This abstraction significantly simplifies the coordinator’s instruction prompt. Instead of needing complex logic to manage state transitions or sequential execution, the coordinator focuses on *when* to delegate to *which* specialist based on the user request and the descriptions provided by the AgentTool wrappers. This explicit, tool-based delegation pattern is a powerful and intuitive way ADK enables the construction of hierarchical and collaborative agent teams.

## **Architecture Overview**

The system operates based on a coordinator-specialist (or manager-worker) pattern facilitated by ADK’s AgentTool:

1.  **User Interaction:** The user communicates their research request to the research_coordinator agent (the root_agent defined in agent.py).
2.  **Coordinator Analysis:** The research_coordinator’s LLM processes the user input, referencing its own instruction prompt and the description of the available tools (which are the wrapped specialist agents).
3.  **Delegation Decision:** Based on the analysis, the coordinator decides which specialist is needed. For instance, a request to “find papers on X” triggers the selection of the **search_agent tool**. A request to “summarize this text…” triggers the **summarizer_agent tool**. A request to “get content from URL Y” triggers the **content_extractor tool**.
4.  **Tool Invocation (Agent Execution):** The coordinator’s LLM generates a function call for the selected AgentTool. The ADK framework executes the run_async method of the corresponding specialist agent.
5.  **Specialist Task Execution:** The invoked specialist agent performs its designated task:
    -   search_agent: Uses its LangchainTool-wrapped Tavily tool to perform a web search.  
    -   content_extractor: Uses its FunctionTool-wrapped extract_content_from_url function (leveraging crawl4ai) to scrape web content.
    -   summarizer_agent: Uses its LLM and instruction prompt to generate a summary of the input text.
6.  **Result Propagation:** The specialist agent produces a final response. The AgentTool captures this response and returns it to the research_coordinator as the result of the tool call.
7.  **Synthesis & Final Response:** The research_coordinator receives the specialist’s output. If the task requires multiple steps (e.g., search -\> extract -\> summarize), it processes the intermediate result and decides the next delegation. Once all necessary information is gathered, the coordinator synthesizes the findings into a coherent, user-friendly final response, fulfilling the original request.

**Agent Roles Summary:**

| Agent Name           | File                 | Role                                       | Key ADK Tool Used by Agent | External Library/API | ADK Orchestration Mechanism Used    |
|:---------------------|:---------------------|:-------------------------------------------|:---------------------------|:---------------------|:------------------------------------|
| research_coordinator | agent.py             | Orchestrates tasks, delegates, synthesizes | AgentTool (x3)             | \-                   | LLM-driven delegation via AgentTool |
| search_agent         | search_agent.py      | Finds relevant web pages                   | LangchainTool              | Tavily Search API    | Invoked by AgentTool                |
| content_extractor    | content_extractor.py | Extracts text content from URLs            | FunctionTool               | Crawl4AI             | Invoked by AgentTool                |
| summarizer_agent     | summarizer.py        | Summarizes provided text                   | None (uses LLM core)       | \-                   | Invoked by AgentTool                |

## **Prerequisites**

-   **Python:** Version 3.9 or higher.1  
-   **Pip:** Python package installer.  
-   **Git:** For cloning the repository.  
-   **API Keys:**
    -   **Tavily API Key:** Required for the search_agent. Obtain from <https://tavily.com/>. A free tier is available.
    -   **Google AI API Key OR Vertex AI Setup:** Required for the Gemini models powering the agents.
        -   **Option 1 (Simpler):** Google AI Studio API Key. Obtain from <https://aistudio.google.com/>.
        -   **Option 2 (Cloud Integrated):** Google Cloud Project with billing enabled and the Vertex AI API enabled. Requires gcloud CLI authentication.
-   **(Potentially) Browser Binaries:** The crawl4ai library uses Playwright, which may require browser binaries (like Chromium) to be installed. The crawl4ai-setup command or playwright install usually handles this.

## **Installation**

1.  **Clone the repository:**
```Bash
    git clone https://github.com/arnab14/adk-research-team.git
    cd adk-research-team
```

2.  **Create and activate a Python virtual environment:**  
```Bash
    python -m venv.venv  
    # On Windows CMD:  
    .\.venv\Scripts\activate.bat
    # On macOS/Linux:  
    # source.venv/bin/activate  
    # On Windows PowerShell:  
    # .\.venv\Scripts\Activate.ps1
```
3.  **Install Python dependencies:**  
```Bash  
    pip install -r requirements.txt
```
4.  **(If needed for Crawl4AI/Playwright):** Run the browser setup command:  
```Bash
    # Recommended setup command for crawl4ai’s dependencies  
    crawl4ai-setup  
    # OR, if the above fails, try manual Playwright setup:  
    # python -m playwright install --with-deps chromium
```

## **Configuration**

1.  Create a file named .env in the root directory of the project (adk-research-team/).  
2.  Copy the following content into .env and replace the placeholder values with your actual API keys and configuration choices.
```Python
    #.env - Environment variables for ADK Research Team

    # -– Agent LLM Configuration -–  
    # Set to FALSE to use Google AI Studio API Key (requires GOOGLE_API_KEY)
    # Set to TRUE to use Google Cloud Vertex AI (requires GOOGLE_CLOUD_PROJECT & GOOGLE_CLOUD_LOCATION)
    # Ensure the corresponding variables below are uncommented and set correctly based on this value.
    GOOGLE_GENAI_USE_VERTEXAI=FALSE

    # -– Option 1: Google AI Studio -–  
    # Get your key from [https://aistudio.google.com/app/apikey\](https://aistudio.google.com/app/apikey)
    # Required if GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=PASTE_YOUR_GOOGLE_AI_API_KEY_HERE

    # -– Option 2: Google Cloud Vertex AI -–  
    # Required if GOOGLE_GENAI_USE_VERTEXAI=TRUE  
    # Ensure your environment is authenticated (e.g., \`gcloud auth application-default login\`)
    # and the Vertex AI API is enabled in your project.
    # GOOGLE_CLOUD_PROJECT=your-gcp-project-id  
    # GOOGLE_CLOUD_LOCATION=us-central1

    # -– Tool API Keys -–  
    # Get your key from \[https://tavily.com/\](https://tavily.com/) (Free tier available)
    # Required for the search_agent
    TAVILY_API_KEY=PASTE_YOUR_TAVILY_API_KEY_HERE
    
    # --- Agent Model Selection ---
    # Specify the model for the main coordinator agent (needs good reasoning/orchestration)
    # Examples: gemini-1.5-pro-latest, gemini-1.0-pro
    COORDINATOR_AGENT_MODEL=gemini-2.5-pro-exp-03-25

    # Specify the model for the specialist agents (can be faster/cheaper models)
    # Examples: gemini-1.5-flash-latest, gemini-1.0-pro
    SPECIALIST_AGENT_MODEL=gemini-2.5-flash-preview-04-17

    # Add any other API keys if you integrate more tools
```

**Environment Variable Details:**

| Variable Name             | Description                                                   | Example Value (Placeholder) | Required By        |
|:--------------------------|:--------------------------------------------------------------|:----------------------------|:-------------------|
| GOOGLE_GENAI_USE_VERTEXAI | FALSE for AI Studio key, TRUE for Vertex AI                   | FALSE                       | All Agents (Model) |
| GOOGLE_API_KEY            | Google AI Studio API Key (if USE_VERTEXAI=FALSE)              | AIzaSyxxxxxxxxxxxxxxxxxxx   | All Agents (Model) |
| GOOGLE_CLOUD_PROJECT      | Your Google Cloud Project ID (if USE_VERTEXAI=TRUE)           | your-gcp-project-id         | All Agents (Model) |
| GOOGLE_CLOUD_LOCATION     | Your Vertex AI region (if USE_VERTEXAI=TRUE)                  | us-central1                 | All Agents (Model) |
| TAVILY_API_KEY            | API Key for Tavily Search service (required for search agent) | tvly-xxxxxxxxxxxxxxxxxxxx   | search_agent       |

*Note: The python-dotenv library (included in requirements.txt) is used by the Python scripts to automatically load these variables from the .env file.*

## **Usage**

Make sure you are in the project’s root directory (adk-research-team/), your virtual environment is activated, and your .env file is correctly configured.

**Option 1: ADK Web UI (Recommended for Interaction & Debugging)**

This provides an interactive web interface for chatting with your agent and visualizing its execution steps.

1.  Run the following command in your terminal:
```Bash  
    adk web .
```
*(The . tells ADK to look for the agent package in the current directory).* 
2.  ADK will start a local server and provide a URL (typically http://localhost:8000 or http://127.0.0.1:8000). Open this URL in your web browser.
3.  In the web UI, select the research_coordinator agent from the top-left dropdown menu.
4.  Use the chat input box to interact with the agent team. You can also use microphone input if enabled.
5.  Explore the UI panels to inspect the sequence of agent calls, tool inputs/outputs, and state changes. This is invaluable for understanding the multi-agent orchestration.

**Option 2: ADK CLI**

This allows you to interact with the agent directly in your terminal.

1.  Run the following command: 
```Bash  
    adk run agent_module  
```
*(This tells ADK to run the agent defined in the agent_module package, which exports root_agent via its \_\_init\_\_.py)*
2.  Type your prompts directly into the terminal when prompted.
3.  Press Ctrl+C to exit the CLI interaction.

**Example Prompts:**

-   “Find information about the benefits of using Google ADK.” (Triggers search_agent)
-   “Extract the main content from this URL: https://google.github.io/adk-docs/” (Triggers content_extractor)
-   “Summarize the following text: \[paste some text\]” (Triggers summarizer_agent)
-   “Research the latest advancements in multi-agent systems using Google ADK, extract content from the top 2 results, and provide a concise summary.” (Triggers the full Search -\> Extract -\> Summarize sequence via the coordinator)

## **Code Structure**

The project follows the standard ADK convention for structuring agent code:

adk-research-team /
├── .env                        # API keys and configuration secrets  
├── requirements.txt            # Python package dependencies  
└── agent_module /              # The main Python package containing agent logic 
    ├── \_\_init\_\_.py             # Makes ‘agent_module’ a package and exports ‘root_agent’  
    ├── agent.py                # Defines the ‘root_agent’ (Research Coordinator) and orchestrates tools  
    ├── search_agent.py         # Defines the ‘search_agent’ specialist  
    ├── content_extractor.py    # Defines the ‘content_extractor’ specialist
    └── summarizer.py           # Defines the ‘summarizer_agent’ specialist

## **How It Works (Detailed Flow)**

1.  **Entry Point:** When you run adk web. or adk run agent_module, ADK loads the root_agent defined in agent_module/agent.py (via agent_module/\_\_init\_\_.py).
2.  **LLM & Instructions:** The root_agent (research_coordinator) uses its configured LLM (e.g., Gemini) and the detailed instruction prompt to process user input.
3.  **Tool Awareness:** The coordinator is aware of the search_tool, extractor_tool, and summarizer_tool (which are AgentTool wrappers around the specialist agents) listed in its tools parameter. The LLM uses the description of these wrapped agents to understand their capabilities.
4.  **Delegation via Function Calling:** Based on the user’s request and its instructions, the coordinator’s LLM determines if a specialist’s capability is needed. If so, it generates a “function call” targeting the appropriate AgentTool (e.g., call search_agent tool with query=“ADK benefits”).
5.  **ADK Routing:** The ADK framework receives this function call and routes it to the specified AgentTool.
6.  **Specialist Execution:** The AgentTool executes the run_async method of the specialist agent it wraps (e.g., search_agent.py runs).
7.  **Specialist Tool Usage:** The specialist agent may use its own configured tools (e.g., search_agent uses LangchainTool for Tavily; content_extractor uses FunctionTool for crawl4ai) or rely solely on its LLM (e.g., summarizer_agent).
8.  **Result Return:** The specialist agent completes its task and returns a result (e.g., search results, extracted text, summary).
9.  **Back to Coordinator:** The AgentTool captures this result and passes it back to the research_coordinator as the output of the tool call it initially made.
10. **Synthesis/Further Delegation:** The coordinator receives the specialist’s output. It might then:
    -   Generate the final response if the task is complete.
    -   Call another specialist if required by the workflow (e.g., call content_extractor with a URL from search_agent’s results).
    -   Synthesize information from multiple specialist calls before generating the final response.

## **ADK Ecosystem Context**

This example provides a foundation for building more complex agentic systems with ADK. While it runs locally, agents developed using ADK are designed with deployment and evaluation in mind:
-   **Evaluation:** ADK includes built-in tools (adk eval) for systematically testing agent performance against predefined datasets, evaluating both final outputs and execution steps.
-   **Deployment:** ADK agents can be containerized and deployed to various targets. Notably, ADK is optimized for deployment to **Google Cloud’s Vertex AI Agent Engine**, a fully managed, scalable runtime environment designed specifically for hosting production-grade AI agents. This provides a clear path from local development (as shown here) to robust cloud deployment.
-   **Broader Integration:** ADK is the framework underpinning agents in Google products like **Google Agentspace**, an enterprise AI platform combining search, agents, and organizational knowledge. Building with ADK aligns with Google’s broader strategy for enterprise AI and agentic systems.

Understanding this ecosystem context is valuable for developers considering ADK for real-world applications, as it demonstrates a supported pathway to production and integration within Google Cloud.

## **Contributing**

Contributions are welcome! Please feel free to submit pull requests or open issues to improve this example.

## **License**

This project is licensed under the GNU General Public License v3.0 - see the(LICENSE) file for details.

#### **Works cited**

1.  Quickstart - Agent Development Kit - Google, accessed May 5, 2025, <https://google.github.io/adk-docs/get-started/quickstart/>
2.  The Complete Guide to Google’s Agent Development Kit (ADK) - Sid Bharath, accessed May 5, 2025, <https://www.siddharthbharath.com/the-complete-guide-to-googles-agent-development-kit-adk/>
3.  Tavily, accessed May 5, 2025, <https://tavily.com/>
4.  Quickstart: Build an agent with the Agent Development Kit \| Generative AI on Vertex AI, accessed May 5, 2025, <https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart>
5.  Home - Crawl4AI Documentation (v0.6.x), accessed May 5, 2025, <https://docs.crawl4ai.com/>
6.  Quick Start - Crawl4AI Documentation (v0.6.x), accessed May 5, 2025, <https://docs.crawl4ai.com/core/quickstart/>
7.  AI web scraper built with Crawl4AI for extracting structured leads data from websites. - GitHub, accessed May 5, 2025, <https://github.com/kaymen99/ai-web-scraper>
8.  Crawl4AI · PyPI, accessed May 5, 2025, <https://pypi.org/project/Crawl4AI/0.3.7/>
9.  unclecode/crawl4ai: Crawl4AI: Open-source LLM Friendly Web Crawler & Scraper. Don’t be shy, join here: https://discord.gg/jP8KfhDhyN - GitHub, accessed May 5, 2025, <https://github.com/unclecode/crawl4ai>
10. Agent Development Kit: Making it easy to build multi-agent applications, accessed May 5, 2025, <https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/>
11. Agent Development Kit - Google, accessed May 5, 2025, <https://google.github.io/adk-docs/>
12. google/adk-python: An open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. - GitHub, accessed May 5, 2025, <https://github.com/google/adk-python>
13. Just did a deep dive into Google’s Agent Development Kit (ADK). Here are some thoughts, nitpicks, and things I loved (unbiased) - Reddit, accessed May 5, 2025, <https://www.reddit.com/r/AI_Agents/comments/1jvsu4l/just_did_a_deep_dive_into_googles_agent/>
14. Google Agentspace Gets Smarter and Easier to Build Agents and Connect Them, accessed May 5, 2025, <https://aragonresearch.com/google-agentspace-gets-smarter-easier-to-build/>
15. Google Agentspace, accessed May 5, 2025, <https://cloud.google.com/products/agentspace>
16. Cloud Next: Google Agentspace announces new features for enterprise, accessed May 5, 2025, <https://blog.google/feed/cloud-next-latest-features-google-agentspace/>
17. Google Agentspace: NotebookLM, AI agents and internal search, accessed May 5, 2025, <https://blog.google/feed/google-agentspace/>
18. Google Agentspace enables the agent-driven enterprise \| Google Cloud Blog, accessed May 5, 2025, <https://cloud.google.com/blog/products/ai-machine-learning/google-agentspace-enables-the-agent-driven-enterprise>