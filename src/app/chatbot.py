from flask import Flask, request, jsonify
from flask_cors import CORS
from ChatBot.src.app.llm_integration import LLMIntegration

'''
This is the main file for the ChatBot application. It creates a Flask app that listens for POST requests to the /chat endpoint.
When a request is received, the app extracts the user input from the request, generates a response using the LLMIntegration class,
and returns the response in the JSON format.

The ChatBot class defines the logic for processing user input and generating responses. It uses the LLMIntegration class to interact
with the LLM API and generate responses. The preprocess_input method is used to clean and normalize the user input before passing it to the LLM model.
The get_reasoned_response method generates a response using the deepseek-r1 model, which is optimized for reasoned responses.
The get_simple_response method generates a response using the llama3.2 model, which is optimized for simple responses.

The app routes POST requests to the /chat endpoint to the chat function, which extracts the user input from the request, generates a response
using the get_simple_response method, and returns the response in the JSON format.

To run the application, use the command `python chatbot.py` in the terminal.
'''

app = Flask(__name__)       # Create a Flask app
CORS(app)                   # Enable Cross-Origin Resource Sharing (CORS)

# Define the Chatbot class
class Chatbot:
    # Initialize the Chatbot with the LLMIntegration class
    def __init__(self, api_url):
        self.llm_integration = LLMIntegration(api_url)                                          # Create an instance of the LLMIntegration class

    # Preprocess the user input
    def preprocess_input(self, user_input):
        # Basic preprocessing: strip whitespace and convert to lowercase
        return user_input.strip().lower()                                                       # Return the preprocessed input

    # Generate a reasoned response using the deepseek-r1 model
    def get_reasoned_response(self, user_input):
        processed_input = self.preprocess_input(user_input)                                     # Preprocess the user input
        reasoned_response = self.llm_integration.generate_reasoned_response(processed_input)    # Generate a reasoned response
        return reasoned_response
    
    # Generate a simple response using the llama3.2 model
    def get_simple_response(self, user_input):
        processed_input = self.preprocess_input(user_input)                                     # Preprocess the user input
        simple_response = self.llm_integration.generate_simple_response(processed_input)        # Generate a simple response
        return simple_response                                                                  # Return the simple response

chatbot = Chatbot(api_url="http://localhost:11434/api/generate")                                # Create an instance of the Chatbot class

# Define the /chat endpoint
@app.route('/chat', methods=['POST'])                                                           # Define the /chat endpoint
def chat():
    data = request.get_json()                                                                   # Extract the JSON data from the request
    user_input = data.get('message')                                                            # Extract the user input from the JSON data
    reasoned_response = chatbot.get_reasoned_response(user_input)                               # Generate a reasoned response
    simple_response = chatbot.get_simple_response(reasoned_response)                            # Generate a simple response
    return jsonify({'response': simple_response})                                               # Return the response in the JSON format

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)