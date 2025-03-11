# 🚀 Welcome to Chatbot UI!

**Chatbot UI** is a modern and responsive user interface for a chatbot application built with React and Flask. This project aims to provide a seamless experience for users to interact with chatbots, featuring a clean design and intuitive functionality.

## Prerequisites

- Node.js and npm
- Python 3.x
- Flask
- Flask-CORS

## 📦 Getting Started

To get started with the Chatbot UI project, follow these steps:

### Frontend

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/chatbot-ui.git
   cd chatbot-ui

2. **Install dependencies**:
   npm install

### Backend
1. **Navigate to the src directory**:
   cd src

2. **Create a virtual environment and activate it**:
   python -m venv venv
   venv\Scripts\activate

3. **Install dependencies**:
   pip install -r requirements.txt

### Starting the Application
1. **Run the Flask server**:
   cd app
   python chatbot.py

2. **Run the Ollama server**:
   cd ollama
   ./ollama.exe serve

3. **Run the Node.js server**:
   cd ..
   npm start

This will start the development server and open the application in your default web browser.

📁 Project Structure
The project is organized as follows:

ChatBot_UI
├── .gitignore
├── package.json
├── README.md
├── requirements.txt
├── setup.ps1
├── start.ps1
├── ollama/
│   └── ollama.exe
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── App.tsx
│   ├── index.tsx
│   ├── react-app-env.d.ts
│   ├── app/
│   │   ├── chatbot.py
│   │   ├── llm_integration.py
│   │   ├── routes.py
│   │   ├── chats/
│   │   ├── documents/
│   │   ├── links/
│   │   └── uploads/
│   ├── components/
│   │   ├── Chatbot.css
│   │   └── Chatbot.tsx
│   └── styles/
│       └── index.css
└── .vscode/
    └── settings.json

🌟 Features
Responsive Design: The chatbot UI adapts to different screen sizes for a better user experience.
State Management: Efficient handling of messages and user input.
Customizable Styles: Easily modify the appearance of the chatbot through CSS.
Markdown Support: Rich text formatting for chatbot responses.
File Uploads: Users can upload documents (PDF, TXT, JSON, DOCX) which the chatbot can process and use in responses.
Link Crawling: Users can provide URLs, and the chatbot will crawl and extract data from the web pages.
Memory Storage: The chatbot stores conversation history and relevant data using ChromaDB and Sentence Transformers for embeddings.

### API Endpoints
GET /: Welcome message for the ChatBot API.
GET /documents: List uploaded documents.
GET /links: List uploaded links.
POST /document_upload: Upload a document.
POST /document_delete: Delete a document.
POST /link_upload: Upload a link and crawl the web page.
POST /link_delete: Delete a link.
POST /store_memory: Store conversation memory.
POST /retrieve_memory: Retrieve conversation memory.
POST /retrieve_latest_memory: Retrieve the latest conversation memory.
POST /chat: Handle chat interactions and generate responses.

🤝 Contributing
Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

📄 License
This project is open-source and available under the MIT License.