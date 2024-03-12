# 
# Create a Streamlit front end to Ollama 
# to implement a simple spelling and grammar check use case
# Use a customized Llama2 model with a specialized system prompt to
# support this use case.   That model is called 'tech-writer'
#
# requirements:  requests, streamlit
#
# invoke this application as:  streamlit run tech-writer.py
#

import os
import json
import requests
import time
import streamlit as st
from   streamlit.logger import get_logger

# Initialize an application logging service

logger = get_logger(__name__)

# Define global variables
ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://host.docker.internal:11434')
ollama_logo_url = os.getenv('OLLAMA_LOGO_URL', 'https://ollama.com/public/ollama.png')
ollama_model = os.getenv('OLLAMA_MODEL', 'tech-writer:latest')

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
    return llm.invoke(prompt)

def front_end():
    """
    Sets up the Streamlit front-end interface, allowing users to input text for processing
    by the Ollama model and displays the results.
    """

    st.image(ollama_logo_url, width=56)
    st.title('Grammar and Spelling Correction')

    text = st.text_area("Enter text to check:", height=150)
    if st.button('Check Syntax'):
        if text:
            output_placeholder = st.empty()
            accumulated_text = ""
            for part in query_ollama(text):
                if part:
                    time.sleep(0.1)
                    accumulated_text += part
                    output_placeholder.markdown(accumulated_text)
                else:
                    st.error("Failed to get a response from Ollama")
        else:
            st.error("Please enter some text to check.")

if __name__ == "__main__":
    front_end()
