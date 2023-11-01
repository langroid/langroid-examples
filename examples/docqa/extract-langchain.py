'''
Extract relevant portions of document(s), using LangChain's
LLMChainExtractor.acompress_documents() method.

Ensure you have OPENAI_API_KEY=... set in your .env file in project root.

PRE-REQUISITE: install langchain in your virtual environment.

Run like this, from project root:
$ python3 examples/docqa/extract-langchain.py

Optional arguments:
    --path=... : path to text file to extract from (default is examples/docqa/giraffes.txt)
    --query="..." : query to run (default is "What do we know about giraffes?")
    --split=False: whether to split the text into paragraphs (default is False)
'''

from dotenv import load_dotenv
import asyncio
from time import time
from langchain.chat_models import ChatOpenAI
from langchain.schema.document import Document
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.callbacks import get_openai_callback
from fire import Fire


load_dotenv()

def main(path="examples/docqa/giraffes.txt", query="What do we know about giraffes?", split=False):
    with open(path, "r") as f:
        text = f.read()
    texts = text.split("\n\n")
    if split:
        texts = [
            Document(page_content=t) for t in texts
        ]
    else:
        texts = [Document(page_content=text)]


    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    extractor = LLMChainExtractor.from_llm(llm)

    start = time()

    with get_openai_callback() as cb:
        compressed_docs = asyncio.run(extractor.acompress_documents(texts, query, [cb]))

    end = time()

    print(cb)

    print(f"Time (secs): {end - start}")

    content = "\n".join(d.page_content for d in compressed_docs)
    print("Extracted content:")
    print(content)
    
    n_sentences = len(content.split("."))
    tot_sentences = len(text.split("."))
    print(f"Extracted {n_sentences} sentences out of {tot_sentences}")

if __name__ == "__main__":
    Fire(main)
