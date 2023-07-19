import typer
from rich import print

from langroid.agent.special.doc_chat_agent import DocChatAgentConfig, PDFChatAgent
from langroid.vector_store.base import VectorStoreConfig
from langroid.parsing.parser import ParsingConfig, Splitter
from langroid.agent.task import Task
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging
from langroid.parsing.urls import get_list_from_user

app = typer.Typer()

setup_colored_logging()


def chat() -> None:
    config = DocChatAgentConfig()
    config.vecdb = VectorStoreConfig(
        type="qdrant",
        collection_name="pdf-chat",
        replace_collection=True,
    )

    config.llm = OpenAIGPTConfig(
        chat_model=OpenAIChatModel.GPT3_5_TURBO, max_output_tokens=100
    )
    config.parsing = ParsingConfig(
        splitter=Splitter.TOKENS,
        chunk_size=100,
    )

    pdf_agent = PDFChatAgent(config)

    print("[blue]Welcome to the document chatbot!")
    print("[cyan]Enter x or q to quit, or ? for evidence")
    print(
        """
        [blue]Enter some PDFs:
        """.strip()
    )
    inputs = get_list_from_user()
    pdf_agent.config.doc_paths = inputs
    pdf_agent.ingest_pdf()

    pdf_task = Task(
        pdf_agent,
        name="DocAgent",
        llm_delegate=False,
        single_round=True,
        system_message="""You will receive various questions about some documents, and
        your job is to answer them concisely in at most 2 sentences, citing sources.
        """,
    )

    pdf_task.run()


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
        )
    )
    chat()


if __name__ == "__main__":
    app()
