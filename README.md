# langroid-examples


## Set up poetry env

Install [`poetry`](https://python-poetry.org/docs/#installation)
and use Python 3.11.

Create virtual env and install dependencies:

```bash
# clone the repo and cd into repo root
git clone https://github.com/langroid/langroid-examples.git
cd langroid-examples

# create a virtual env under project root, .venv directory
python3 -m venv .venv

# activate the virtual env
. .venv/bin/activate

# use poetry to install dependencies (these go into .venv dir)
poetry install
```

## Set up environment variables (API keys, etc)

Copy the `.env-template` file to a new file `.env` and
insert these secrets:
- OpenAI API key,
- GitHub Personal Access Token (needed by  PyGithub to analyze git repos;
  token-based API calls are less rate-limited).
- Redis Password (ask @pchalasani for this) for the redis cache.
- Qdrant API key (ask @pchalasani for this) for the vector db.

```bash
cp .env-template .env
# now edit the .env file, insert your secrets as above
``` 

Currently only OpenAI models are supported. Others will be added later.


