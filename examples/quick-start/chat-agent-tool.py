"""
A simple example of a Langroid Agent equipped with a Tool/function-calling.

The Agent has a "secret" list of numbers in "mind", and the LLM's task is to
find the smallest number in the list. The LLM can make use of the ProbeTool
which takes a number as argument. The agent's `probe` method handles this tool,
and returns the number of numbers in the list that are less than or equal to the
number in the ProbeTool message.

Run as follows:

python3 examples/quick-start/chat-agent-tool.py

For more explanation see
[the Getting Started guide](https://langroid.github.io/langroid/quick-start/chat-agent-tool/).
"""
from typing import List

import typer
from rich import print

import langroid as lr
import langroid.language_models as lm

app = typer.Typer()

class ProbeTool(lr.agent.ToolMessage):
    request: str = "probe"
    purpose: str = """
        To find how many numbers in my list are less than or equal to  
        the <number> you specify.
        """
    number: int

    @classmethod
    def examples(cls) -> List["ToolMessage"]:
        return [
            ProbeTool(number=5),
            ProbeTool(number=10),
        ]

    @classmethod
    def instructions(cls) -> str:
        return """
        You must remember to use the `probe` tool to present your number to me.
        Be sure to include both the "request" and "number" fields.
        """


class SpyGameAgent(lr.ChatAgent):
    def __init__(self, config: lr.ChatAgentConfig):
        super().__init__(config)
        self.numbers = [3, 4, 8, 11, 15]

    def probe(self, msg: ProbeTool) -> str:
        # return how many numbers in self.numbers are less or equal to msg.number
        return str(len([n for n in self.numbers if n <= msg.number]))


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    fn_api: bool = typer.Option(False, "--fn_api", "-f", help="use functions api"),
    model: str = typer.Option("", "--model", "-m", help="model name"),
) -> None:
    lr.utils.configuration.set_global(
        lr.utils.configuration.Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    print(
        """
        [blue]Welcome to the number guessing game!
        Enter x or q to quit
        """
        )
    spy_game_agent = SpyGameAgent(
        lr.ChatAgentConfig(
            name="Spy",
            llm = lr.language_models.OpenAIGPTConfig(
                chat_model=model or lm.OpenAIChatModel.GPT4_TURBO,
            ),
            vecdb=None,
            use_tools=not fn_api,
            use_functions_api=fn_api,
        )
    )

    spy_game_agent.enable_message(ProbeTool)
    task = lr.Task(
        spy_game_agent,
        system_message="""
            I have a list of numbers between 1 and 20.
            Your job is to find the smallest of them.
            To help with this, you can give me a number and I will
            tell you how many of my numbers are equal or less than your number.
            You must present your number to me using the `probe` tool/function.
            Once you have found the smallest number,
            you can say DONE and report your answer.
        """
    )
    task.run()




if __name__ == "__main__":
    app()
