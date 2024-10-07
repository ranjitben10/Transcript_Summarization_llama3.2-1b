import asyncio,ollama
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import ValidationError
import httpx
from Entity import TextRequest,Meta,ResponseModel
from Utility import load_model, check_memory_usage, check_cpu_usage, recursive_summary_for_chunks, direct_summary
from TextSplitter import RecursiveTextSplitter

# Load environment variables from .env file
load_dotenv(override=True)

# Access the environment variables
model = os.getenv('MODEL_NAME')
system_prompt = os.getenv('SYSTEM_PROMPT')
prompt_ = os.getenv('PROMPT')
recursive_system_prompt = os.getenv('RECURSIVE_SYSTEM_PROMPT')

#pull the model
ollama.pull(model)

#create fastai object
app = FastAPI()

#to check the summerize url health/status
async def check_external_service(request: Request, client: httpx.AsyncClient):
    """
    Check the availability of the /summarize endpoint.
    """
    url = str(request.url_for("summarize"))  # Dynamically get the URL for /summarize    
    payload = {
        "text": "Romantic love often captures the most attention, filled with intense emotions and an undeniable chemistry. It inspires art, literature, and music, reflecting humanity's quest to understand and express this powerful feeling. Conversely, familial love provides a sense of belonging and support, forming the foundation of our earliest relationships and shaping our values. Platonic love, characterized by deep friendships, highlights the importance of companionship and shared experiences.",
        "max_tokens": 40,
        "temperature": 0.7,
        "presence_penalty": 0.6
    }
    try:
        print('Requesting URL...')
        response = await client.post(url, json=payload, timeout=460)  # Match timeout
        print(f"Response status: {response.status_code}")
        response.raise_for_status()  # Raise error for bad HTTP responses
        response_data = response.json()
        
        if 'summary' in response_data and response_data['summary']:
            return True
        return False
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return False
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

#/health endpoint to check the health of /summary endpoint and load model into memory and collect cpu and memory usage
@app.get("/health")
async def health(request: Request):
    """
    Check the health status of the application.Load model into memory for 20mins.Collects hardware status.
    """

    #load model into memory
    res = await load_model()
    print('model loaded:',res)

    async with httpx.AsyncClient() as client:
        # Check external service
        external_service_status = await check_external_service(request, client)
        print('External service status:', external_service_status)

    # Check resource usage
    memory_usage, cpu_usage = await asyncio.gather(check_memory_usage(), check_cpu_usage())
    print('Data gathered...')

    # Compile health results
    health_results = {
        "model_status": res,
        "external_service_status": external_service_status,
        "memory_usage": memory_usage,
        "cpu_usage": cpu_usage,
    }

    # Determine overall health
    if not external_service_status:
        return {"status": "unhealthy", "details": health_results}, 503

    return {"status": "healthy", "details": health_results}, 200

# Main /summarize API function for short text
@app.post("/summarize")
async def summarize(text_request: TextRequest):
    """
    To summerize the text directly,follows stuff methodology.
    """
    try:
        text = text_request.text
        penalty = text_request.presence_penalty
        max_token = text_request.max_tokens
        temperature = text_request.temperature
        # prompt_=text
        # Directly summarize the short text
        final_summary,tokens_used = await direct_summary(text, model, temperature, max_token, penalty,system_prompt,prompt_)

        # Return the result
        result = ResponseModel(
            summary=final_summary,
            meta=Meta(model=model, total_tokens=tokens_used)
        )
        return result
    except ValidationError as e:
        return {"error": str(e)}, 422
    except Exception as e:
        return {"error": str(e)}, 500

# New /recursive_summarize API function for larger texts
@app.post("/recursive_summarize")
async def recursive_summarize(text_request: TextRequest):
    """
    To summerize large text length > 5000 , follows map reduce methodology...
    """
    try:
        text = text_request.text
        penalty = text_request.presence_penalty
        max_token = text_request.max_tokens
        temperature = text_request.temperature
        # prompt_=text
        # If text length is greater than 5000 characters, split into chunks
        if len(text) > 5000:
            splitter = RecursiveTextSplitter(chunk_size=1000, chunk_overlap=250)
            text_chunks = splitter.split_text(text)
            reduced_max_token = 170

            # Get summaries for each chunk
            chunk_summaries = await recursive_summary_for_chunks(
                text_chunks, model, temperature, reduced_max_token, penalty,recursive_system_prompt,prompt_
            )

            # Combine chunk summaries into one summary
            combined_summary = " ".join(chunk_summaries)

            # Perform a final summarization of the combined summary using full max_token
            final_summary,tokens_used = await direct_summary(combined_summary, model, temperature, max_token, penalty, system_prompt,prompt_)

            # Return the result
            result = ResponseModel(
            summary=final_summary,
            meta=Meta(model=model, total_tokens=tokens_used)
            )
            return result
        else:
            return {"error": "Text length is less than 5000 characters. Use /summarize for short texts."}, 400

    except ValidationError as e:
        return {"error": str(e)}, 422
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
