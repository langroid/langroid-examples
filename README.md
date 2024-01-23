# langroid-examples

Examples of using the [Langroid](https://github.com/langroid/langroid) 
Multi-Agent Programming framework to build LLM applications.

## Ubuntu
On ubuntu you'll need to make sure a few dependencies are installed including

postgrestql
```
sudo apt-get install libpq-dev
```
mysql dev
```
sudo apt install libmysqlclient-dev
```
and if you are on an earlier version of ubuntu, then python11
```
sudo apt install python3.11-dev build-essential
```
## Set up virtual env and install `langroid`

IMPORTANT: Please ensure you are using Python 3.11+. If you are using poetry,
you may be able to just run `poetry env use 3.11` if you have Python 3.11 available in your system.


```bash
# clone the repo and cd into repo root
git clone https://github.com/langroid/langroid-examples.git
cd langroid-examples

# create a virtual env under project root, .venv directory
python3 -m venv .venv

# activate the virtual env
. .venv/bin/activate

# install dependencies from pyproject.toml:
# This installs langroid with extras.
poetry install 
# or equivalently:
# pip install "langroid[litellm,hf-embeddings,postgres,mysql]"

# or to update an existing installation:
pip install --upgrade "langroid[litellm,hf-embeddings,postgres,mysql]"
```


## Set up environment variables (API keys, etc)

To get started, all you need is an OpenAI API Key.
If you don't have one, see [this OpenAI Page](https://help.openai.com/en/collections/3675940-getting-started-with-openai-api).
Currently only OpenAI models are supported. Others will be added later
(Pull Requests welcome!).

In the root of the repo, copy the `.env-template` file to a new file `.env`:
```bash
cp .env-template .env
```
Then insert your OpenAI API Key.
Your `.env` file should look like this (the organization is optional but may be
required in some scenarios):
```bash
OPENAI_API_KEY=your-key-here-without-quotes
OPENAI_ORGANIZATION=optionally-your-organization-id
````

Alternatively, you can set this as an environment variable in your shell
(you will need to do this every time you open a new shell):
```bash
export OPENAI_API_KEY=your-key-here-without-quotes
```

<details>
<summary><b>Optional Setup Instructions (click to expand) </b></summary>

- **Qdrant** Vector Store API Key, URL. This is only required if you want to use Qdrant cloud.
  You can sign up for a free 1GB account at [Qdrant cloud](https://cloud.qdrant.io).
  If you skip setting up these, Langroid will use Qdrant in local-storage mode.
  Alternatively [Chroma](https://docs.trychroma.com/) is also currently supported.
  We use the local-storage version of Chroma, so there is no need for an API key.
  Langroid uses Qdrant by default.
- **Redis** Password, host, port: This is optional, and only needed to cache LLM API responses
  using Redis Cloud. Redis [offers](https://redis.com/try-free/) a free 30MB Redis account
  which is more than sufficient to try out Langroid and even beyond.
  If you don't set up these, Langroid will use a pure-python
  Redis in-memory cache via the [Fakeredis](https://fakeredis.readthedocs.io/en/latest/) library.
- **Momento** Serverless Caching of LLM API responses (as an alternative to Redis).
  To use Momento instead of Redis:
  - enter your Momento Token in the `.env` file, as the value of `MOMENTO_AUTH_TOKEN` (see example file below),
  - in the `.env` file set `CACHE_TYPE=momento` (instead of `CACHE_TYPE=redis` which is the default).
- **GitHub** Personal Access Token (required for apps that need to analyze git
  repos; token-based API calls are less rate-limited). See this
  [GitHub page](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
- **Google Custom Search API Credentials:** Only needed to enable an Agent to use the `GoogleSearchTool`.
  To use Google Search as an LLM Tool/Plugin/function-call,
  you'll need to set up
  [a Google API key](https://developers.google.com/custom-search/v1/introduction#identify_your_application_to_google_with_api_key),
  then [setup a Google Custom Search Engine (CSE) and get the CSE ID](https://developers.google.com/custom-search/docs/tutorial/creatingcse).
  (Documentation for these can be challenging, we suggest asking GPT4 for a step-by-step guide.)
  After obtaining these credentials, store them as values of
  `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` in your `.env` file.
  Full documentation on using this (and other such "stateless" tools) is coming soon, but
  in the meantime take a peek at the test
  [`tests/main/test_google_search_tool.py`](tests/main/test_google_search_tool.py) to see how to use it.


If you add all of these optional variables, your `.env` file should look like this:
```bash
OPENAI_API_KEY=your-key-here-without-quotes
GITHUB_ACCESS_TOKEN=your-personal-access-token-no-quotes
CACHE_TYPE=redis # or momento
REDIS_PASSWORD=your-redis-password-no-quotes
REDIS_HOST=your-redis-hostname-no-quotes
REDIS_PORT=your-redis-port-no-quotes
MOMENTO_AUTH_TOKEN=your-momento-token-no-quotes # instead of REDIS* variables
QDRANT_API_KEY=your-key
QDRANT_API_URL=https://your.url.here:6333 # note port number must be included
GOOGLE_API_KEY=your-key
GOOGLE_CSE_ID=your-cse-id
```
</details>

## Running the examples

Typically, the examples are run as follows:

```bash
python3 examples/quick-start/chat-agent.py
```
Most of the scripts take additional flags:

- `-nc` turn off cache retrieval for LLM responses, 
    i.e., get fresh (rather than cached) responses each time you run it.
- `-d` turns on debug mode, showing more detail such as prompts etc.
- `-ns` turn off streaming output from the OpenAI API
- `-f` use OpenAI function-calling instead of Langroid Tool mechanism (where applicable).

All of the examples are best run on the command-line, preferably in a nice
terminal like [Iterm2](https://iterm2.com/).


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
