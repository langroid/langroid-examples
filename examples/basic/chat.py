"""
The most basic chatbot example, using the default settings.
A single Agent allows you to chat with a pre-trained Language Model.

Run like this:

python3 examples/basic/chat.py

Use optional arguments to change the settings, e.g.:

-m "local" to use a model served locally at an OpenAI-API-compatible endpoint
[ Ensure the API endpoint url matches the one in the code below, or edit it. ]
OR
- m "litellm/ollama/llama2" to use any model supported by litellm
(see list here https://docs.litellm.ai/docs/providers)
[Note you must prepend "litellm/" to the model name required in the litellm docs,
e.g. "ollama/llama2" becomes "litellm/ollama/llama2",
"bedrock/anthropic.claude-instant-v1" becomes
"litellm/bedrock/anthropic.claude-instant-v1"]

-ns # no streaming
-d # debug mode
-nc # no cache
-ct momento # use momento cache (instead of redis)

For details on running with local Llama model, see:
https://langroid.github.io/langroid/blog/2023/09/14/using-langroid-with-local-llms/
"""
import typer
from rich import print
from rich.prompt import Prompt
from pydantic import BaseSettings
from dotenv import load_dotenv

from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.task import Task
from langroid.language_models.openai_gpt import OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging


app = typer.Typer()

setup_colored_logging()

# Create classes for non-OpenAI model configs

# OPTION 1: LiteLLM-supported models
# -----------------------------------
# For any model supported by litellm
# (see list here https://docs.litellm.ai/docs/providers)
# The `chat_model` should be specified as "litellm/" followed by
# the chat_model name in the litellm docs.
# In this case Langroid uses the litellm adapter library to
# translate between OpenAI API and the model's API.
# For external (remote) models, typical there will be specific env vars
# (e.g. API Keys, etc) that need to be set.
# If those are not set, you will get an err msg saying which vars need to be set.

# OPTION 2: Local models served at an OpenAI-compatible API endpoint
# -----------------------------------------------------------------
# Use this config for any model that is locally served at an
# OpenAI-compatible API endpoint, for example, using either the
# litellm proxy server https://docs.litellm.ai/docs/proxy_server
# or the oooba/text-generation-webui server
# https://github.com/oobabooga/text-generation-webui/tree/main/extensions/openai
#
# In this case the `chat_model` name should be specified as
# "local/localhost:8000/v1" or "local/localhost:8000" or other port number
# depending on how you launch the model locally.
# Langroid takes care of extracting the local URL to set the `api_base`
# of the config so that the `openai.*` completion functions can be used
# without having to rely on adapter libraries like litellm.

MyLLMConfig = OpenAIGPTConfig.create(prefix="myllm")
my_llm_config = MyLLMConfig(
    chat_model="litellm/ollama/llama2",
    # or, other possibilities for example:
    # "litellm/bedrock/anthropic.claude-instant-v1"
    # "litellm/ollama/llama2"
    # "local/localhost:8000/v1"
    # "local/localhost:8000"
    chat_context_length=2048,  # adjust based on model
)


class CLIOptions(BaseSettings):
    model: str = ""

    class Config:
        extra = "forbid"
        env_prefix = ""


def chat(opts: CLIOptions) -> None:
    print(
        """
        [blue]Welcome to the basic chatbot!
        Enter x or q to quit at any point.
        """
    )

    load_dotenv()

    # use the appropriate config instance depending on model name
    if opts.model.startswith("litellm/") or opts.model.startswith("local/"):
        # e.g. litellm/ollama/llama2 or litellm/bedrock/anthropic.claude-instant-v1
        llm_config = my_llm_config
        llm_config.chat_model = opts.model

    else:
        llm_config = OpenAIGPTConfig()

    default_sys_msg = "You are a helpful assistant. Be concise in your answers."

    sys_msg = Prompt.ask(
        "[blue]Tell me who I am. Hit Enter for default, or type your own\n",
        default=default_sys_msg,
    )

    config = ChatAgentConfig(
        system_message=sys_msg,
        llm=llm_config,
    )
    agent = ChatAgent(config)
    task = Task(agent)
    # OpenAI models are ok with just a system msg,
    # but in some scenarios, other (e.g. llama) models
    # seem to do better when kicked off with a sys msg and a user msg.
    # In those cases we may want to do task.run("hello") instead.
    task.run()


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    model: str = typer.Option("", "--model", "-m", help="model name"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    cache_type: str = typer.Option(
        "redis", "--cachetype", "-ct", help="redis or momento"
    ),
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
            cache_type=cache_type,
        )
    )
    opts = CLIOptions(model=model)
    chat(opts)


if __name__ == "__main__":
    app()
