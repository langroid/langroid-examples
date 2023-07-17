import typer

from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.task import Task
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging
from langroid.utils.constants import NO_ANSWER

app = typer.Typer()

setup_colored_logging()


def chat() -> None:
    config = ChatAgentConfig(
        llm = OpenAIGPTConfig(
            chat_model=OpenAIChatModel.GPT4,
        ),
        vecdb = None,
    )
    repeater_agent = ChatAgent(config)
    repeater_task = Task(
        repeater_agent,
        name = "Repeater",
        system_message="""
        Your job is to repeat whatever number you receive.
        """,
        llm_delegate=True,
        single_round=False,
    )
    even_agent = ChatAgent(config)
    even_task = Task(
        even_agent,
        name = "EvenHandler",
        system_message=f"""
        You will be given a number. 
        If it is even, divide by 2 and say the result, nothing else.
        If it is odd, say {NO_ANSWER}
        """,
        single_round=True,  # task done after 1 step() with valid response
    )

    odd_agent = ChatAgent(config)
    odd_task = Task(
        odd_agent,
        name = "OddHandler",
        system_message=f"""
        You will be given a number n. 
        If it is odd, return (n*3+1), say nothing else. 
        If it is even, say {NO_ANSWER}
        """,
        single_round=True,  # task done after 1 step() with valid response
    )

    repeater_task.add_sub_task([even_task, odd_task])
    repeater_task.run("3")


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
