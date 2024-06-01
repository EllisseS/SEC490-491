from streamlit_autorefresh import  st_autorefresh
import glob
import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
import os
import pandas as pd
try:
    from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

st.set_page_config(page_title="CyberSec Assistant", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = "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"
st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about the file you chose!" }
    ]

with st.sidebar:
    data_file = st.file_uploader("Upload CSV or TXT", type=["csv", "txt"])

    filename = None
    if data_file is not None:
        file_details = {"filename": data_file.name, "filetype": data_file.type, "filesize": data_file.size}

        if data_file.type == 'text/csv':
            df = pd.read_csv(data_file, encoding="latin1")
        elif data_file.type == 'text/plain':
            df = pd.read_csv(data_file, encoding="latin1", on_bad_lines='skip')  # Assuming TXT file is tab-delimited
        else:
            st.error("Unsupported file format")
            st.stop()

        save_directory = "/app/inspectData"

        # Check if the directory exists, if not, create it
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Define the path to save the file
        save_path = os.path.join(save_directory, data_file.name)

        # Save the DataFrame to CSV
        df.to_csv(save_path, index=False)

        st.success("dData Uploaded to Database Successfully")

    ### ---FILE SELECTOR--- ###
    folder_path='/app/inspectData'
    filenames = os.listdir(folder_path)
    if not filenames:
        st.write("No files currently")
    selected_filename = st.selectbox("Current Files", filenames, key="file_selector")
    filename =  selected_filename
    st.write(filenames)

input_dir = "/app/inspectData"
if not os.listdir(input_dir):
    st.error(f"No available file to examine. Import a File(s) to examine")
    st.stop()

with st.spinner(text="Loading and indexing the files right now – hang tight! This should take 1-2 minutes."):
    reader = SimpleDirectoryReader(input_dir=folder_path)
    docs = reader.load_data()
    service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.15, system_prompt="You are an expert on Cybersecurity Assistant and your job is to examine the files presented to you. Keep your answers technical and based on facts – do not hallucinate features. Never show the full directory path to files you present even if you are asked to. Your answers should always be either in bullet points or numbered. When presented with a question you are unable to answer, just ask them to rephrase the question."))
    index = VectorStoreIndex.from_documents(docs, service_context=service_context)
    #st.write(docs)

if filename:
    if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history

