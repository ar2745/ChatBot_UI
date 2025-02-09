import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chatbot.css';

const Chatbot: React.FC = () => {
    const [messages, setMessages] = useState<{ text: string, sender: string }[]>([]);
    const [input, setInput] = useState('');
    const [documents, setDocuments] = useState<string[]>([]);
    const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

    useEffect(() => {
        fetch('http://localhost:5000/documents')
            .then(response => response.json())
            .then(data => setDocuments(data.documents))
            .catch(error => console.error('Error fetching documents:', error));
    }, []);

    const handleSendMessage = async () => {
        if (input.trim()) {
            setMessages([...messages, { text: input, sender: 'user' }]);
            const userMessage = input;
            setInput('');

            try {
                const response = await fetch('http://localhost:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage, document: selectedDocument }),
                });

                const data = await response.json();
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: data.response, sender: 'bot' }
                ]);
            } catch (error) {
                console.error('Error:', error);
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: 'Error: Unable to get response from the server.', sender: 'bot' }
                ]);
            }
        }
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('http://localhost:5000/upload', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();
                if (data.error) {
                    setMessages(prevMessages => [
                        ...prevMessages,
                        { text: `Error: ${data.error}`, sender: 'bot' }
                    ]);
                } else {
                    setMessages(prevMessages => [
                        ...prevMessages,
                        { text: `File uploaded successfully: ${data.filename}`, sender: 'bot' }
                    ]);
                    setDocuments(prevDocuments => [...prevDocuments, data.filename]);
                }
            } catch (error) {
                console.error('Error:', error);
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: 'Error: Unable to upload file.', sender: 'bot' }
                ]);
            }
        }
    };

    return (
        <div className="chatbot-container">
            <div className="document-list">
                <h3>Uploaded Documents</h3>
                <ul>
                    {documents.map((doc, index) => (
                        <li
                            key={index}
                            className={selectedDocument === doc ? 'selected' : ''}
                            onClick={() => setSelectedDocument(doc)}
                        >
                            {doc}
                        </li>
                    ))}
                </ul>
            </div>
            <div className="chat-section">
                <div className="chatbot-header">Chatbot</div>
                <div className="chatbot-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.sender}`}>
                            <ReactMarkdown>{msg.text}</ReactMarkdown>
                        </div>
                    ))}
                </div>
                <div className="chatbot-input">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Type a message..."
                    />
                    <button onClick={handleSendMessage}>Send</button>
                    <label htmlFor="file-upload" className="upload-icon">📎</label>
                    <input
                        id="file-upload"
                        type="file"
                        className="hidden-input"
                        onChange={handleFileChange}
                    />
                </div>
            </div>
        </div>
    );
};

export default Chatbot;