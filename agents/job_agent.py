# job_agent.py - Creates and runs the LangChain agent
# Receives LLM and tools from factories, invokes the agent

from langchain.agents import create_agent

from llms.llm_factory import get_llm
from tools.tool_factory import get_tools
from config import SYSTEM_PROMPT


def create_job_agent():
    """
    Assembles and returns the job search agent.
    LLM, tools, and prompt all come from their dedicated modules.
    """
    llm   = get_llm()
    tools = get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent