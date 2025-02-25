from flask import Flask, request, jsonify
from flask_cors import CORS
from src.app.llm_integration import LLMIntegration
import PyPDF2
import json
import docx
from werkzeug.utils import secure_filename
import os
import asyncio
from crawl4ai import AsyncWebCrawler

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
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'uploads'
LINKS_FOLDER = 'links'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'json', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LINKS_FOLDER'] = LINKS_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(LINKS_FOLDER):
    os.makedirs(LINKS_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define the Chatbot class
class Chatbot:
    # Initialize the Chatbot with the LLMIntegration class
    def __init__(self, api_url):
        self.llm_integration = LLMIntegration(api_url)                                              # Create an instance of the LLMIntegration class
        self.documents = {}                                                                         # Initialize a dictionary to store uploaded documents
        self.links = {}                                                                             # Initialize a dictionary to store extracted data from web pages

    # Preprocess the user input
    def preprocess_input(self, user_input):
        # Basic preprocessing: strip whitespace and convert to lowercase
        return user_input.strip().lower()                                                           # Return the preprocessed input
    
    # Generate a reasoned response using the deepseek-r1 model
    def get_reasoned_response(self, user_input):
        processed_input = self.preprocess_input(user_input)                                         # Preprocess the user input
        reasoned_response = self.llm_integration.generate_reasoned_response(processed_input)        # Generate a reasoned response
        return reasoned_response                                                                    # Return the reasoned response
    
    # Generate a simple response using the llama3.2 model
    def get_simple_response(self, user_input):
        processed_input = self.preprocess_input(user_input)                                         # Preprocess the user input
        simple_response = self.llm_integration.generate_simple_response(processed_input)            # Generate a simple response
        return simple_response                                                                      # Return the simple response
    
    # Extract text from different file formats
    def extract_text_from_file(self, filepath):
        ext = filepath.rsplit('.', 1)[1].lower()                                                    # Get the file extension
        if ext == 'pdf':                                                                            # Check if the file is a PDF
            return self.extract_text_from_pdf(filepath)                                             # Extract text from PDF
        elif ext == 'txt':                                                                          # Check if the file is a text file
            return self.extract_text_from_txt(filepath)                                             # Extract text from text file
        elif ext == 'json':                                                                         # Check if the file is a JSON file
            return self.extract_text_from_json(filepath)                                            # Extract text from JSON file
        elif ext == 'docx':                                                                         # Check if the file is a DOCX file
            return self.extract_text_from_docx(filepath)                                            # Extract text from DOCX file
        return ""                                                                                   # Return an empty string if the file format is not supported

    # Extract text from a PDF file
    def extract_text_from_pdf(self, filepath):
        text = ""                                                                                   # Initialize an empty string to store the text
        try:
            with open(filepath, 'rb') as file:                                                          # Open the PDF file in read-binary mode
                reader = PyPDF2.PdfReader(file)                                                         # Create a PDF reader object
                for page_num in range(len(reader.pages)):                                               # Iterate over the pages in the PDF
                    text += reader.pages[page_num].extract_text()                                       # Extract text from the page and append to the text string
            return text                                                                                 # Return the extracted text
        except FileNotFoundError:
            return "Error file not found"                                                               # Return an error message if the file is not found
        except Exception as e:
            return f"Error: {e}"                                                                        # Return the exception message
        
    # Extract text from a text file
    def extract_text_from_txt(self, filepath):
        try:
            with open(filepath, 'r') as file:                                                           # Open the text file in read mode
                return file.read()                                                                      # Read the contents of the file and return as a string
        except FileNotFoundError:
            return "Error file not found"                                                               # Return an error message if the file is not found
        except Exception as e:
            return f"Error: {e}"                                                                        # Return the exception message

    # Extract text from a JSON file
    def extract_text_from_json(self, filepath):
        try:
            with open(filepath, 'r') as file:                                                           # Open the JSON file in read mode
                data = json.load(file)                                                                  # Load the JSON data
                return json.dumps(data, indent=4)                                                       # Return the JSON data as a formatted string
        except FileNotFoundError:
            return "Error file not found"                                                               # Return an error message if the file is not found
        except Exception as e:
            return f"Error: {e}"                                                                        # Return the exception message
        
    # Extract text from a DOCX file
    def extract_text_from_docx(self, filepath):
        try:
            doc = docx.Document(filepath)                                                               # Open the DOCX file
            return "\n".join([para.text for para in doc.paragraphs])                                    # Extract text from the paragraphs and join them with newline characters
        except FileNotFoundError:
            return "Error file not found"                                                               # Return an error message if the file is not found
        except Exception as e:
            return f"Error: {e}"                                                                        # Return the exception message
        
    # Extract data from a web page
    def extract_data_from_web_page(self, url):
        # Call the web crawler API here and return the result
        async def get_web_data(url):
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                )
                return result.markdown
            
        return asyncio.run(get_web_data(url))                                                                       # Return an error message
        
# Create an instance of the Chatbot class
chatbot = Chatbot(api_url="http://localhost:11434/api/generate")                                    # Create an instance of the Chatbot class

