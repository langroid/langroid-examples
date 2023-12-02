"""
Basic single-agent chat example, without streaming.

After setting up the virtual env as in README,
and you have your OpenAI API Key in the .env file, run like this:

chainlit run examples/chainlit/chat.py
"""

import chainlit as cl
from langroid import ChatAgent, ChatAgentConfig


@cl.on_chat_start
async def on_chat_start():
    sys_msg = "You are a helpful assistant. Be concise in your answers."
    config = ChatAgentConfig(
        system_message=sys_msg,
    )
    agent = ChatAgent(config)
    cl.user_session.set("agent", agent)


@cl.on_message
async def on_message(message: cl.Message):
    agent: ChatAgent = cl.user_session.get("agent")
    msg = cl.Message(content="")

    response = await agent.llm_response_async(message.content)
    msg.content = response.content
    await msg.send()
