# Text Summarizer:
Text summarizer using Ollama's llama3.2:1b model.
Note: Due to system resource constraint the mentioned model is in use, however please do change the model name in .env file and dockerfile according to your usage.

# Requirements:
1.Ollama should be installed and up and running.
2.specified model should be downloaded using ollama pull.

# Running Locally
```
Create virtual env : python -m venv venv

Activate venv: venv/Source/activate

Install requirements: pip install -r requirements.txt

Run Uvicorn: uvicorn app:app --host 0.0.0.0 --port 8080 --reload 

```


# Build Docker container:
```
docker build -f DockerFile -t llama3-summary .
```
# Run the Docker container:
```
docker run --name my_fastapi_container -p 8080:8080 llama3-summary
```

# Inspect the health status of the container
```
docker inspect --format='{{json .State.Health}}' my_fastapi_container
```

Once the docker is built and is running, hit the postman API/use fastapi swagger api docs interface to test, using the following endpoints.

# API Endpoints:
1. GET '/health' - to check the container's health.
2. POST '/summarize' - Summarize the summary of the given transcript or user input, this folllows stuff methodology.
3.POST '/recursive_summarize' - Summarize the summary of the given transcript or user input of high length(>5k,as an example considered this number), this folllows map reduce methodology.
```
Example payload:
    {
     'text': '<user-input>',
     'max_tokens': 150,
     'temperature': 0.7,
     'presence_penalty': 0.5
   }
```