# Define the / endpoint
@app.route('/', methods=['GET'])                                                                   # Define the / endpoint
def home():                                                                                         # Define the home function
    return jsonify({"message": "Welcome to the ChatBot API"})                                       # Return a welcome message

# Define the /documents endpoint
@app.route('/documents', methods=['GET'])                                                           # Define the /documents endpoint
def list_documents():                                                                               # Define the list_documents function
    return jsonify({"documents": list(chatbot.documents.keys())})                                   # Return the list of uploaded documents

@app.route('/links', methods=['GET'])
def list_links():
    print("Received request for /links")
    return jsonify({"links": list(chatbot.links.keys())})

# Define the /upload endpoint
@app.route('/document_upload', methods=['POST'])                                                             # Define the /upload endpoint
def upload_file():                                                                                  # Define the upload_file function
    if 'file' not in request.files:                                                                 # Check if the request contains a file part
        return jsonify({"error": "No file part"}), 400                                              # Return an error response if no file part is found
    file = request.files['file']                                                                    # Get the file from the request
    if file.filename == '':                                                                         # Check if the file name is empty
        return jsonify({"error": "No selected file"}), 400                                          # Return an error response if no file is selected
    if file and allowed_file(file.filename):                                                        # Check if the file is allowed
        filename = secure_filename(file.filename)                                                   # Secure the filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)                              # Get the file path
        file.save(filepath)                                                                         # Save the file to the specified path
        chatbot.documents[filename] = chatbot.extract_text_from_file(filepath)                      # Extract text from the file and store it in the documents dictionary
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200        # Return a success response
    return jsonify({"error": "File type not allowed"}), 400                                         # Return an error response if the file type is not allowed

@app.route('/document_delete', methods=['POST'])
def delete_document():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({"response": "Error: No filename provided"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"response": "Error: File not found"}), 404

    try:
        os.remove(filepath)
        del chatbot.documents[filename]
        return jsonify({"response": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"response": f"Error: {e}"}), 500
    
# Define the /link_upload endpoint
@app.route('/link_upload', methods=['POST'])
def crawl():
    data = request.get_json()
    urls = data.get('urls')
    if not urls:
        return jsonify({"response": "Error: Empty input"}), 400

    # Call the web crawler API here and return the result
    try:
        response = chatbot.extract_data_from_web_page(urls)
        if response:
            # Generate a safe filename
            filename = secure_filename(f"{urls}.json")
            filepath = os.path.join(app.config['LINKS_FOLDER'], filename)
            # Save the response to a file
            with open(filepath, 'w') as file:
                json.dump(response, file)
            chatbot.links[filename] = response
            return jsonify({"response": response}), 200
        else:
            return jsonify({"response": "Error: Unable to extract data"}), 500
    except Exception as e:
        return jsonify({"response": f"Error: {e}"}), 500

