# Tech Writer App

![](./images/tech-writer-header-image-dalle3.jpg "Source: Dall-E 3: Image of a AI robot, typing at a computer, presumably writing a blog post article, and wanting an application to help it write more clearly, concisely and effectively")

## Introduction
This application provides a simple interface for checking grammar and spelling in text inputs. It leverages a open source large language model for processing and correcting text, making it ideal for professionals seeking to enhance their written communication while retaining privacy and ownership of their created content.

The Tech Writer communicates with [Ollama](https://ollama.ai), an open source LLM inference server that provides a standardized API interface for various open source models.

## Use Case
The app is designed to correct spelling and grammar errors, improve clarity, and enhance the conciseness of professional communication. It's particularly useful for writers, editors, content creators, and anyone who values precision in written English.

## Installation Instructions
### Prerequisites
#### Ollama
1. Install [Ollama](https://ollama.ai) on your host PC
2. Pull the default LLM `ollama pull llama3.2:1b` (you can use other models; change the name in the `prompts.yaml` file)
### Python Base Installation
#### Windows
- Download and install Python from [python.org](https://www.python.org/downloads/windows/).
#### Linux/MacOS
- Python is typically pre-installed on Linux and macOS. If not, install Python using your distribution's package manager (Linux) or download from [python.org](https://www.python.org/downloads/macos/) (macOS).
### Python Library Module Installation
```
$ pip3 install -r requirements.txt
```
## Running the Application
#### Windows, Linux and MacOS
From the command line, run:
```
$ streamlit run tech-writer.py
```
## Usage
After launching the application, simply enter the text you wish to check in the provided text area and click "Check Syntax." 
