"""
Enhanced chat agent that remembers conversations using RAG.

Same functionalities as ConversationMemoryAgent but with the all the utility provided
by the DocChatAgent class.
In this case the "documents" are simply the past conversations stored in the vector database.

Run as follows:
python3 examples/quick-start/memory-chat-agent/memory_doc_chat_agent.py -u {username}

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
from typing import Callable, List, Optional, Tuple
from datetime import datetime
import langroid as lr
from langroid.utils.configuration import Settings
from langroid.vector_store.qdrantdb import QdrantDBConfig
from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig
from langroid.mytypes import Document, DocMetaData
from langroid.agent.chat_document import ChatDocument
from langroid.utils.constants import NO_ANSWER
from base_memory_chat_agent import BaseMemoryChatAgent


app = typer.Typer()

lr.utils.logging.setup_colored_logging()


class ConversationMemoryDocAgent(DocChatAgent, BaseMemoryChatAgent):
    """DocChatAgent with conversation memory capabilities."""

    def __init__(
        self,
        config: DocChatAgentConfig,
        username: Optional[str] = None,
    ) -> None:
        """Initialize ConversationMemoryDocAgent."""
        DocChatAgent.__init__(self, config)
        BaseMemoryChatAgent.__init__(self, username)
        self.set_system_message(self.generate_system_prompt())
        self.set_user_message("")

    def _create_conversation_document(self, message: str, response: str) -> Document:
        """Create conversation document from message and response."""
        return Document(
            content=f"User ({self.username}): {message}\nAssistant: {response}",
            metadata=DocMetaData(
                source="conversation",
                sender_name=self.username,
                timestamp=datetime.now().isoformat(),
                conversation_type="dialogue",
            ),
        )

    def _store_document(self, document: Document) -> None:
        """Store document in vector database."""
        self.ingest_docs([document], split=True)

    def answer_from_docs(self, query: str) -> ChatDocument:
        """
        Answer from documents with context.

        Override to include memory retrieval in response.
        If storage is empty, return LLM response.
        """
        answer = super().answer_from_docs(query)
        if not answer or answer.content == NO_ANSWER:
            return self.llm_response_messages(query)
        return answer

    def llm_response(
        self,
        query: None | str | ChatDocument = None,
    ) -> Optional[ChatDocument]:
        """Override llm_response to include memory retrieval in response."""
        if not self.llm_can_respond(query):
            return None

        message_str = query.content if isinstance(query, ChatDocument) else query
        enriched_message = self._get_enriched_message(message_str)
        response = super().llm_response(enriched_message)

        if response:
            self.store_conversation(message_str, response.content)

        return response

    def entity_responders(
        self,
    ) -> List[Tuple[lr.Entity, Callable[[None | str | ChatDocument], None | ChatDocument]]]:
        """We don't want to involve Agent responders in this case."""
        return [
            (lr.Entity.LLM, self.llm_response),
            (lr.Entity.USER, self.user_response),
        ]


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
    """Run the chatbot with memory using DocChatAgent."""
    print(
        """
        [blue]Welcome to the enhanced chatbot with memory!
        Enter x or q to quit
        """
    )

    def create_agent(username: Optional[str] = None) -> ConversationMemoryDocAgent:
        vecdb_config = setup_vecdb(docker_vecdb, reset_memory, username)

        config = DocChatAgentConfig(
            llm=lr.language_models.OpenAIGPTConfig(
                chat_model=lr.language_models.OpenAIChatModel.GPT4o_MINI,
            ),
            vecdb=vecdb_config,
            # Enable hypothetical answers for better RAG
            hypothetical_answer=True,
            # Enable query rephrasing for better recall
            n_query_rephrases=2,
            # Enable various search methods
            use_fuzzy_match=True,
            use_bm25_search=True,
            # Better ranking
            use_reciprocal_rank_fusion=True,
            # Add neighbors for better context
            n_neighbor_chunks=1,
            # Avoid redundancy in results
            rerank_diversity=True,
            # Handle long contexts better
            rerank_periphery=True,
            # Enable streaming for better UX
            stream=True,
            conversation_mode=True,
        )

        agent = ConversationMemoryDocAgent(config=config, username=username)

        # Check if collection is empty and handle appropriately
        if agent.vecdb is None or agent.vecdb.config.collection_name not in agent.vecdb.list_collections():
            print("[yellow]Starting fresh conversation - no previous memory found.")
        else:
            print("[green]Found existing conversation history.")

        return agent

    # Create agent with user context
    agent = create_agent(username=username)

    # Create task
    task = lr.Task(
        agent,
        name="MemoryBot",
    )

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
