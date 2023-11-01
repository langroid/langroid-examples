This folder contains various example scripts and text files for RAG, a.k.a 
document-chat.

## Example text files

These files are meant to test relevance-extraction using an LLM.

- `giraffes.txt`: has statements about giraffes interspersed among other 
  random statements. The idea is to use an LLM to retrieve sentences 
  relevant to the query `What do we know about giraffes?`. Try this with 
  the `extract-langroid.py` and `extract-langchain.py` scripts.
- `biden-ai.txt` contains 4 blocks of entirely made-up (by GPT4) 
  sentences of various types: President Biden, AI Regulation, What 
  President Biden said about AI regulation, and Gov regulation in general. 
  The idea is to use an LLM to retrieve sentences relevant to the query, 
  `What did President Biden say about AI Regulation?`. Use the above two 
  scripts to try this out.
- `lease.txt` is a commercial lease document. This is meant to be used with 
  the `chat_multi_extract.py` script, to extract structured lease info 
  using a 2-agent system. 

