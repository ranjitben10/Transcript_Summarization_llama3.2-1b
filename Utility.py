import asyncio,psutil,ollama

# Asynchronous function to check memory usage
async def check_memory_usage():
    return await asyncio.to_thread(psutil.virtual_memory)

# Asynchronous function to check CPU usage
async def check_cpu_usage():
    return await asyncio.to_thread(psutil.cpu_percent, interval=1)

#load the model and keep it in memory for next 20min
async def load_model():
    return await asyncio.to_thread(ollama.generate,model="llama3.2:1b",keep_alive='20m')

# Unified function to generate summary
async def generate_summary(text, model, temperature, max_token, penalty,system_prompt,prompt_):
    print("System Prompt",system_prompt)
    print("User Prompt",prompt_.format(text=text))
    response = await asyncio.to_thread(
        ollama.generate,
        model=model,
        system = system_prompt,
        prompt=prompt_.format(text=text),
        stream=False,
        options={
            "temperature": temperature,
            "num_predict":max_token,
            "presence_penalty": penalty,
        }
    )
    if 'response' not in response:
        raise ValueError("Response format is incorrect.")
    print('Response generated',response)
    print("Total Duration:",response['total_duration']/1e9)
    print("Load Duration:",response['load_duration']/1e9)
    return response['response'],int(response['prompt_eval_count'])+int(response['eval_count'])

# Function to summarize shorter text directly
async def direct_summary(text, model, temperature, max_token, penalty,system_prompt,prompt_):
    return await generate_summary(text, model, temperature, max_token, penalty,system_prompt,prompt_)

# Function to recursively summarize text by splitting it into chunks
async def recursive_summary_for_chunks(text_chunks, model, temperature, reduced_max_token, penalty,system_prompt,prompt_):
    summaries = []
    for chunk in text_chunks:
        summary,total_tokens = await generate_summary(chunk, model, temperature, reduced_max_token, penalty, system_prompt,prompt_)
        summaries.append(summary)
    return summaries