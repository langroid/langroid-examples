'''
Extract relevant portions of document(s), using Langroid's
DocChatAgent.get_verbatim_extracts() method.

Ensure you have followed the install instructions in the README.md file.
Essentially, have a virtual env and do `pip install langroid`.
Ensure you have OPENAI_API_KEY=... set in your .env file in project root.

Run like this, from project root:
$ python3 examples/docqa/extract-langroid.py

Optional arguments:
    --path=... : path to text file to extract from (default is examples/docqa/giraffes.txt)
    --query="..." : query to run (default is "What do we know about giraffes?")
    --split=False: whether to split the text into paragraphs (default is False)

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


def main(path="examples/docqa/giraffes.txt", query="What do we know about giraffes?", split=False):
    # configure agent

    # read text from path
    with open(path, "r") as f:
        text = f.read()
    if split:
        docs = [
            Document(content=t, metadata=DocMetaData(source="user")) for t in text.split("\n\n")
        ]
    else:
        # or pass the entire text as a single document
        docs = [Document(content=text, metadata=DocMetaData(source="user"))]

    agent_cfg = DocChatAgentConfig()

    agent = DocChatAgent(agent_cfg)

    start = time()
    extracts = agent.get_verbatim_extracts(query, docs)
    end = time()
    content = "\n".join([e.content for e in extracts])
    n_sentences = len(content.split("."))
    tot_sentences = len(text.split("."))

    print("Extracted content:")
    print(content)
    print(f"Extracted {n_sentences} sentences out of {tot_sentences}")
    print(f"Time (secs): {end - start}")
    print(str(lr.language_models.base.LanguageModel.usage_cost_summary()))

if __name__ == "__main__":
    Fire(main)

