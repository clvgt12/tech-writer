# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Specify the Ollama server location to be the host by default
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run tech-writer.py when the container launches
CMD ["streamlit", "run", "tech-writer.py", "--server.address=0.0.0.0"]
