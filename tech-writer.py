import os
import yaml
import streamlit as st
import logging
import ollama

# Initialize an application logging service
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Configure basic logging

def load_config_file(filepath_list: list[str]) -> dict:
    """
    Slogan: Merges configuration from environment, YAML, and defaults. (order of precedence)
    Parameters:
        filepath_list (List[str]): list of strings indicating location of prompts.yaml file
    Returns:
        dict: Merged configuration with keys: host, model, system prompt.
    """
    def set_defaults() -> dict:
        return {
            "host": "localhost:11434",
            "model": "llama3.2:1b",
            "system": """You are an advanced model trained to identify and correct English language spelling and grammar errors while enhancing the clarity and conciseness of professional communication. Please review the text provided below, determine if there are spelling and/or grammar errors, correct them if you find them, revise the content for clarity and conciseness without altering the original meaning.  Respond back to this prompt with two sections.  The first section shall shall be titled Revised Text:, and contain your revised text.  The second section shall be titled Corrections:, and contain an bulletized list highlighting the spelling and grammar corrections you made. If you cannot make corrections to the provided text, just say the provided text is correct. Finally, please emit your response in markdown format so it can be streamed inside a web application. From a styling perspective, when you generate the section headers, use level two markup, e.g., ## Revised Text:, ## Corrections:. 
            """,
        }

    def load_yaml_file(config: dict, filepath_list: list[str]) -> dict:
        # Attempt to load YAML configuration if a file is specified or if "prompts.yaml" exists.
        yaml_config = {}
        while filepath_list:  # Use a while loop to iterate through the list
            filename = filepath_list.pop(0)  # pop from the beginning to check in order.
            try:
                with open(filename, "r") as f:
                    yaml_config = yaml.safe_load(f) or {}
            except FileNotFoundError:
                logging.warning(f"[WARNING merge_config()]: Could not load prompts file '{filename}'")
            except yaml.YAMLError as e:
                logging.error(f"[ERROR merge_config()]: YAML error in '{filename}': {e}")
            except Exception as e:
                logging.error(f"[ERROR merge_config()]: Unexpected error loading '{filename}': {e}")
        # Extract values from YAML file (if available)
        config['host'] = yaml_config.get("host", config['host'])
        config['model'] = yaml_config.get("model", config['model'])
        #Extract the system prompt.
        if yaml_config.get("messages") and isinstance(yaml_config["messages"], list) and len(yaml_config["messages"]) > 0 and yaml_config["messages"][0].get("role") == "system" and yaml_config["messages"][0].get("content"):
            config['system'] = yaml_config["messages"][0]["content"]
        else:
            config['system'] = config['system'] #Keep default if not found.
        return config

    def load_env(config: dict) -> dict:
        # Environment variables
        config['host'] = os.getenv("OLLAMA_HOST", config['host'])
        config['model'] = os.getenv("MODEL_NAME", config['model'])
        return config

    # Merge using precedence: environment > YAML > defaults.
    config = set_defaults()
    config = load_yaml_file(config, filepath_list)
    config = load_env(config)
    return config

def check_ollama_status():
    """
    Checks the status of the Ollama service by issuing an ollama ps status API call.
    Displays a status message in the Streamlit interface based on the response.
    """
    try:
        response = ollama.ps()
        st.markdown(f'<div style="background-color:green;color:white;padding:0.5rem;">Ollama is available.</div>', unsafe_allow_html=True)
    except ollama.ResponseError as e:
        st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
        logger.error(f"Failed to connect to Ollama server: {e}")
    except Exception as e:
        st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
        logger.error(f"Failed to check Ollama status: {e}")

def query_ollama(config: dict, prompt: str, st: object):
    """
    Sends a prompt to the Ollama container and retrieves the streamed response.
    :param config: Dictionary containing configuration, including 'model' and 'system'.
    :param prompt: Text prompt to be corrected or processed by the model.
    :param st: Streamlit object for displaying output.
    :return: None (displays streamed responses in Streamlit).
    """
    messages = [  # messages should be a list of dictionaries
        {"role": "system", "content": config['system']},
        {"role": "user", "content": prompt},
    ]
    output_placeholder = st.empty()
    accumulated_text = ""
    try:
        for part in ollama.chat(model=config['model'], messages=messages, stream=True):
            if part['message']['content']:  # Access content from part
                accumulated_text += part['message']['content']
                output_placeholder.markdown(accumulated_text)
            else:
                st.warning("Ollama returned an empty content part.")  # Use warning instead of error for partial responses
    except ollama.ResponseError as e:
        st.error(f"Error from Ollama: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

def front_end():
    """
    Sets up the Streamlit front-end interface, allowing users to input text for processing
    by the Ollama model and displays the results.
    """
    ollama_logo_url = os.getenv('OLLAMA_LOGO_URL', 'https://ollama.com/public/ollama.png')
    st.image(ollama_logo_url, width=56)
    st.title('Grammar and Spelling Correction')

    # Check and display the Ollama service status
    check_ollama_status()

    st.markdown('<style>div.row-widget.stTextArea { padding-top: 0.5rem; }</style>', unsafe_allow_html=True)
    text = st.text_area("Enter text to check:", height=150)
    if st.button('Check Syntax'):
        st.markdown('<style>h2 { font-size: 1.2rem; }</style>', unsafe_allow_html=True)
        if text:
            query_ollama(config, text, st)
        else:
            st.error("Please enter some text to check.")

if __name__ == "__main__":
    config = load_config_file(['/etc/tech-writer/prompts.yaml', './prompts.yaml'])
    if config is None:
        logger.error('Can not locate prompts.yaml config file')
        exit()  # Corrected exit call
    front_end()