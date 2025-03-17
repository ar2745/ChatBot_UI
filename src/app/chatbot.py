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
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

CHATS_FOLDER = 'chats'
DOCUMENTS_FOLDER = 'documents'
LINKS_FOLDER = 'links'
UPLOADS_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'json', 'docx'}

app.config['CHATS_FOLDER'] = CHATS_FOLDER
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER
app.config['LINKS_FOLDER'] = LINKS_FOLDER
app.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER

if not os.path.exists(CHATS_FOLDER):
    os.makedirs(CHATS_FOLDER)

if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

if not os.path.exists(LINKS_FOLDER):
    os.makedirs(LINKS_FOLDER)

if not os.path.exists(UPLOADS_FOLDER):
    os.makedirs(UPLOADS_FOLDER)

chroma_client = chromadb.Client()       
collection = chroma_client.get_or_create_collection(name="chatbot_memory")
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Chatbot:
    def __init__(self, api_url):
        self.llm_integration = LLMIntegration(api_url)
        self.documents = {}
        self.links = {}

    def preprocess_input(self, user_input):
        return user_input.strip().lower()

    def get_reasoned_response(self, user_input):
        processed_input = self.preprocess_input(user_input)
        reasoned_response = self.llm_integration.generate_reasoned_response(processed_input)
        return reasoned_response

    def get_simple_response(self, user_input):
        processed_input = self.preprocess_input(user_input)
        simple_response = self.llm_integration.generate_simple_response(processed_input)
        return simple_response

    def extract_text_from_file(self, filepath):
        ext = filepath.rsplit('.', 1)[1].lower()
        if ext == 'pdf':
            return self.extract_text_from_pdf(filepath)
        elif ext == 'txt':
            return self.extract_text_from_txt(filepath)
        elif ext == 'json':
            return self.extract_text_from_json(filepath)
        elif ext == 'docx':
            return self.extract_text_from_docx(filepath)
        return ""

    def extract_text_from_pdf(self, filepath):
        text = ""
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text()
            return text
        except FileNotFoundError:
            return "Error file not found"
        except Exception as e:
            return f"Error: {e}"

    def extract_text_from_txt(self, filepath):
        try:
            with open(filepath, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "Error file not found"
        except Exception as e:
            return f"Error: {e}"

    def extract_text_from_json(self, filepath):
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                return json.dumps(data, indent=4)
        except FileNotFoundError:
            return "Error file not found"
        except Exception as e:
            return f"Error: {e}"

    def extract_text_from_docx(self, filepath):
        try:
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        except FileNotFoundError:
            return "Error file not found"
        except Exception as e:
            return f"Error: {e}"

    def extract_data_from_web_page(self, url):
        async def get_web_data(url):
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                return result.markdown
        return asyncio.run(get_web_data(url))

chatbot = Chatbot(api_url="http://localhost:11434/api/generate")

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the ChatBot API"})

@app.route('/documents', methods=['GET'])
def list_documents():
    return jsonify({"documents": list(chatbot.documents.keys())})

@app.route('/links', methods=['GET'])
def list_links():
    return jsonify({"links": list(chatbot.links.keys())})

@app.route('/document_upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['DOCUMENTS_FOLDER'], filename)
            file.save(filepath)
            # Check if chatbot object is available and functioning
            try:
                extracted_text = chatbot.extract_text_from_file(filepath)
                chatbot.documents[filename] = extracted_text
            except Exception as e:
                print("Error extracting text:", e)
                raise e
            return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
        return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        print(f"Error during file upload: {e}")
        return jsonify({"error": f"Error during file upload: {e}"}), 500

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

@app.route('/link_upload', methods=['POST'])
def crawl():
    data = request.get_json()
    urls = data.get('urls')
    if not urls:
        return jsonify({"response": "Error: Empty input"}), 400

    try:
        response = chatbot.extract_data_from_web_page(urls)
        if response:
            filename = secure_filename(f"{urls}.json")
            filepath = os.path.join(app.config['LINKS_FOLDER'], filename)
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
    filename = data.get('filename')
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

@app.route('/store_memory', methods=['POST'])
def store_memory():
    data = request.get_json()
    user_message = data.get('userMessage')
    bot_message = data.get('botMessage')
    documents = data.get('documents', [])
    links = data.get('links', [])
    conversation_id = data.get('conversationId')

    if not user_message and not bot_message:
        return jsonify({"error": "No message provided"}), 400

    # Create a unified metadata structure with a timestamp
    metadata = {
        "userMessage": user_message,
        "botMessage": bot_message,
        "documents": documents,
        "links": links,
        "timestamp": datetime.utcnow().isoformat(),
        "conversationId": conversation_id
    }

    metadata_json = json.dumps(metadata)

    embeddings = []
    if user_message:
        user_embedding = sentence_model.encode(user_message['text']).tolist()
        embeddings.append({"text": user_message['text'], 
                           "embedding": user_embedding, 
                           "metadata": metadata_json,
                           "conversation_id": conversation_id})
   
    if bot_message:
        bot_embedding = sentence_model.encode(bot_message['text']).tolist()
        embeddings.append({"text": bot_message['text'], 
                           "embedding": bot_embedding, 
                           "metadata": metadata_json,
                           "conversation_id": conversation_id})
    
    if documents:
        for doc in documents:
            doc_embedding = sentence_model.encode(doc).tolist()
            embeddings.append({"text": doc, 
                               "embedding": doc_embedding, 
                               "metadata": metadata_json,
                               "conversation_id": conversation_id})
    
    if links:
        for link in links:
            link_embedding = sentence_model.encode(link).tolist()
            embeddings.append({"text": link, 
                               "embedding": link_embedding, 
                               "metadata": metadata_json,
                               "conversation_id": conversation_id})

    for embedding in embeddings:
        collection.upsert(
            documents=[embedding["text"]],
            metadatas=[{"metadata": embedding["metadata"], "conversation_id": embedding["conversation_id"]}],
            embeddings=[embedding["embedding"]],
            ids=[embedding["text"]]
        )

    return jsonify({"message": "Memory stored successfully", "metadata": metadata}), 200
    
@app.route('/retrieve_memory', methods=['POST'])
def retrieve_memory():
    data = request.get_json()
    conversation_id = data.get('conversationId')

    if not conversation_id:
        return jsonify({"error": "No conversation ID provided"}), 400

    results = collection.query(
        query_texts=[""],
        n_results=100,
        where={"conversation_id": conversation_id}
    )

    memories = []
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    for metadata_item, doc in zip(metadatas, documents):
        metadata = metadata_item[0] if isinstance(metadata_item, list) else metadata_item

        try:
            metadata_json = json.loads(metadata.get("metadata", "{}"))
        except Exception:
            metadata_json = {}

        memories.append(metadata_json)

    return jsonify({"memories": memories}), 200

@app.route('/retrieve_latest_memory', methods=['POST'])
def retrieve_latest_memory():
    data = request.get_json()
    conversation_id = data.get('conversationId')

    if not conversation_id:
        return jsonify({"error": "No conversation ID provided"}), 400

    results = collection.query(
        query_texts=[""],
        n_results=100,
        where={"conversation_id": conversation_id}
    )

    memories = []
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    for metadata_item, doc in zip(metadatas, documents):
        metadata = metadata_item[0] if isinstance(metadata_item, list) else metadata_item

        try:
            metadata_json = json.loads(metadata.get("metadata", "{}"))
        except Exception:
            metadata_json = {}
        
        timestamp_str = metadata_json.get("timestamp", "")
        try:
            timestamp = datetime.fromisoformat(timestamp_str).replace(tzinfo=None)
        except ValueError:
            timestamp = datetime.min.replace(tzinfo=None)
        metadata_json["timestamp"] = timestamp

        memories.append(metadata_json)

    memories = sorted(memories, key=lambda x: x.get("timestamp", datetime.min), reverse=True)

    recent_memories = memories[:5]

    return jsonify({"memories": recent_memories}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')
    document_name = data.get('document')
    link = data.get('link')
    memories = data.get('memories')
    relevant_memories = []

    if not user_input:
        return jsonify({'response': 'Error: Empty input'})
    
    if len(user_input) > 512:
        return jsonify({'response': 'Error: Input too long'})
    
    if not isinstance(user_input, str):
        return jsonify({'response': 'Error: Invalid input type'})
    
    if user_input.lower() == '/bye':
        formatted_inquiry = f"Am trying to say goodbye to you. Please wish me well."
        simple_response = chatbot.get_simple_response(formatted_inquiry)
        return jsonify({'response': simple_response})
        exit()

    if memories:
        for memory in memories:
            print(f"Memory: {memory}")

    if relevant_memories:
        memories_input = f"{user_input}\n\n{' '.join(str(relevant_memories))}"
        print(f"Relevant memories: {memories_input}")
    else:
        memories_input = user_input

    try:
        if data.get('reasoning'):
            try:
                simple_response = chatbot.get_simple_response(memories_input)
                deepseek_input = f"Our client is requesting about this: {simple_response}"
                reasoned_response = chatbot.get_reasoned_response(deepseek_input)
                deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"
                final_response = chatbot.get_simple_response(deepseek_output)
                return jsonify({'response': final_response})
            except Exception as e:
                return jsonify({'response': f'Error): {e}'})
        elif document_name:
            if document_name in chatbot.documents:
                try:
                    doc_content = chatbot.documents[document_name]
                    combined_input = f"{memories_input}\n\nDocument Content:\n{doc_content}"
                    response = chatbot.get_simple_response(combined_input)
                    return jsonify({'response': response})
                except Exception as e:
                    return jsonify({'response': f'Error: {e}'})
            else:
                return jsonify({'response': 'Error: Document not found'})
        elif data.get('reasoning') and document_name:
            if document_name in chatbot.documents:
                try:
                    doc_content = chatbot.documents[document_name]
                    combined_input = f"{memories_input}\n\nDocument Content:\n{doc_content}"
                    deepseek_input = f"Our client is requesting about this: {combined_input}"
                    reasoned_response = chatbot.get_reasoned_response(deepseek_input)
                    deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"
                    final_response = chatbot.get_simple_response(deepseek_output)
                    return jsonify({'response': final_response})
                except Exception as e:
                    return jsonify({'response': f'Error: {e}'})
            else:
                return jsonify({'response': 'Error: Document not found'})
        elif link:
            if link in chatbot.links:
                try:
                    link_content = chatbot.links[link]
                    combined_input = f"{memories_input}\n\nLink Content:\n{link_content}"
                    response = chatbot.get_simple_response(combined_input)
                    return jsonify({'response': response})
                except Exception as e:
                    return jsonify({'response': f'Error: {e}'})
            else:
                return jsonify({'response': 'Error: Link not found'})
        elif data.get('reasoning') and link:
            if link in chatbot.links:
                try:
                    link_content = chatbot.links[link]
                    combined_input = f"{memories_input}\n\nLink Content:\n{link_content}"
                    deepseek_input = f"Our client is requesting about this: {combined_input}"
                    reasoned_response = chatbot.get_reasoned_response(deepseek_input)
                    deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"
                    final_response = chatbot.get_simple_response(deepseek_output)
                    return jsonify({'response': final_response})
                except Exception as e:
                    return jsonify({'response': f'Error: {e}'})
            else:
                return jsonify({'response': 'Error: Link not found'})
        elif data.get('reasoning') and document_name and link:
            if document_name in chatbot.documents and link in chatbot.links:
                try:
                    doc_content = chatbot.documents[document_name]
                    link_content = chatbot.links[link]
                    combined_input = f"{memories_input}\n\nDocument Content:\n{doc_content}\n\nLink Content:\n{link_content}"
                    deepseek_input = f"Our client is requesting about this: {combined_input}"
                    reasoned_response = chatbot.get_reasoned_response(deepseek_input)
                    deepseek_output = f"Here is the relevant reasoned response: {reasoned_response}"
                    final_response = chatbot.get_simple_response(deepseek_output)
                    return jsonify({'response': final_response})
                except Exception as e:
                    return jsonify({'response': f'Error: {e}'})
            else:
                return jsonify({'response': 'Error: Document or link not found'})
        else:
            try:
                simple_response = chatbot.get_simple_response(memories_input)
                return jsonify({'response': simple_response})
            except Exception as e:
                return jsonify({'response': f'Error: {e}'})
    except Exception as e:
        return jsonify({'response': f'Error: {e}'})

if __name__ == "__main__":
    app.run(port=5000, debug=True)