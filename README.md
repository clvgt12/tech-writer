# Tech Writer App
## Introduction
This application provides a simple interface for checking grammar and spelling in text inputs. It leverages the powerful Llama2 open source large language model for processing and correcting text, making it ideal for professionals seeking to enhance their written communication.
## Use Case
The app is designed to correct spelling and grammar errors, improve clarity, and enhance the conciseness of professional communication. It's particularly useful for writers, editors, content creators, and anyone who values precision in written English.
## Installation Instructions
### Prerequisites
- Python 3.8 or later
- Docker (for container-based deployment)
### Python and Required Modules Installation
#### Windows
1. Download and install Python from [python.org](https://www.python.org/downloads/windows/).
2. Install Streamlit and other required modules:
```
pip install streamlit requests
```
#### Linux/MacOS
1. Python is typically pre-installed on Linux and macOS. If not, install Python using your distribution's package manager (Linux) or download from [python.org](https://www.python.org/downloads/macos/) (macOS).
2. Install Streamlit and other required modules:
```
pip3 install streamlit requests
```
### Ollama and Llama2 Model Setup
**Note:** The following installation instructions assume the use of the native Ollama installation on Windows, MocOS and Linux.  Support for the Ollama Docker container is out of scope.
1. Install Ollama following the instructions at [Ollama's Github page](https://github.com/ollama/ollama).
2. Pull the Llama2 model using Ollama CLI:
```
ollama pull model llama2
```
3. Create the `tech-writer` model with your `tech-writer` Modelfile. Place your Modelfile in the directory and run:
```
ollama create tech-writer --file tech-writer.Modelfile
```
## Building the Docker Container
Build your Docker container image with:
```
docker build -t tech-writer-app .
```
## Running the Application as a Docker Container
#### Windows Desktop
Run the tech-writer container from Docker Desktop for Windows.  
1. Click on 'Images'
2. Click on 'tech-writer'
3. Click on 'Run' in the upper right hand corner
4. Select 'Optional Settings' and cick on the down arrow.
5. Enter 8501 for the host port
6. Enter 'tech-writer' for the container name
7. Click on Run
#### Linux / MacOS / Windows Subsystem for Linux (WSL)
From the bash command line, run:
```
docker run -p 8501:8501 tech-writer
```
## Usage
After launching the application, simply enter the text you wish to check in the provided text area and click "Check Syntax." 

