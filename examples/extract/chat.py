"""
Extract structured data from text using function_calling/tools.
Inspired by this W&B example notebook, but goes beyond, i.e. gets slightly
more structured output to include model quality:
https://wandb.ai/darek/llmapps/reports/Using-LLMs-to-Extract-Structured-Data-OpenAI-Function-Calling-in-Action--Vmlldzo0Nzc0MzQ3

Example usage, to use Langroid tool:

python3 examples/basic/extract.py

Use -f option to use OpenAI function calling API instead of Langroid tool.

"""
import textwrap
import json

import typer
from typing import List
from rich import print
from pydantic import BaseModel

from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.task import Task
from kaggle_text import kaggle_description
from langroid.agent.tool_message import ToolMessage
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging

app = typer.Typer()

setup_colored_logging()

class MethodQuality(BaseModel):
    """
    Structure we want to extract
    """
    name: str
    quality: str


class MethodsList(ToolMessage):
    request: str = "methods_list"
    purpose: str = """
        Make a list of Machine Learning methods and their quality
        """
    methods: List[MethodQuality]
    result: str = ""

    @classmethod
    def examples(cls) -> List["ToolMessage"]:
        return [
            cls(
                methods=[
                    MethodQuality(name="XGBoost", quality="good"),
                    MethodQuality(name="Random Forest", quality="bad"),
                ],
                result="",
            ),
        ]


class ExtractorAgent(ChatAgent):
    def methods_list(self, message: MethodsList) -> str:
        """
        Method to handle the MethodsList ToolMessage
        Args:
            message: MethodsList ToolMessage
        Returns:
            str: JSON string of the methods list
        """
        print(
            f"""
        DONE! Successfully extracted ML Methods list:
        {message.methods}
        """
        )
        return "\n".join(json.dumps(m.dict()) for m in message.methods)


def chat(config: ChatAgentConfig) -> None:
    print(
        textwrap.dedent(
            """
        [blue]Welcome to the basic chatbot!
        Enter x or q to quit
        """
        ).strip()
    )
    agent = ExtractorAgent(config)
    agent.enable_message(
        MethodsList,
        use=True,
        handle=True,
        force=True,
    )

    task = Task(
        agent,
        system_message="""
        You are a machine learning engineer analyzing Kaggle competition solutions.
        Your goal is to create a list of Machine Learning methods and their 
        quality, based on the user's description. 
        The "quality" can be "good" or "bad", based on your understanding of the 
        description.
        The methods must be very short names, not long phrases.
        Don't add any methods not mentioned in the solution description.
        Call the methods_list function or Tool to accomplish this.
        """,
        llm_delegate=False,
        single_round=False,
    )
    task.run(kaggle_description)


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    fn_api: bool = typer.Option(False, "--fn_api", "-f", help="use functions api"),
) -> None:
    config = ChatAgentConfig(
        llm = OpenAIGPTConfig(
            chat_model=OpenAIChatModel.GPT4,
        ),
        use_functions_api=fn_api,
        use_tools=not fn_api,
    )

    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    chat(config)


if __name__ == "__main__":
    app()
