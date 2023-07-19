"""
Example of a Langroid DocChatAgent equipped with a vector-store and LLM.

This is a specialized agent that can ingest (chunk, embed, store in vector-DB)
a collection of documents, and the LLM uses Retrieval Augmented Generation (RAG)
to answer questions about the documents.

Run as follows:

python3 examples/quick-start/chat-agent-docs.py

For more explanation see
[the Getting Started guide](https://langroid.github.io/langroid/quick-start/chat-agent-docs/).
"""
import typer
from rich import print

from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig
from langroid.vector_store.base import VectorStoreConfig
from langroid.agent.task import Task
from langroid.parsing.parser import Parser, Splitter, ParsingConfig
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging
from langroid.mytypes import Document, DocMetaData


app = typer.Typer()

setup_colored_logging()


documents = [
    Document(
        content="""
            In the year 2050, GPT10 was released. 
            
            In 2057, paperclips were seen all over the world. 
            
            Global warming was solved in 2060. 
            
            In 2061, the world was taken over by paperclips.         
            
            In 2045, the Tour de France was still going on.
            They were still using bicycles. 
            
            There was one more ice age in 2040.
            """,
        metadata=DocMetaData(source="wikipedia-2063"),
    ),
    Document(
        content="""
            We are living in an alternate universe 
            where Germany has occupied the USA, and the capital of USA is Berlin.
            
            Charlie Chaplin was a great comedian.
            In 2050, all Asian merged into Indonesia.
            """,
        metadata=DocMetaData(source="Almanac"),
    ),
]


def chat() -> None:
    print(
        """
        [blue]Welcome to the retrieval-augmented chatbot!
        Enter x or q to quit
        """
    )

    config = DocChatAgentConfig(
        llm=OpenAIGPTConfig(
            chat_model=OpenAIChatModel.GPT4,
        ),
        vecdb=VectorStoreConfig(
            type="qdrant",
            collection_name="quick-start-chat-agent-docs",
            replace_collection=True,
        ),
        parsing=ParsingConfig(
            separators=["\n\n"],
            splitter=Splitter.SIMPLE,
            n_similar_docs=2,
        ),
    )
    agent = DocChatAgent(config)
    agent.ingest_docs(documents)
    task = Task(agent)
    task.run()


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    chat()


if __name__ == "__main__":
    app()
