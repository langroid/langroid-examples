'''
Answer a question about a document using Langroid's DocChatAgent,
which uses Dynamic Context Retrieval (DCR) to retrieve a desired window of
chunks around the matching chunk.

Ensure you have followed the install instructions in the README.md file.
Essentially, have a virtual env and do `pip install langroid`.
Ensure you have OPENAI_API_KEY=... set in your .env file in project root.

Run like this, from project root:
$ python3 examples/docqa/retrieve-context-langroid.py

Optional arguments:
    --path=... : path to text file to extract from (default is examples/docqa/giraffes.txt)
    --query="..." : query to run (default is "What do we know about giraffes?")
    --k=... : number of neighbor chunks to retrieve (default is 2)

Also see this colab:
https://colab.research.google.com/drive/1JvH6CO9AS7CaWK0GTblZGesJoo9Jjyn7
'''

import langroid as lr
from time import time
from langroid.utils.configuration import set_global, Settings
from fire import Fire

DocChatAgentConfig = lr.agent.special.DocChatAgentConfig
DocChatAgent = lr.agent.special.DocChatAgent
ParsingConfig = lr.parsing.parser.ParsingConfig
QdrantDBConfig = lr.vector_store.QdrantDBConfig
Document = lr.mytypes.Document
ChatDocument = lr.agent.chat_document.ChatDocument
DocMetaData = lr.mytypes.DocMetaData

set_global(Settings(cache=False, debug=False))


def main(
        path="examples/docqa/employment.txt",
        #query= "What are the provisions following cessation of employment?",
        query="What must an employee do when their role changes?",
        k=1,
):
    # configure agent

    # read text from path
    with open(path, "r") as f:
        text = f.read()
    docs = [Document(content=text, metadata=DocMetaData(source="user"))]

    agent_cfg = DocChatAgentConfig(
        n_neighbor_chunks=k,
        vecdb=QdrantDBConfig(
            collection_name="testing",
            replace_collection=True,
        ),
        parsing=ParsingConfig(
            splitter=lr.parsing.parser.Splitter.TOKENS,
            chunk_size=100, # roughly matches LangChain child splitter with 400 chars
            overlap=25,
            n_neighbor_ids=5,
            n_similar_docs=3,
        )
    )

    agent = DocChatAgent(agent_cfg)
    agent.ingest_docs(docs)


    # clear history and usage
    agent.clear_history(0)
    agent.llm.reset_usage_cost()

    start = time()

    chunks = agent.get_relevant_chunks(query)
    end = time()
    content = "\n".join([c.content for c in chunks])
    n_words = len(content.split(" "))
    tot_words = len(text.split(" "))

    print(f"Retrieved chunks: {n_words} words out of {tot_words}")


    extracts = agent.get_verbatim_extracts(query, chunks)
    answer = agent.get_summary_answer(query, extracts)
    print(f"Answer: {answer}\n")

    print(f"Time (secs): {end - start}")
    print(str(lr.language_models.base.LanguageModel.usage_cost_summary()))

if __name__ == "__main__":
    Fire(main)