@app.route('/link_delete', methods=['POST'])
def delete_link():
    data = request.get_json()
    filename = data.get('filename')  # Ensure the key matches what the client sends
    if not filename:
        return jsonify({"response": "Error: No filename provided"}), 400

    filepath = os.path.join(app.config['LINKS_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"response": "Error: File not found"}), 404

    try:
        os.remove(filepath)
        del chatbot.links[filename]
        return jsonify({"response": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"response": f"Error: {e}"}), 500
    
# Define the /chat endpoint
@app.route('/chat', methods=['POST'])                                                               # Define the /chat endpoint
def chat():                                                                                         # Define the chat function
    data = request.get_json()                                                                       # Get the JSON data from the request
    user_input = data.get('message')                                                                # Get the user input from the JSON data
    document_name = data.get('document')                                                            # Get the document name from the JSON data                                                                       # Get the link from the JSON data
    link = data.get('link')
    
    if not user_input:                                                                              # Check if the user input is empty
        return jsonify({'response': 'Error: Empty input'})                                          # Return an error response if the input is empty
    elif len(user_input) > 512:                                                                     # Check if the user input is too long
        return jsonify({'response': 'Error: Input too long'})                                       # Return an error response if the input is too long
    elif not isinstance(user_input, str):                                                           # Check if the user input is not a string
        return jsonify({'response': 'Error: Invalid input type'})                                   # Return an error response if the input is not a string
    elif user_input.lower() == '/bye':                                                              # Check if the user input is '/bye'
        formatted_inquiry = f"Am trying to say goodbye to you. Please wish me well."                # Format the user input
        simple_response = chatbot.get_simple_response(formatted_inquiry)                            # Generate a simple response
        return jsonify({'response': simple_response})                                               # Return the simple response
        exit()
    elif data.get('reasoning'):                                                                     # Check if the reasoning flag is set
        try:                                                                                        # Try to process the deepseek request
            simple_response = chatbot.get_simple_response(user_input)                               # Generate a simple response
            deepseek_input = f"Our client is requesting about this: {simple_response}"              # Format the deepseek input
            reasoned_response = chatbot.get_reasoned_response(deepseek_input)                       # Generate a reasoned response
            deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"        # Format the deepseek output
            final_response = chatbot.get_simple_response(deepseek_output)                           # Generate a simple response
            return jsonify({'response': final_response})                                            # Return the final response
        except Exception as e:                                                                      # Handle exceptions
            return jsonify({'response': f'Error: {e}'})                                             # Return an error response
    elif document_name:                                                                             # Check if a document name is provided
        if document_name in chatbot.documents:                                                      # Check if the document exists in the documents dictionary
            try:
                doc_content = chatbot.documents[document_name]                                          # Get the content of the document
                combined_input = f"{user_input}\n\nDocument Content:\n{doc_content}"                    # Combine the user input and document content
                print(combined_input)
                response = chatbot.get_simple_response(combined_input)                                  # Generate a simple response
                return jsonify({'response': response})                                                  # Return the response
            except Exception as e:                                                                      # Handle exceptions
                return jsonify({'response': f'Error: {e}'})                                             # Return an error response
        else:                                                                                       # If the document does not exist
            return jsonify({'response': 'Error: Document not found'})                               # Return an error response
    elif data.get('reasoning') and document_name:
        if document_name in chatbot.documents:                                                      # Check if the document exists in the documents dictionary
            try:
                doc_content = chatbot.documents[document_name]                                          # Get the content of the document
                combined_input = f"{user_input}\n\nDocument Content:\n{doc_content}"                    # Combine the user input and document content
                deepseek_input = f"Our client is requesting about this: {combined_input}"                # Format the deepseek input
                reasoned_response = chatbot.get_reasoned_response(deepseek_input)                       # Generate a reasoned response
                deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"        # Format the deepseek output
                final_response = chatbot.get_simple_response(deepseek_output)                           # Generate a simple response
                return jsonify({'response': final_response})                                            # Return the final response
            except Exception as e:                                                                      # Handle exceptions
                return jsonify({'response': f'Error: {e}'})                                             # Return an error response
        else:                                                                                       # If the document does not exist
            return jsonify({'response': 'Error: Document not found'})                               # Return an error response
    elif link:
        if link in chatbot.links:                                                                   # Check if the link exists in the links dictionary
            try:
                link_content = chatbot.links[link]                                                       # Get the content of the link
                combined_input = f"{user_input}\n\nLink Content:\n{link_content}"                        # Combine the user input and link content
                response = chatbot.get_simple_response(combined_input)                                   # Generate a simple response
                return jsonify({'response': response})                                                   # Return the response
            except Exception as e:                                                                      # Handle exceptions
                return jsonify({'response': f'Error: {e}'})                                             # Return an error response
        else:                                                                                       # If the link does not exist
            return jsonify({'response': 'Error: Link not found'})                                     # Return an error response
    elif data.get('reasoning') and link:
        if link in chatbot.links:                                                                   # Check if the link exists in the links dictionary
            try:
                link_content = chatbot.links[link]                                                       # Get the content of the link
                combined_input = f"{user_input}\n\nLink Content:\n{link_content}"                        # Combine the user input and link content
                deepseek_input = f"Our client is requesting about this: {combined_input}"                # Format the deepseek input
                reasoned_response = chatbot.get_reasoned_response(deepseek_input)                       # Generate a reasoned response
                deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"        # Format the deepseek output
                final_response = chatbot.get_simple_response(deepseek_output)                           # Generate a simple response
                return jsonify({'response': final_response})                                            # Return the final response
            except Exception as e:                                                                      # Handle exceptions
                return jsonify({'response': f'Error: {e}'})                                             # Return an error response
        else:                                                                                       # If the link does not exist
            return jsonify({'response': 'Error: Link not found'})                                     # Return an error response
    elif data.get('reasoning') and document_name and link:
        if document_name in chatbot.documents and link in chatbot.links:                              # Check if the document and link exist
            try:
                doc_content = chatbot.documents[document_name]                                          # Get the content of the document
                link_content = chatbot.links[link]                                                       # Get the content of the link
                combined_input = f"{user_input}\n\nDocument Content:\n{doc_content}\n\nLink Content:\n{link_content}" # Combine the user input, document content, and link content
                deepseek_input = f"Our client is requesting about this: {combined_input}"                # Format the deepseek input
                reasoned_response = chatbot.get_reasoned_response(deepseek_input)                       # Generate a reasoned response
                deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"        # Format the deepseek output
                final_response = chatbot.get_simple_response(deepseek_output)                           # Generate a simple response
                return jsonify({'response': final_response})                                            # Return the final response
            except Exception as e:                                                                      # Handle exceptions
                return jsonify({'response': f'Error: {e}'})                                             # Return an error response
        else:                                                                                       # If the document or link does not exist
            return jsonify({'response': 'Error: Document or link not found'})                        # Return an error responseected
    else:                                                                                           # If no special case is detected
        try:
            simple_response = chatbot.get_simple_response(user_input)                                   # Generate a simple response
            return jsonify({'response': simple_response})                                               # Return the simple response
        except Exception as e:                                                                      # Handle exceptions
            return jsonify({'response': f'Error: {e}'})                                                 # Return an error response

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)