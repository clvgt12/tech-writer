import os
import yaml
import streamlit as st
import logging
import ollama

# Initialize an application logging service
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Configure basic logging

def load_config(filepath_list: list[str]) -> dict:
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
    logger.info(f"load_config(): OLLAMA_HOST={config['host']}")
    logger.info(f"load_config(): MODEL_NAME={config['model']}")
    return config

def check_ollama_status():
    """
    Checks the status of the Ollama service by issuing an ollama ps status API call.
    Displays a status message in the Streamlit interface based on the response.
    :return Bool (to control streamlit objects)
    """
    status = True
    try:
        response = ollama.ps()
        st.markdown(f'<div style="background-color:green;color:white;padding:0.5rem;">Ollama is available.</div>', unsafe_allow_html=True)
        status = False
        return status
    except ollama.ResponseError as e:
        st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
        logger.error(f"check_ollama_status(): {e}")
        return status
    except Exception as e:
        st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
        logger.error(f"check_ollama_status(): {e}")
        return status

def check_model_status(model: str) -> str:
    """
    Checks the availability of the requested model on the Ollama server.
    If the requested model is available on the server, then return the same
    If it is not available, return the first model name on the list, and use that one for the session
    :param model: string containing requested model name
    :return: string: the model name to be used for this session
    """
    try:
        response: ollama.ListResponse = ollama.list()
        model_names = [m.model for m in response.models]  # Extract model names
        logger.info(f"check_model_status(): Available model(s): {model_names}")
        if model not in model_names:
            if model_names:  # Check if the list is not empty
                logger.warning(f"check_model_status(): User specified model {model} not available")
                logger.warning(f"check_model_status(): Using {model_names[0]} for this session")
                model = model_names[0]
        return model
    except ollama.ResponseError as e:
        logger.error(f"check_model_status(): Error from Ollama: {e}")
        return model
    except Exception as e:
        logger.error(f"check_model_status(): An unexpected error occurred: {e}")
        return model

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
            p = part['message']['content'] # Access content from part
            if p and p != "":  
                accumulated_text += p
                output_placeholder.markdown(accumulated_text)
    except ollama.ResponseError as e:
        st.error(f"query_ollama(): {e}")
    except Exception as e:
        st.error(f"query_ollama(): {e}")

def front_end(config: dict) -> None:
    """
    Sets up the Streamlit front-end interface, allowing users to input text for processing
    by the Ollama model and displays the results.
    :param config: Dictionary containing configuration, including 'model' and 'system'.
    :return: None (enters event loop).
    """
    ollama_logo_url = os.getenv('OLLAMA_LOGO_URL', 'https://ollama.com/public/ollama.png')
    st.image(ollama_logo_url, width=56)
    st.title('Grammar and Spelling Correction')

    # Check and display the Ollama service status
    ollama_disabled_state = check_ollama_status()
    if not ollama_disabled_state:  # If ollama_disabled_state is False, then check model
        config['model'] = check_model_status(config['model'])

    st.markdown('<style>div.row-widget.stTextArea { padding-top: 0.5rem; }</style>', unsafe_allow_html=True)
    text = st.text_area("Enter text to check:", height=150, disabled=ollama_disabled_state)
    if st.button('Check Syntax', disabled=ollama_disabled_state):
        st.markdown('<style>h2 { font-size: 1.2rem; }</style>', unsafe_allow_html=True)
        if text:
            query_ollama(config, text, st)
        else:
            st.error("Please enter some text to check.")

if __name__ == "__main__":
    config = load_config(['/etc/tech-writer/prompts.yaml', './prompts.yaml'])
    if config is None:
        logger.error('main(): Can not locate prompts.yaml config file')
        exit()  # Corrected exit call
    front_end(config)