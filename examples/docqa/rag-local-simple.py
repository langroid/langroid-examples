"""
RAG example using a local LLM, with ollama
"""
import os
import langroid as lr
import langroid.language_models as lm
from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# (1) Mac: Install latest ollama, then do this:
# ollama pull mistral:7b-instruct-v0.2-q4_K_M

# (2) Ensure you've installed the `litellm` extra with Langroid, e.g.
# pip install langroid[litellm], or if you use the `pyproject.toml` in this repo
# you can simply say `poetry install`

llm = lm.OpenAIGPTConfig(
    chat_model="litellm/ollama/mistral:7b-instruct-v0.2-q4_K_M",
    completion_model="litellm/ollama/mistral:7b-instruct-v0.2-q4_K_M",
    chat_context_length=4096, # set this based on model
    max_output_tokens=100,
    temperature=0.2,
    stream=True,
    timeout=45,
)

# test if basic chat works with this llm setup
#
# agent = lr.ChatAgent(
#     lr.ChatAgentConfig(
#         llm=llm
#     )
# )
#
# agent.llm_response("What is 3 + 4?")
#
# task = lr.Task(agent)
# verify you can interact with this in a chat loop on cmd line:
# task.run("Concisely answer some questions")

hf_embed_config = lr.embedding_models.SentenceTransformerEmbeddingsConfig(
    model_type="sentence-transformer",
    model_name="BAAI/bge-large-en-v1.5",
)

config = DocChatAgentConfig(
    default_paths= [],
    conversation_mode=True,
    llm = llm,
    relevance_extractor_config = lr.agent.special.RelevanceExtractorAgentConfig(
        llm=llm
    ),
    vecdb=lr.vector_store.QdrantDBConfig(
        collection_name="test1",
        replace_collection=True,
        embedding=hf_embed_config
    ),
    doc_paths= [
        "https://arxiv.org/pdf/2312.17238.pdf",
    ],
    system_message="""
    Answer some questions about docs. Be concise. 
    Start by asking me what I want to know
    """,
)

agent = DocChatAgent(config)
task = lr.Task(agent)
task.run()



