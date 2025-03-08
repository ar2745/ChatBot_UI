import isEqual from 'lodash.isequal';
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chatbot.css';

// Modal component for link input
const LinkModal: React.FC<{ show: boolean, onClose: () => void, onSubmit: (link: string) => void }> = ({ show, onClose, onSubmit }) => {
    const [link, setLink] = useState('');

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        onSubmit(link);
        setLink('');
    };

    if (!show) {
        return null;
    }

    return (
        <div className="modal">
            <div className="modal-content">
                <span className="close" onClick={onClose}>&times;</span>
                <h2>Enter Link</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={link}
                        onChange={(e) => setLink(e.target.value)}
                        placeholder="Enter URL"
                        required
                    />
                    <button type="submit">Submit</button>
                </form>
            </div>
        </div>
    );
};

// Chatbot component
const Chatbot: React.FC = () => {
    const [messages, setMessages] = useState<{ text: string, sender: string }[]>([]);
    const [input, setInput] = useState('');
    const [chats, setChats] = useState<string[]>([]);
    const [documents, setDocuments] = useState<string[]>([]);
    const [links, setLinks] = useState<string[]>([]);
    const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
    const [selectedLink, setSelectedLink] = useState<string | null>(null);
    const [activeSection, setActiveSection] = useState<string>('chatHistory');
    const [chatHistory, setChatHistory] = useState<{ id: number, title: string, messages: { text: string, sender: string }[] }[]>([]);
    const [linkHistory, setLinkHistory] = useState<string[]>([]);
    const [selectedChat, setSelectedChat] = useState<number | null>(null);
    const [reasoningMode, setReasoningMode] = useState(false);
    const [editingChatId, setEditingChatId] = useState<number | null>(null);
    const [voiceInputMode, setVoiceInputMode] = useState(false);
    const [voiceTimeout, setVoiceTimeout] = useState<NodeJS.Timeout | null>(null);
    const [linkInput, setLinkInput] = useState(''); // New state for link input
    const [showLinkModal, setShowLinkModal] = useState(false); // State to control the modal visibility

    useEffect(() => {
        fetchChatHistory();
        fetchDocumentHistory();
        fetchLinkHistory();
    
        // Set up periodic memory storage
        const intervalId = setInterval(() => {
            const lastUserMessage = messages.length > 0 ? messages[messages.length - 1] : undefined;
            const lastBotMessage = messages.length > 1 ? messages[messages.length - 2] : undefined;
            if (selectedChat !== null) {
                storeMemory(lastBotMessage, lastUserMessage, selectedDocument, selectedLink, selectedChat);
            }
        }, 10000); // Store memory every 60 seconds
    
        // Clean up the interval on component unmount
        return () => clearInterval(intervalId);
    }, [messages, selectedDocument, selectedLink, selectedChat]);

    const fetchChatHistory = () => {
        const history = localStorage.getItem('chatHistory');
        if (history) {
            setChatHistory(JSON.parse(history));
        }
    };

    const saveChatHistory = (history: { id: number, title: string, messages: { text: string, sender: string }[] }[]) => {
        localStorage.setItem('chatHistory', JSON.stringify(history));
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

    const fetchDocumentHistory = () => {
        fetch('http://localhost:5000/documents')
            .then(response => response.json())
            .then(data => setDocuments(data.documents))
            .catch(error => console.error('Error fetching documents:', error));
    };

    const handleDocumentSelect = (document: string) => {
        setSelectedDocument(document);
    };

    const handleDocumentUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
    
            try {
                console.log('Uploading file:', file.name); // Add this line for logging
                const response = await fetch('http://localhost:5000/document_upload', {
                    method: 'POST',
                    body: formData,
                });
    
                const responseText = await response.text(); // Get the full response text
                console.log('Server response:', responseText); // Log the full response text
    
                const data = JSON.parse(responseText); // Parse the response text as JSON
                if (data.error) {
                    console.error('Error from server:', data.error); // Add this line for logging
                    setMessages(prevMessages => [
                        ...prevMessages,
                        { text: `Error: ${data.error}`, sender: 'bot' }
                    ]);
                } else {
                    console.log('File uploaded successfully:', data.filename); // Add this line for logging
                    setMessages(prevMessages => [
                        ...prevMessages,
                        { text: `File uploaded successfully: ${data.filename}`, sender: 'bot' }
                    ]);
                    setDocuments(prevDocuments => [...prevDocuments, data.filename]);
                }
            } catch (error) {
                console.error('Error during file upload:', error); // Add this line for logging
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: 'Error: Unable to upload file.', sender: 'bot' }
                ]);
            }
        }
    };   

    const handleDocumentDelete = async (document: string) => {
        try {
            const response = await fetch('http://localhost:5000/document_delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: document }),
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
                    { text: `File deleted successfully: ${document}`, sender: 'bot' }
                ]);
                setDocuments(prevDocuments => prevDocuments.filter(doc => doc !== document));
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prevMessages => [
                ...prevMessages,
                { text: 'Error: Unable to delete file.', sender: 'bot' }
            ]);
        }
    };

    const fetchLinkHistory = () => {
        fetch('http://localhost:5000/links')
            .then(response => response.json())
            .then(data => setLinks(data.links))
            .catch(error => console.error('Error fetching links:', error));
    };

    const handleLinkUpload = async (link: string) => {
        try {
            const response = await fetch('http://localhost:5000/link_upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urls: link }),
            });

            const data = await response.json();
            if (data.response) {
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: `Link uploaded successfully: ${link}`, sender: 'bot' }
                ]);
                setLinks(prevLinks => [...prevLinks, link]);
            } else {
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: `Error: ${data.response}`, sender: 'bot' }
                ]);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prevMessages => [
                ...prevMessages,
                { text: 'Error: Unable to upload link.', sender: 'bot' }
            ]);
        }
    };

    const handleLinkDelete = async (link: string) => {
        try {
            const response = await fetch('http://localhost:5000/link_delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: link }), // Ensure the key matches what the server expects
            });
    
            const data = await response.json();
            if (data.response) {
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: `Link deleted successfully: ${link}`, sender: 'bot' }
                ]);
                setLinks(prevLinks => prevLinks.filter(l => l !== link));
            } else {
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: `Error: ${data.response}`, sender: 'bot' }
                ]);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prevMessages => [
                ...prevMessages,
                { text: 'Error: Unable to delete link.', sender: 'bot' }
            ]);
        }
    };

    const startVoiceRecognition = () => {
        const win: any = window;
        const SpeechRecognition = win.SpeechRecognition || win.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        let timeout: NodeJS.Timeout | null = null;

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            setInput(transcript);

            if (timeout) {
                clearTimeout(timeout);
            }

            timeout = setTimeout(() => {
                handleSendMessage();
            }, 4000);
        };

        recognition.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'network') {
                alert('Network error occurred during speech recognition. Please check your internet connection or use a different browser.');
            }
        };

        recognition.onend = () => {
            if (voiceInputMode) {
                recognition.start();
            }
        };

        recognition.start();
    };

    const handleSidebarClick = (event: React.MouseEvent<HTMLDivElement>) => {
        if (event.target === event.currentTarget) {
            setSelectedDocument(null);
            setSelectedLink(null);
        }
    };

    const storeMemory = async (userMessage?: { text: string, sender: string }, botMessage?: { text: string, sender: string }, document?: string | null, link?: string | null, conversationId?: number) => {
        const memoryData = {
            userMessage,
            botMessage,
            documents: document ? [document] : [],
            links: link ? [link] : [],
            conversationId
        };
    
        console.log('Storing memory data:', memoryData); // Add this line
    
        // Retrieve the last stored memory for comparison
        const lastStoredMemory = await retrieveLastStoredMemory(conversationId);
    
        // Check if the current memory is the same as the last stored memory
        if (lastStoredMemory && isMemoryEqual(memoryData, lastStoredMemory)) {
            console.log('Memory is the same as the last stored memory. Skipping storage.');
            return;
        }
    
        try {
            const response = await fetch('http://localhost:5000/store_memory', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(memoryData),
            });
    
            if (response.ok) {
                console.log('Memory stored successfully');
            } else {
                const errorData = await response.json();
                console.error('Error storing memory:', errorData.error);
            }
        } catch (error) {
            console.error('Error storing memory:', error);
        }
    };

    const retrieveMemory = async (query: string, conversationId?: number) => {
        try {
            const response = await fetch('http://localhost:5000/retrieve_memory', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query, conversationId }),
            });
    
            const data = await response.json();
            if (data.memories) {
                return data.memories;
            } else {
                console.error('Error retrieving memories:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error retrieving memories:', error);
            return [];
        }
    };

    const retrieveLastStoredMemory = async (conversationId?: number) => {
        try {
            const response = await fetch('http://localhost:5000/retrieve_last_memory', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ conversationId }),
            });
    
            const data = await response.json();
            return data.memory;
        } catch (error) {
            console.error('Error retrieving last stored memory:', error);
            return null;
        }
    };

    const isMemoryEqual = (memory1: any, memory2: any) => {
        return isEqual(memory1, memory2);
    };

    const handleSendMessage = async () => {
        if (input.trim()) {
            const newMessage = { text: input, sender: 'user' };
            setMessages([...messages, newMessage]);
            const userMessage = input;
            setInput('');
    
            try {
                // Retrieve relevant past interactions
                const retrievedMemories = await retrieveMemory(userMessage, selectedChat ?? undefined);
                console.log('Retrieved memories:', retrievedMemories);
    
                // Use retrieved memories to provide context for the new message
                const response = await fetch('http://localhost:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage, document: selectedDocument, link: selectedLink, reasoning: reasoningMode, memories: retrievedMemories, conversationId: selectedChat }),
                });
    
                const data = await response.json();
                const botMessage = { text: data.response, sender: 'bot' };
                setMessages(prevMessages => [...prevMessages, botMessage]);
    
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
    
                // Store the new message in memory
                storeMemory(newMessage, botMessage, selectedDocument, selectedLink, selectedChat ?? undefined);
    
            } catch (error) {
                console.error('Error:', error);
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: 'Error: Unable to get response from the server.', sender: 'bot' }
                ]);
            }
        }
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
                                    onClick={() => handleDocumentSelect(doc)}
                                >
                                    {doc}
                                    <button onClick={() => handleDocumentDelete(doc)}>Delete</button>
                                </li>
                            ))}
                        </ul>
                    </div>
                );
            case 'links':
                return (
                    <div>
                        <h3>Links</h3>
                        <ul>
                            {links.map((link, index) => (
                                <li
                                    key={index}
                                    className={selectedLink === link ? 'selected' : ''}
                                    onClick={() => setSelectedLink(link)}
                                >
                                    {link}
                                    <button onClick={() => handleLinkDelete(link)}>Delete</button>
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
                    <li onClick={() => setActiveSection('links')}>Links</li>
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
                        <button className="link-button" onClick={() => setShowLinkModal(true)}>
                            <i className="fas fa-link"></i>
                        </button>
                        <div className="input-container">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                placeholder="Type a message..."
                            />
                            <button className={`voice-input-button ${voiceInputMode ? 'active' : ''}`} onClick={() => {
                                setVoiceInputMode(!voiceInputMode);
                                if (!voiceInputMode) {
                                    startVoiceRecognition();
                                }
                            }}>
                                <i className="fas fa-microphone"></i>
                            </button>
                        </div>
                        <button onClick={handleSendMessage}>Send</button>
                        <label htmlFor="file-upload" className="upload-icon">
                            <i className="fas fa-paperclip"></i>
                        </label>
                        <input
                            id="file-upload"
                            type="file"
                            className="hidden-input"
                            onChange={handleDocumentUpload}
                        />
                    </div>
                </div>
            </div>
            <LinkModal show={showLinkModal} onClose={() => setShowLinkModal(false)} onSubmit={handleLinkUpload} />
        </div>
    );
};

export default Chatbot;