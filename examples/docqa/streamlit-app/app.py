from langroid.utils.configuration import settings
from utils import configure, agent
import tempfile

import streamlit as st
import os

settings.cache_type = "fakeredis"

st.header('DocChatAgent by Langroid', divider='rainbow')

uploadedFile = st.file_uploader('Choose a txt file')

if uploadedFile is not None:

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = os.path.join(temp_dir.name,uploadedFile.name)
    with open(temp_path,"wb") as f:
         f.write(uploadedFile.getbuffer())

    cfg = configure(temp_path)
    
prompt = st.chat_input("Talk with Document")
if prompt:
    st.write(f"{prompt}")

    #chat using docchatagent
    answer = agent(cfg, prompt)
    st.write(f"{answer}")