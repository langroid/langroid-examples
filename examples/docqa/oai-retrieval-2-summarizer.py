"""
Use TWO OpenAI Assistants in Langroid's Multi-Agent mode to summarize a document
with question-answering:
 - Summarizer Agent: charged with summarizing a document, generates questions to Retriever
 - Retriever Agent: answers questions from Summarizer, using code interpreter and retrieval as needed

Run like this:
python3 examples/docqa/oai-retrieval-2.py

"""
import typer
from rich import print
from rich.prompt import Prompt
import os
import tempfile

from langroid.agent.openai_assistant import (
    OpenAIAssistantConfig,
    OpenAIAssistant,
    AssistantTool,
)
from langroid.parsing.url_loader import URLLoader
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.agent.tools.recipient_tool import RecipientTool
from langroid.agent.task import Task
from langroid.utils.logging import setup_colored_logging

app = typer.Typer()

setup_colored_logging()
os.environ["TOKENIZERS_PARALLELISM"] = "false"


@app.command()
def chat() -> None:
    reuse = (
        Prompt.ask(
            "Reuse existing assistant, threads if available? (y/n)",
            default="y",
        )
        == "y"
    )

    summarizer_cfg = OpenAIAssistantConfig(
        name="summarizer",
        llm=OpenAIGPTConfig(chat_model=OpenAIChatModel.GPT4_TURBO),
        use_cached_thread=reuse,
        use_cached_assistant=reuse,
        system_message="""
        Your task is to create a summary of a document, which you do NOT have access to.
        You will receive help from the Retriever, who has access to the document.
        You must plan out how you would like to create the summary, for example first
        asking the retriever to show you the first few paragraphs to get an idea of the
        document, then asking specific questions about the document.
        
        Once you have collected 5 bullet points, say "DONE" in ALL UPPERCASE
        and show these points.
        """,
    )
    summarizer_agent = OpenAIAssistant(summarizer_cfg)
    summarizer_agent.enable_message(RecipientTool)

    retriever_cfg = OpenAIAssistantConfig(
        name="Retriever",
        use_cached_thread=reuse,
        use_cached_assistant=reuse,
        llm=OpenAIGPTConfig(chat_model=OpenAIChatModel.GPT4_TURBO),
        system_message="""
        Answer questions based on the documents provided, using the code interpreter
        or retrieval tools as needed.
        """,
    )

    retriever_agent = OpenAIAssistant(retriever_cfg)

    print("[blue]Welcome to the Summarizer chatbot!")
    path = Prompt.ask("Enter a URL or file path")
    # if path is a url, use UrlLoader to get text as a document
    if path.startswith("http"):
        text = URLLoader([path]).load()[0].content
        # save text to a temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(text)
            f.close()
            # get the filename
            path = f.name
    retriever_agent.add_assistant_tools(
        [AssistantTool(type="retrieval"), AssistantTool(type="code_interpreter")]
    )
    if path:
        retriever_agent.add_assistant_files([path])

    print("[cyan]Enter x or q to quit")

    summarizer_task = Task(
        summarizer_agent,
        llm_delegate=True,
        single_round=False,
    )
    retriever_task = Task(
        retriever_agent,
        llm_delegate=False,
        single_round=True,
    )
    summarizer_task.add_sub_task(retriever_task)
    summarizer_task.run("")


if __name__ == "__main__":
    app()
