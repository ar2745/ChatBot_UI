# 🚀 Welcome to Chatbot UI!

**Chatbot UI** is a modern and responsive user interface for a chatbot application built with React and Flask. This project aims to provide a seamless experience for users to interact with chatbots, featuring a clean design and intuitive functionality.

**Prerequisites**

- Node.js and npm
- Ollama
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
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

### Backend

1. **Navigate to the src directory**:
   ```bash
   cd ChatBot/src
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Starting the application

1. **Run the Flask server**:
   ```bash
   cd ChatBot/src/app
   python chatbot.py
   ```

2. **Run the Ollama server**:
   ```bash
   cd ChatBot/ollama
   ./ollama.exe serve
   ```

3. **Run the node server**:
   ```bash
   ch ChatBot
   npm start
   ```

   This will start the development server and open the application in your default web browser.

## 📁 Project Structure

The project is organized as follows:

```
chatbot-ui
├── src
│   ├── components        # Contains React components for the chatbot
│   ├── styles            # Contains CSS styles for the UI
│   ├── App.tsx           # Main application component
│   └── index.tsx         # Entry point of the application
├── public
│   ├── index.html        # Main HTML file
│   └── favicon.ico       # Favicon for the application
├── package.json          # NPM configuration file
├── tsconfig.json         # TypeScript configuration file
└── README.md             # Project documentation
```

## 🌟 Features

- **Responsive Design**: The chatbot UI adapts to different screen sizes for a better user experience.
- **State Management**: Efficient handling of messages and user input.
- **Customizable Styles**: Easily modify the appearance of the chatbot through CSS.
- **Markdown Support**: Rich text formatting for chatbot responses.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).