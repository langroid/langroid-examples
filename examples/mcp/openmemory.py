"""
OpenMemory Example - Langroid integration with mem0's OpenMemory knowledge graph system

This example demonstrates how to use Langroid with OpenMemory's MCP (Model Control Protocol)
tools to create an agent with persistent memory and knowledge graph capabilities.

What this example shows:
- Integration with OpenMemory's MCP server for persistent knowledge storage
- How to connect to and use OpenMemory's knowledge graph tools within a Langroid agent
- Creation of a contextually-aware agent that can access and store information in a knowledge graph

What is mem0/OpenMemory?
- OpenMemory is an open-source knowledge graph system for LLM applications
- It allows LLMs to store and retrieve information across conversations as a connected graph
- The MCP server provides tools for knowledge operations (create, retrieve, search)
- This example demonstrates using these knowledge graph capabilities within a Langroid agent

References:
https://mem0.ai/blog/how-to-make-your-clients-more-context-aware-with-openmemory-mcp/
https://docs.mem0.ai/openmemory/quickstart
https://github.com/mem0ai/mem0/tree/main/openmemory

Steps to create and connect to openmemory mcp server:

- git clone <https://github.com/mem0ai/mem0.git>
- cd mem0/openmemory
- cp api/.env.example api/.env
- add your OPENAI_API_KEY
- make build # builds the mcp server and ui
- make up  # runs openmemory mcp server and ui

You can check ui for your memories at
localhost:3000
"""

import os

from fastmcp.client.transports import SSETransport
from fire import Fire

import langroid as lr
import langroid.language_models as lm
from langroid.agent.tools.mcp.fastmcp_client import get_tools_async
from langroid.mytypes import NonToolAction

# trying to connect to openmemory
URL = "http://localhost:8765/mcp/openmemory/sse/"
# set userid to my own, got from os: $USER
userid = os.getenv("USER")


async def main(model: str = ""):
    transport = SSETransport(
        url=URL + userid,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )
    all_tools = await get_tools_async(transport)

    agent = lr.ChatAgent(
        lr.ChatAgentConfig(
            # forward to user when LLM doesn't use a tool
            handle_llm_no_tool=NonToolAction.FORWARD_USER,
            llm=lm.OpenAIGPTConfig(
                chat_model=model or "gpt-4.1-mini",
                max_output_tokens=1000,
                async_stream_quiet=False,
            ),
        )
    )

    # enable the agent to use all tools
    agent.enable_message(all_tools)
    # make task with interactive=False =>
    # waits for user only when LLM doesn't use a tool
    task = lr.Task(agent, interactive=False)
    await task.run_async(
        "Based on the TOOLs available to you, greet the user and"
        "tell them what kinds of help you can provide."
    )


if __name__ == "__main__":
    Fire(main)
