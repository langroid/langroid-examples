'''
Answer question about a document using LangChain's
Parent Document Retriever, which
embeds small chunks and retrieves "parent" chunks.

Ensure you have OPENAI_API_KEY=... set in your .env file in project root.

PRE-REQUISITE: install langchain in your virtual environment.

Run like this, from project root:
$ python3 examples/docqa/retrieve-context-langchain.py

Optional arguments:
    --path=... : path to text file to extract from (default is examples/docqa/giraffes.txt)
    --query="..." : query to run (default is "What do we know about giraffes?")

Also see this colab:
https://colab.research.google.com/drive/1JvH6CO9AS7CaWK0GTblZGesJoo9Jjyn7

'''

from dotenv import load_dotenv
from time import time
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever

## Text Splitting & Docloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain.document_loaders import TextLoader
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever

from langchain.callbacks import get_openai_callback
from fire import Fire

from langchain.embeddings import HuggingFaceBgeEmbeddings

model_name = "BAAI/bge-large-en-v1.5"
#model_name = "BAAI/bge-small-en-v1.5"
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity

bge_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs=encode_kwargs
)

load_dotenv()

def main(
        path="examples/docqa/employment.txt",
        #query= "What are the provisions following cessation of employment?",
        query="What must an employee do when their role changes?",
):
    loader = TextLoader(path)
    docs = loader.load()

    # This text splitter is used to create the parent documents - The big chunks
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

    # This text splitter is used to create the child documents - The small chunks
    # It should create documents smaller than the parent
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(collection_name="split_parents", embedding_function=bge_embeddings) #OpenAIEmbeddings()

    # The storage layer for the parent documents
    store = InMemoryStore()

    big_chunks_retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    big_chunks_retriever.add_documents(docs)
    n_keys = len(list(store.yield_keys()))
    print(f"Indexed {n_keys} chunks")

    from langchain.chains import RetrievalQA

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")

    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=big_chunks_retriever,
    )
    qa = RetrievalQA.from_chain_type(llm=llm,
                                     chain_type="stuff",
                                     retriever=compression_retriever)
    start = time()
    with get_openai_callback() as cb:
        answer = qa.run(query)
    print(f"Answer: {answer}")
    end = time()

    print(f"Time (secs): {end - start}")
    print(cb)

if __name__ == "__main__":
    Fire(main)
