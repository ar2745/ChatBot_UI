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
   ```bash
   npm install

### Backend
1. **Navigate to the src directory**:
   ```bash
   cd src

3. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   venv\Scripts\activate

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

### Starting the Application
1. **Run the Flask server**:
   ```bash
   cd app
   python chatbot.py

3. **Run the Ollama server**:
   ```bash
   cd ollama
   ./ollama.exe serve

5. **Run the Node.js server**:
   ```bash
   cd ..
   npm start

This will start the development server and open the application in your default web browser.

### 🌟 Features
### Responsive Design 
The chatbot UI adapts to different screen sizes for a better user experience.

### State Management
Efficient handling of messages and user input.

### Customizable Styles 
Easily modify the appearance of the chatbot through CSS.

### Markdown Support
Rich text formatting for chatbot responses.

### File Uploads 
Users can upload documents (PDF, TXT, JSON, DOCX) which the chatbot can process and use in responses.

### Link Crawling
Users can provide URLs, and the chatbot will crawl and extract data from the web pages.

### Memory Storage: 
The chatbot stores conversation history and relevant data using ChromaDB and Sentence Transformers for embeddings.

### 📄 License
This project is open-source and available under the MIT License.

### 📁 Project Structure
The project is organized as follows:

```bash
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
