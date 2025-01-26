import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chatbot.css';

const Chatbot: React.FC = () => {
    const [messages, setMessages] = useState<{ text: string, sender: string }[]>([]);
    const [input, setInput] = useState('');

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
                    body: JSON.stringify({ message: userMessage }),
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

    return (
        <div className="chatbot-container">
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
            </div>
        </div>
    );
};

export default Chatbot;