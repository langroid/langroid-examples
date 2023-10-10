"""
This example shows how to use Langroid to interact directly with an OpenAI GPT chat model,
i.e., without wrapping it in an Agent.

Run as follows:

python3 examples/quick-start/try-llm.py

For more explanation see the
[Getting Started guide](https://langroid.github.io/langroid/quick-start/llm-interaction/)
"""
import typer
from rich import print
from rich.prompt import Prompt

from langroid.language_models.base import LLMMessage, Role
from langroid.language_models.openai_gpt import (
    OpenAIGPT,
    OpenAIChatModel, OpenAIGPTConfig
)

from langroid.utils.configuration import set_global, Settings

app = typer.Typer()

def chat() -> None:
    print("[blue]Welcome to langroid!")

    cfg = OpenAIGPTConfig(
        chat_model=OpenAIChatModel.GPT4,
    )

    mdl = OpenAIGPT(cfg)
    messages = [
        LLMMessage(role=Role.SYSTEM, content="You are a helpful assistant"),
    ]
    while True:
        message = Prompt.ask("[blue]Human")
        if message in ["x", "q"]:
            print("[magenta]Bye!")
            break
        messages.append(LLMMessage(role=Role.USER, content=message))

        # use the OpenAI ChatCompletion API to generate a response
        response = mdl.chat(messages=messages, max_tokens=200)

        messages.append(response.to_LLMMessage())

        print("[green]Bot: " + response.message)


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
