# tech-writer
#
# @Author: clvgt12
# @URL:  https://github.com/clvgt12/tech-writer
# @License: MIT
#
# Implement a simple spelling and grammar check use case
# Use a customized Llama2 model with a specialized system prompt.   
# That model is called 'tech-writer'
#
# LLM requirements:  install Ollama with tech-writer LLM created
# pip requirements:  requests, streamlit
#
# invoke this application as:  streamlit run tech-writer.py

import os
import json
import requests
import time
import streamlit as st
from   streamlit.logger import get_logger

# Initialize an application logging service

logger = get_logger(__name__)

# Define global variables
ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
ollama_logo_url = os.getenv('OLLAMA_LOGO_URL', 'https://ollama.com/public/ollama.png')
ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')

class ChatOllama:
    """
    Represents a client for interacting with the Ollama service for language model operations.
    """
    
    def __init__(self, base_url=ollama_base_url, model=ollama_model):
        """
        Initializes the ChatOllama client with the base URL and model name.
        :param base_url: URL of the Ollama API endpoint.
        :param model: Name of the model to use for requests.
        """
        self.base_url = base_url
        self.model = model

    def invoke(self, prompt):
        """
        Invokes the Ollama model with a given prompt for generating a response.
        Enables streaming for real-time processing of the model's output.
        :param prompt: Text prompt to send to the model.
        :return: Yields responses from the model as they are received.
        """
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        try:
            response = requests.post(url, json=data, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        json_line = json.loads(line.decode('utf-8'))
                        if json_line.get("done") is not False:
                            break
                        yield json_line.get("response")
            else:
                logger.error(f"Ollama API call failed with status code {response.status_code}")
                yield None
        except Exception as e:
            logger.error(f"Failed to call Ollama API: {e}")
            yield None

def query_ollama(prompt):
    """
    Sends a prompt to the Ollama container and retrieves the streamed response.
    :param prompt: Text prompt to be corrected or processed by the model.
    :return: Streamed responses from the model or an error message.
    """
    llm = ChatOllama()
    system_prompt = """You are an advanced model trained to identify and correct English language spelling and grammar errors while enhancing the clarity and conciseness of professional communication. Please review the text provided below, determine if there are spelling and/or grammar errors, correct them if you find them, revise the content for clarity and conciseness without altering the original meaning.  Respond back to this prompt with two sections.  The first section shall shall be titled Revised Text:, and contain your revised text.  The second section shall be titled Corrections:, and contain an bulletized list highlighting the spelling and grammar corrections you made. If you cannot make corrections to the provided text, just say the provided text is correct. Finally, please emit your response in markdown format so it can be streamed inside a web application. From a styling perspective, when you generate the section headers, use level two markup, e.g., ## Revised Text:, ## Corrections:. """
    full_prompt = f"{system_prompt}\n\n{prompt}"  # Combine system and user prompts
    return llm.invoke(full_prompt)

def check_ollama_status():
    """
    Checks the status of the Ollama service by making a GET request to the base endpoint.
    Displays a status message in the Streamlit interface based on the response.
    """
    try:
        response = requests.get(ollama_base_url)
        if response.status_code == 200:
            st.markdown(f'<div style="background-color:green;color:white;padding:0.5rem;">{response.text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
    except requests.exceptions.RequestException as e:
        st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
        logger.error(f"Failed to connect to Ollama API: {e}")

def front_end():
    """
    Sets up the Streamlit front-end interface, allowing users to input text for processing
    by the Ollama model and displays the results.
    """

    st.image(ollama_logo_url, width=56)
    st.title('Grammar and Spelling Correction')

    # Check and display the Ollama service status
    check_ollama_status()

    st.markdown('<style>div.row-widget.stTextArea { padding-top: 0.5rem; }</style>', unsafe_allow_html=True)
    text = st.text_area("Enter text to check:", height=150)
    if st.button('Check Syntax'):
        st.markdown('<style>h2 { font-size: 1.2rem; }</style>', unsafe_allow_html=True)
        if text:
            output_placeholder = st.empty()
            accumulated_text = ""
            for part in query_ollama(text):
                if part:
                    accumulated_text += part
                    output_placeholder.markdown(accumulated_text)
                else:
                    st.error("Failed to get a response from Ollama")
        else:
            st.error("Please enter some text to check.")

if __name__ == "__main__":
    front_end()
