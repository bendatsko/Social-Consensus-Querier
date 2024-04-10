import os
import json
from llamaapi import LlamaAPI
from dotenv import load_dotenv

load_dotenv()


# Initialize the SDK
llama = LlamaAPI(os.getenv('LLAMA_API_KEY'))

# Build the API request
api_request_json = {
    "messages": [
        {"role": "user", "content": "Please summarize this in one sentence less than 8 words: "},
    ],
    "stream": False,
}

# Execute the Request
response = llama.run(api_request_json)
response_json = response.json()

# Extracting the 'content' from the response
if 'choices' in response_json and len(response_json['choices']) > 0:
    content = response_json['choices'][0].get('message', {}).get('content')
    print("Extracted content:", content)
else:
    print("No content found in the response")