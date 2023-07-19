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

Copy the `.env-template` file to a new file `.env` and
insert these secrets:
- **OpenAI API** key (required): If you don't have one, see [this OpenAI Page](https://help.openai.com/en/collections/3675940-getting-started-with-openai-api).
- **Qdrant** Vector Store API Key (required for apps that need retrieval from
  documents): Sign up for a free 1GB account at [Qdrant cloud](https://cloud.qdrant.io)
  Alternatively [Chroma](https://docs.trychroma.com/) is also currently supported.
  We use the local-storage version of Chroma, so there is no need for an API key.
- **GitHub** Personal Access Token (required for apps that need to analyze git
  repos; token-based API calls are less rate-limited). See this
  [GitHub page](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
- **Redis** Password (optional, only needed to cache LLM API responses):
  Redis [offers](https://redis.com/try-free/) a free 30MB Redis account
  which is more than sufficient to try out Langroid and even beyond.

```bash
cp .env-template .env
# now edit the .env file, insert your secrets as above
``` 

Your `.env` file should look like this:
```bash
OPENAI_API_KEY=<your key>
GITHUB_ACCESS_TOKEN=<your token>
REDIS_PASSWORD=<your password>
QDRANT_API_KEY=<your key>
```

Currently only OpenAI models are supported. Others will be added later.

## Running the examples

Typically, the examples are run as follows:

```bash
python3 examples/quick-start/chat-agent.py
```

All of the examples are best run on the command-line, preferably in a nice
terminal like [Iterm2](https://iterm2.com/).


