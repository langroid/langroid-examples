"""
Use Langroid to set up a collaboration among three agents:

- `Processor`: needs to transform a list of positive numbers, does not know how to
apply the transformations, and sends out each number so that one of two
specialized agents apply the transformation. It is instructed to avoid getting a
negative number.
- `EvenHandler` only transforms even numbers, otherwise returns a negative number
- `OddHandler` only transforms odd numbers, otherwise returns a negative number

Since the `Processor` must avoid getting a negative number, it needs to
specify a recipient for each number it sends out,
using `TO[<recipient>]:` at the beginning of the message.

However, the `Processor` often forgets to use this syntax, and in this situation
the `RecipientValidator` Agent asks the `Processor` to clarify the intended recipient.

Run as follows:

```bash
python3 examples/quick-start/two-agent-chat-num-router.py
```

For more explanation, see the
[Getting Started guide](https://langroid.github.io/langroid/quick-start/three-agent-chat-num-router/)
"""

import typer

from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.special.recipient_validator_agent import (
    RecipientValidator, RecipientValidatorConfig
)
from langroid.agent.task import Task
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging


app = typer.Typer()

setup_colored_logging()


def chat() -> None:
    config = ChatAgentConfig(
        llm = OpenAIGPTConfig(
            chat_model=OpenAIChatModel.GPT4,
        ),
        vecdb = None,
    )
    processor_agent = ChatAgent(config)
    processor_task = Task(
        processor_agent,
        name = "Processor",
        system_message="""
        You will receive a list of numbers from me (the user).
        Your goal is to apply a transformation to each number.
        However you do not know how to do this transformation.
        You can take the help of two people to perform the 
        transformation.
        If the number is even, send it to EvenHandler,
        and if it is odd, send it to OddHandler.
        
        IMPORTANT: send the numbers ONE AT A TIME
        
        The handlers will transform the number and give you a new number.        
        If you send it to the wrong person, you will receive a negative value.
        Your aim is to never get a negative number, so you must 
        clearly specify who you are sending the number to, by starting 
        your message with "TO[EvenHandler]:" or "TO[OddHandler]:".
        For example, you could say "TO[EvenHandler]: 4".
        
        Once all numbers in the given list have been transformed, 
        say DONE and show me the result. 
        Start by asking me for the list of numbers.
        """,
        llm_delegate=True,
        single_round=False,
    )
    even_agent = ChatAgent(config)
    even_task = Task(
        even_agent,
        name = "EvenHandler",
        system_message="""
        You will be given a number. 
        If it is even, divide by 2 and say the result, nothing else.
        If it is odd, say -10
        """,
        single_round=True,  # task done after 1 step() with valid response
    )

    odd_agent = ChatAgent(config)
    odd_task = Task(
        odd_agent,
        name = "OddHandler",
        system_message="""
        You will be given a number n. 
        If it is odd, return (n*3+1), say nothing else. 
        If it is even, say -10
        """,
        single_round=True,  # task done after 1 step() with valid response
    )
    validator_agent = RecipientValidator(
        RecipientValidatorConfig(
            recipients=["EvenHandler", "OddHandler"],
        )
    )
    validator_task = Task(validator_agent, single_round=True)

    processor_task.add_sub_task([validator_task, even_task, odd_task])
    processor_task.run()


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
