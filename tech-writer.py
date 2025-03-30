import os
import time
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
                    logging.info(f"load_yaml_file(): Loaded prompts file '{filename}'")
            except FileNotFoundError:
                logging.warning(f"load_yaml_file(): Prompts file '{filename}' does not exist")
            except yaml.YAMLError as e:
                logging.error(f"load_yaml_file(): YAML error in '{filename}': {e}")
            except Exception as e:
                logging.error(f"load_yaml_file(): Unexpected error: {e}")
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

def set_ollama_status_banner(st: object, ollama_disabled_state: bool) -> None:
    """
    Displays correct banner based on ollama_disabled_state
    Parameters:
        st: obj: The streamlit object
        ollama_disabled_state: bool: True if ollama is NOT available, False if it is
    Returns:
        None
    """
    if ollama_disabled_state:
        st.markdown('<div style="background-color:red;color:white;padding:0.5rem;">Ollama is unavailable.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:green;color:white;padding:0.5rem;">Ollama is available.</div>', unsafe_allow_html=True)


def check_ollama_status() -> bool:
    """
    Checks the status of the Ollama service by issuing an ollama ps status API call.
    :return: bool (to control streamlit objects)
    """
    status = True
    try:
        response = ollama.ps()
        status = False
        return status
    except ollama.ResponseError as e:
        logger.error(f"check_ollama_status(): {e}")
        return status
    except Exception as e:
        logger.error(f"check_ollama_status(): {e}")
        return status

def check_model_status(model: str) -> str:
    """
    Slogan: Check and update the model based on availability from the Ollama server.
    
    Parameters:
        model (str): The user-requested model name.
        
    Returns:
        str: The model name to be used for the session, or an empty string if no model is available.
    """
    try:
        response: ListResponse = ollama.list()
        # logger.info(f"check_model_status(): Full response from Ollama: {response}")
    except ollama.ResponseError as e:
        logger.error(f"check_model_status(): Error from Ollama: {e}")
        return None
    except Exception as e:
        logger.error(f"check_model_status(): An unexpected error occurred: {e}")
        return None
        
    # Ensure the response contains the 'models' key.
    if 'models' not in response:
        logger.error("check_model_status(): 'models' key not found in response")
        return None
    
    # Process each model entry, handling both dicts and Model objects
    model_list = response.get('models', [])
    model_names = []
    for m in model_list:
        model_name = None
        if isinstance(m, dict):
            # Prefer the 'model' key, but fallback to 'name'
            model_name = m.get('model') or m.get('name')
        elif hasattr(m, 'model'):
            model_name = m.model
        if model_name:
            model_names.append(model_name)

    logger.info(f"check_model_status(): Available model(s): {model_names}")

    if model_names:
        if model not in model_names:
            logger.warning(f"check_model_status(): User specified model {model} not available")
            model = model_names[0]
    else:
        logger.error("check_model_status(): No model is available on Ollama server")
        return None   # Return None if no models are available.
    logger.info(f"check_model_status(): Using {model} for this session")
    return model

def query_ollama(config: dict, prompt: str, st: object) -> None:
    """
    Sends a prompt to the Ollama container and retrieves the streamed response,
    calculating tokens per second.
    :param config: Dictionary containing configuration, including 'model' and 'system'.
    :param prompt: Text prompt to be corrected or processed by the model.
    :param st: Streamlit object for displaying output.
    :return: None (displays streamed responses in Streamlit).
    """
    messages = [
        {"role": "system", "content": config['system']},
        {"role": "user", "content": prompt},
    ]
    output_placeholder = st.empty()
    accumulated_text = ""
    token_count = 0
    start_time = time.time()
    logger.info(f"query_ollama(): starting inference with model {config['model']}...")
    try:
        for part in ollama.chat(model=config['model'], messages=messages, stream=True):
            if token_count == 0:
                gpu_decode_time = time.time() - start_time
                if gpu_decode_time > 0:
                    logger.info(f"query_ollama(): GPU Decode Time = {gpu_decode_time:.2f} seconds")
                else:
                    logger.warning("query_ollama(): GPU Decode Time is zero.")
            p = part['message']['content']
            if p and p != "":
                accumulated_text += p
                output_placeholder.markdown(accumulated_text)
                token_count += 1  # Increment token count
        elapsed_time = time.time() - start_time
        if token_count > 0:
            time_per_output_token = elapsed_time / token_count
            logger.info(f"query_ollama(): Time Per Output Token (TPOT) = {time_per_output_token:.4f}")
        else
            logger.warning("query_ollama(): Token Count is zero.")
    except ollama.ResponseError as e:
        logger.error(f"query_ollama(): {e}")
    except Exception as e:
        logger.error(f"query_ollama(): {e}")

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
    st_error_msg = ""
    ollama_disabled_state = check_ollama_status()
    if not ollama_disabled_state:  # If ollama_disabled_state is False, then check model
        config['model'] = check_model_status(config['model'])
        if config['model'] is None or config['model'] == "":
            ollama_disabled_state = True
            st_error_msg = "There is no available model on Ollama server"
    else:
        st_error_msg = "The Ollama server is not reachable"

    set_ollama_status_banner(st, ollama_disabled_state)
    if st_error_msg != "":
        st.error(st_error_msg)

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
