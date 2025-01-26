import requests

'''
This class provides integration with the LLM API for generating responses to user prompts.
The generate_reasoned_response method generates a response using the deepseek-r1 model, which is optimized for reasoned responses.
The generate_simple_response method generates a response using the llama3.2 model, which is optimized for simple responses.

The LLMIntegration class takes an optional api_url parameter that specifies the URL of the LLM API.
If no URL is provided, the default URL http://localhost:11434/api/generate is used.

To use this class, create an instance of the LLMIntegration class and call the generate_reasoned_response or generate_simple_response method with a prompt as the argument.
The method will return the generated response as a string.

Example usage:
llm_integration = LLMIntegration()
response = llm_integration.generate_reasoned_response("What is the capital of France?")
print(response)

response = llm_integration.generate_simple_response("What is the capital of France?")
print(response)
'''

# Define the LLMIntegration class
class LLMIntegration:
    def __init__(self, api_url="http://localhost:11434/api/generate"):          # Initialize the LLMIntegration class with the API URL
        self.api_url = api_url                                                  # Set the API URL

    def generate_reasoned_response(self, prompt):                               # Generate a reasoned response using the deepseek-r1 model
        # Set the request headers and data
        headers = {
            "Content-Type": "application/json"                                  # Set the content type to JSON
        }
        data = {
            "model": "deepseek-r1:1.5b",                                        # Set the model to deepseek-r1:1.5b
            "prompt": prompt,                                                   # Set the prompt to the user input
            "stream": False                                                     # Set the stream flag to False
        }
        # Send a POST request to the LLM API
        try:
            response = requests.post(self.api_url, json=data)                   # Send a POST request to the LLM API
            if response.status_code == 200:                                     # Check if the response status code is 200 (OK)
                return response.json().get("response", "")                      # Return the response from the API
            else:                                                               # If the response status code is not 200
                return "Error: Unable to generate response"                     # Return an error message
        except requests.exceptions.RequestException as e:                       # Handle request exceptions
            return f"Error: {e}"                                                # Return an error message with the exception
    
    # Generate a simple response using the llama3.2 model
    def generate_simple_response(self, prompt):
        # Set the request headers and data
        headers = {
            "Content-Type": "application/json"                                  # Set the content type to JSON
        }
        data = {
            "model": "llama3.2:1B",                                             # Set the model to llama3.2:1B
            "prompt": prompt,                                                   # Set the prompt to the user input
            "stream": False                                                     # Set the stream flag to False
        }
        # Send a POST request to the LLM API
        try:
            response = requests.post(self.api_url, json=data)                   # Send a POST request to the LLM API
            if response.status_code == 200:                                     # Check if the response status code is 200 (OK)
                return response.json().get("response", "")                      # Return the response from the API
            else:                                                               # If the response status code is not 200
                return "Error: Unable to generate response"                     # Return an error message
        except requests.exceptions.RequestException as e:                       # Handle request exceptions
            return f"Error: {e}"                                                # Return an error message with the exception