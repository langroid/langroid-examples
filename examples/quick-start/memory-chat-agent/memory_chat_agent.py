"""
Enhanced chat agent that remembers conversations using RAG.

Basically it stores the conversation turns in a vector database and retrieves
relevant context to personalize responses for different users with different sessions.

Run as follows
python3 examples/quick-start/memory-chat-agent/memory_chat_agent.py -u {username}

To test try 2 different run with the same username and different messages:

run 1
    USER: I am a software engineer
    LLM: {some response}
    <<quit>>

run 2
    USER: What do I do for a living?
    LLM: {some response} should be related to software engineering
"""

import typer
from rich import print
from typing import Optional, List
from langroid.language_models.base import (
    LLMMessage,
)
from datetime import datetime
import langroid as lr
from langroid.utils.configuration import Settings
from langroid.vector_store.qdrantdb import QdrantDBConfig
from langroid.agent.chat_document import ChatDocument
from langroid.mytypes import DocMetaData
from base_memory_chat_agent import BaseMemoryChatAgent

app = typer.Typer()

lr.utils.logging.setup_colored_logging()


class MemoryChatAgent(lr.ChatAgent, BaseMemoryChatAgent):
    """Chat agent with conversation memory."""

    def __init__(
        self,
        config: lr.ChatAgentConfig,
        task: Optional[List[LLMMessage]] = None,
        username: Optional[str] = None,
    ) -> None:
        """Initialize MemoryChatAgent."""
        lr.ChatAgent.__init__(self, config, task)
        BaseMemoryChatAgent.__init__(self, username)

    def _create_conversation_document(self, message: str, response: str) -> ChatDocument:
        """Create conversation document from message and response."""
        return ChatDocument(
            content=f"User ({self.username}): {message}\nAssistant: {response}",
            metadata=DocMetaData(
                sender=lr.Entity.USER,
                sender_name=self.username,
                timestamp=datetime.now().isoformat(),
                conversation_type="dialogue",
            ),
        )

    def _store_document(self, document: ChatDocument) -> None:
        """Store document in vector database."""
        self.vecdb.add_documents([document])

    def llm_response(self, message: Optional[str | ChatDocument] = None) -> Optional[ChatDocument]:
        """Enhanced llm_response with memory retrieval."""
        if not self.llm_can_respond(message):
            return None

        message_str = message.content if isinstance(message, ChatDocument) else message
        enriched_message = self._get_enriched_message(message_str)
        response = super().llm_response(enriched_message)

        if response:
            self.store_conversation(message_str, response.content)

        return response


def setup_vecdb(docker: bool, reset: bool, username: Optional[str] = None) -> QdrantDBConfig:
    """Configure vector database."""
    collection_name = "conversation_memory"
    if username:
        collection_name += f"_{username}"

    return QdrantDBConfig(collection_name=collection_name, replace_collection=reset, docker=docker)


def chat(
    docker_vecdb: bool = False,
    reset_memory: bool = False,
    username: Optional[str] = "user",
    init_message: str = "",
) -> None:
    """Run the chatbot with memory."""
    print(
        """
        [blue]Welcome to the enhanced chatbot with memory!
        Enter x or q to quit
        """
    )

    def create_agent(username: Optional[str] = None) -> MemoryChatAgent:
        vecdb_config = setup_vecdb(docker_vecdb, reset_memory, username)

        config = lr.ChatAgentConfig(
            llm=lr.language_models.OpenAIGPTConfig(
                chat_model=lr.language_models.OpenAIChatModel.GPT4,
            ),
            vecdb=vecdb_config,
        )

        agent = MemoryChatAgent(config=config, username=username)
        # Update system message based on user
        agent.set_system_message(agent.generate_system_prompt())
        return agent

    # Initial agent without user context
    agent = create_agent(username=username)

    # Create task
    task = lr.Task(agent, name="MemoryBot")

    # Run the task
    task.run(msg=init_message or None)


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    docker: bool = typer.Option(True, "--docker", help="use docker for vector database"),
    reset: bool = typer.Option(False, "--reset", help="reset conversation memory"),
    username: str = typer.Option("user", "--user", "-u", help="user name"),
    init_message: str = typer.Option("", "--msg", "-m", help="initial message"),
) -> None:
    """Main app function."""
    lr.utils.configuration.set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    chat(docker_vecdb=docker, reset_memory=reset, username=username, init_message=init_message)


if __name__ == "__main__":
    app()
