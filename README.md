# Tech Writer App

![](./images/tech-writer-header-image-dalle3.jpg "Source: Dall-E 3: Image of a AI robot, typing at a computer, presumably writing a blog post article, and wanting an application to help it write more clearly, concisely and effectively")

## Introduction
This application provides a simple interface for checking grammar and spelling in text inputs. It leverages a open source large language model for processing and correcting text, making it ideal for professionals seeking to enhance their written communication while retaining privacy and ownership of their created content.

The Tech Writer communicates with [Ollama](https://ollama.ai), an open source LLM runtime environment that provides a standardized API interface for various open source models.

## Use Case
The app is designed to correct spelling and grammar errors, improve clarity, and enhance the conciseness of professional communication. It's particularly useful for writers, editors, content creators, and anyone who values precision in written English.

## Installation Instructions
### Prerequisites
- Python 3.8 or later
- Ollama, installed on your host computer
### Python and Required Modules Installation
#### Windows
1. Download and install Python from [python.org](https://www.python.org/downloads/windows/).
2. Install Streamlit and other required modules:
```
$ pip install streamlit requests
```
#### Linux/MacOS
1. Python is typically pre-installed on Linux and macOS. If not, install Python using your distribution's package manager (Linux) or download from [python.org](https://www.python.org/downloads/macos/) (macOS).
2. Install Streamlit and other required modules:
```
$ pip3 install streamlit requests
```
### Ollama Model Setup
**Note:** The following installation instructions assume the use of Ollama that is installed on Windows, MocOS and Linux systems.   

After you install [Ollama](https://github.com/ollama/ollama), proceed with the following instructions.
#### Windows, MacOS and Linux
1. Pull the Google Gemma LLM using Ollama CLI:
```
$ ollama pull model gemma:7b
```
2. Create the `tech-writer` model with your `tech-writer` Modelfile. Place your Modelfile in the directory and run:
```
$ ollama create tech-writer --file tech-writer.Modelfile
```
## Running the Application
#### Windows, Linux and MacOS
From the command line, run:
```
$ streamlit run tech-writer.py
```
## Usage
After launching the application, simply enter the text you wish to check in the provided text area and click "Check Syntax." 

