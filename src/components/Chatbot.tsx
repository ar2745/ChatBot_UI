import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chatbot.css';

const Chatbot: React.FC = () => {
    const [messages, setMessages] = useState<{ text: string, sender: string }[]>([]);
    const [input, setInput] = useState('');
    const [documents, setDocuments] = useState<string[]>([]);
    const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
    const [activeSection, setActiveSection] = useState<string>('chatHistory');
    const [chatHistory, setChatHistory] = useState<{ id: number, title: string, messages: { text: string, sender: string }[] }[]>([]);
    const [selectedChat, setSelectedChat] = useState<number | null>(null);
    const [reasoningMode, setReasoningMode] = useState(false); // New state variable
    const [editingChatId, setEditingChatId] = useState<number | null>(null); // New state variable for editing chat

    useEffect(() => {
        fetch('http://localhost:5000/documents')
            .then(response => response.json())
            .then(data => setDocuments(data.documents))
            .catch(error => console.error('Error fetching documents:', error));
        
        // Fetch chat history from local storage
        fetchChatHistory();
    }, []);

    const fetchChatHistory = () => {
        const history = localStorage.getItem('chatHistory');
        if (history) {
            setChatHistory(JSON.parse(history));
        }
    };

    const saveChatHistory = (history: { id: number, title: string, messages: { text: string, sender: string }[] }[]) => {
        localStorage.setItem('chatHistory', JSON.stringify(history));
    };

    const handleSendMessage = async () => {
        if (input.trim()) {
            const newMessage = { text: input, sender: 'user' };
            setMessages([...messages, newMessage]);
            const userMessage = input;
            setInput('');

            try {
                const response = await fetch('http://localhost:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage, document: selectedDocument, reasoning: reasoningMode }), // Include reasoning mode
                });

                const data = await response.json();
                const botMessage = { text: data.response, sender: 'bot' };
                setMessages(prevMessages => [...prevMessages, botMessage]);

                // Update chat history
                if (selectedChat !== null) {
                    const updatedHistory = chatHistory.map(chat => {
                        if (chat.id === selectedChat) {
                            return { ...chat, messages: [...chat.messages, newMessage, botMessage] };
                        }
                        return chat;
                    });
                    setChatHistory(updatedHistory);
                    saveChatHistory(updatedHistory);
                } else {
                    const newChat = {
                        id: chatHistory.length + 1,
                        title: `Chat Session ${chatHistory.length + 1}`,
                        messages: [newMessage, botMessage]
                    };
                    const updatedHistory = [...chatHistory, newChat];
                    setChatHistory(updatedHistory);
                    saveChatHistory(updatedHistory);
                    setSelectedChat(newChat.id);
                }
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

    const handleSidebarClick = (event: React.MouseEvent<HTMLDivElement>) => {
        if (event.target === event.currentTarget) {
            setSelectedDocument(null);
        }
    };

    const handleChatSelect = (chatId: number) => {
        const selectedChat = chatHistory.find(chat => chat.id === chatId);
        if (selectedChat) {
            setSelectedChat(chatId);
            setMessages(selectedChat.messages);
        }
    };

    const handleDeleteChat = (chatId: number) => {
        const updatedHistory = chatHistory.filter(chat => chat.id !== chatId);
        setChatHistory(updatedHistory);
        saveChatHistory(updatedHistory);
        if (selectedChat === chatId) {
            setSelectedChat(null);
            setMessages([]);
        }
    };

    const handleRenameChat = (chatId: number, newTitle: string) => {
        const updatedHistory = chatHistory.map(chat => {
            if (chat.id === chatId) {
                return { ...chat, title: newTitle };
            }
            return chat;
        });
        setChatHistory(updatedHistory);
        saveChatHistory(updatedHistory);
        setEditingChatId(null);
    };

    const handleNewChat = () => {
        const newChat = {
            id: chatHistory.length + 1,
            title: `Chat Session ${chatHistory.length + 1}`,
            messages: []
        };
        const updatedHistory = [...chatHistory, newChat];
        setChatHistory(updatedHistory);
        saveChatHistory(updatedHistory);
        setSelectedChat(newChat.id);
        setMessages([]);
    };

    const renderSection = () => {
        switch (activeSection) {
            case 'chatHistory':
                return (
                    <div>
                        <h3>Chat History</h3>
                        <ul>
                            {chatHistory.map(chat => (
                                <li key={chat.id}>
                                    {editingChatId === chat.id ? (
                                        <input
                                        type="text"
                                        defaultValue={chat.title}
                                        onBlur={(e) => handleRenameChat(chat.id, e.target.value)}
                                        onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
                                          if (e.key === 'Enter') {
                                            handleRenameChat(chat.id, e.currentTarget.value);
                                          }
                                        }}
                                        autoFocus
                                        />                                      
                                    ) : (
                                        <>
                                            <span onClick={() => handleChatSelect(chat.id)}>{chat.title}</span>
                                            <button onClick={() => setEditingChatId(chat.id)}>Rename</button>
                                            <button onClick={() => handleDeleteChat(chat.id)}>Delete</button>
                                        </>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                );
            case 'documents':
                return (
                    <div>
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
                );
            case 'settings':
                return (
                    <div>
                        <h3>Settings</h3>
                        <p>User preferences, notification settings, language selection...</p>
                    </div>
                );
            case 'helpSupport':
                return (
                    <div>
                        <h3>Help & Support</h3>
                        <p>FAQ, contact support, user guide...</p>
                    </div>
                );
            case 'profile':
                return (
                    <div>
                        <h3>Profile</h3>
                        <p>User profile information, edit profile, logout...</p>
                    </div>
                );
            case 'about':
                return (
                    <div>
                        <h3>About</h3>
                        <p>Information about the chatbot, version details, credits...</p>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="chatbot-container">
            <div className="sidebar" onClick={handleSidebarClick}>
                <div className="sidebar-header">
                    <span className="app-name">JAMAL 1.0</span>
                    <button className="new-chat-button" onClick={handleNewChat}>
                        <i className="fas fa-pen"></i>
                    </button>
                </div>
                <ul className="menu">
                    <li onClick={() => setActiveSection('chatHistory')}>Chat History</li>
                    <li onClick={() => setActiveSection('documents')}>Documents</li>
                    <li onClick={() => setActiveSection('settings')}>Settings</li>
                    <li onClick={() => setActiveSection('helpSupport')}>Help & Support</li>
                    <li onClick={() => setActiveSection('profile')}>Profile</li>
                    <li onClick={() => setActiveSection('about')}>About</li>
                </ul>
                <div className="section-content">
                    {renderSection()}
                </div>
            </div>
            <div className="main-content">
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
                        <button className={`reasoning-button ${reasoningMode ? 'active' : ''}`} onClick={() => setReasoningMode(!reasoningMode)}>
                            <i className="fas fa-lightbulb"></i>
                        </button>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                            placeholder="Type a message..."
                        />
                        <button onClick={handleSendMessage}>Send</button>
                        <label htmlFor="file-upload" className="upload-icon">
                            <i className="fas fa-paperclip"></i>
                        </label>
                        <input
                            id="file-upload"
                            type="file"
                            className="hidden-input"
                            onChange={handleFileChange}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Chatbot;