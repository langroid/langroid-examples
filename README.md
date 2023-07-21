# langroid-examples

Examples of using the [Langroid](https://github.com/langroid/langroid) 
Multi-Agent Programming framework to build LLM applications.

## Set up virtual env and install `langroid`

```bash
# clone the repo and cd into repo root
git clone https://github.com/langroid/langroid-examples.git
cd langroid-examples

# create a virtual env under project root, .venv directory
python3 -m venv .venv

# activate the virtual env
. .venv/bin/activate

pip install langroid
```


## Set up environment variables (API keys, etc)

In the root of the repo, copy the `.env-template` file to a new file `.env`:
```bash
cp .env-template .env
```
Then insert your OpenAI API Key. If you don't have one, see [this OpenAI Page](https://help.openai.com/en/collections/3675940-getting-started-with-openai-api).
Your `.env` file should look like this:

```bash
OPENAI_API_KEY=your-key-here-without-quotes
````

Currently only OpenAI models are supported. Others will be added later
(Pull Requests welcome!).

All of the below are optional and not strictly needed to run any of the examples.

- **Qdrant** Vector Store API Key, URL. This is only required if you want to use Qdrant cloud.
  You can sign up for a free 1GB account at [Qdrant cloud](https://cloud.qdrant.io).
  If you skip setting up these, Langroid will use Qdrant in local-storage mode.
  Alternatively [Chroma](https://docs.trychroma.com/) is also currently supported.
  We use the local-storage version of Chroma, so there is no need for an API key.
- **Redis** Password, host, port: This is optional, and only needed to cache LLM API responses
  using Redis Cloud. Redis [offers](https://redis.com/try-free/) a free 30MB Redis account
  which is more than sufficient to try out Langroid and even beyond.
  If you don't set up these, Langroid will use a pure-python
  Redis in-memory cache via the [Fakeredis](https://fakeredis.readthedocs.io/en/latest/) library.
- **GitHub** Personal Access Token (required for apps that need to analyze git
  repos; token-based API calls are less rate-limited). See this
  [GitHub page](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

If you add all of these optional variables, your `.env` file should look like this:
```bash
OPENAI_API_KEY=your-key-here-without-quotes
GITHUB_ACCESS_TOKEN=your-personal-access-token-no-quotes
REDIS_PASSWORD=your-redis-password-no-quotes
REDIS_HOST=your-redis-hostname-no-quotes
REDIS_PORT=your-redis-port-no-quotes
QDRANT_API_KEY=your-key
QDRANT_API_URL=https://your.url.here:6333 # note port number must be included
```

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


