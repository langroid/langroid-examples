# langroid-examples


Examples of using the [Langroid](https://github.com/langroid/langroid) Multi-Agent 
Programming framework to build LLM applications.

:warning: Many of the examples in the `examples` folder in this repo are copied
from the corresponding folder in the core [langroid](https://github.com/langroid/langroid) repo, although the core repo is  generally more updated.
We occasionally update this repo with the latest versions from the langroid repo.
However, there are some examples in this repo that are not in the core langroid repo.

## Set up various keys in the `.env` file or as environment variables

Many of the examples require API keys for LLMs, vector-stores, redis-cache, etc.
Follow the instructions in the main [langroid](https://github.com/langroid/langroid) 
repo to set up these keys in the `.env` file,
or explicitly set the environment variables in your shell 
using, e.g., `export GEMINI_API_KEY=your_key`.


## Use `uv` to run the examples

First clone this repo, then go to the root dir (e.g., `cd langroid-examples`).

Install `uv`, see [here](https://docs.astral.sh/uv/getting-started/installation/)

Then run any of the examples as in the examples below:

```bash
uv run examples/basic/chat.py
uv run examples/docqa/chat.py
```
The `chainlit` examples can be run using:
```bash
uv run chainlit run examples/basic/simplest.py
```

This auto-installs a virtual env with the right dependencies and runs the example.
The first run may take a little bit of time as it installs the dependencies.

Many of the non-chainlit scripts take additional flags such as the following, but
see the specific scripts for details:

- `-m` to specify an LLM, e.g. `-m ollama/mistral`.
- `-nc` turn off cache retrieval for LLM responses,
  i.e., get fresh (rather than cached) responses each time you run it.
- `-d` turns on debug mode, showing more detail such as prompts etc.

All of the examples are best run on the command-line, preferably in a nice
terminal like [Iterm2](https://iterm2.com/).

## Run scripts with No repo cloning, No venv setup

In `pyproject.toml` we've set up some specific scripts to be runnable 
from anywhere, without cloning this repo, and without setting up any venv etc,
simply by using `uvx`, e.g.:

```bash
uvx --from langroid-examples chat
uvx --from langroid-examples completion
uvx --from langroid-examples chatdoc
uvx --from langroid-examples chatsearch
```

We'll add more scripts to this list as needed.
 

## For developers/contributors

### First-time set up of the project with `uv`

To set up the project the first time using `uv`, we did the following (it was 
only needed one time, but recording it here for future reference):

Initialize the project as an application named `examples` with Python 3.11:
```
uv init --app --name examples --python 3.11
```
This creates a `pyproject.toml` with the appropriate entries.

### Create virtual env and install dependencies

Then create a virtual env, activate it and install the dependencies:
```bash
uv venv --python 3.11
. ./.venv/bin/activate 
uv pip install -r pyproject.toml 
```


## Ubuntu
On ubuntu, for the SQL applications, you'll need to make sure a few dependencies are installed including:

- postgresql
```
sudo apt-get install libpq-dev
```
- mysql dev
```
sudo apt install libmysqlclient-dev
```
- and if you are on an earlier version of ubuntu, then python11
```
sudo apt install python3.11-dev build-essential
```

## Docker Instructions

We provide a containerized version of this repo via this [Docker Image](https://hub.docker.com/r/langroid/langroid).
All you need to do is set up environment variables in the `.env` file.
Please follow these steps to setup the container:

```bash
# get the .env file template from `langroid` repo
wget https://github.com/langroid/langroid/blob/main/.env-template .env

# Edit the .env file with your favorite editor (here nano):
# add API keys as explained above
nano .env

# launch the container
docker run -it  -v ./.env:/.env langroid/langroid

# Use this command to run any of the examples
python examples/<Path/To/Example.py> 
``` 
</details>
