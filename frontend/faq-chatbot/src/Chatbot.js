// src/Chatbot.js
import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleInputChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query) return;

        const userMessage = { text: query, sender: 'user' };
        setMessages([...messages, userMessage]);
        setQuery('');
        setLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:5000/get_answer', { query });
            const botMessage = { text: response.data.answer, sender: 'bot' };
            setMessages([...messages, userMessage, botMessage]);
        } catch (error) {
            console.error('Error fetching the answer:', error);
            const errorMessage = { text: 'Sorry, something went wrong. Please try again later.', sender: 'bot' };
            setMessages([...messages, userMessage, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-window">
                <div className="chat-messages">
                    {messages.map((message, index) => (
                        <div key={index} className={`chat-message ${message.sender}`}>
                            <div className="chat-bubble">{message.text}</div>
                        </div>
                    ))}
                    {loading && <div className="chat-message bot"><div className="chat-bubble">Loading...</div></div>}
                </div>
                <form onSubmit={handleSubmit} className="chat-input-form">
                    <input
                        type="text"
                        value={query}
                        onChange={handleInputChange}
                        placeholder="Ask a question..."
                        className="chat-input"
                    />
                    <button type="submit" className="chat-submit-button">Send</button>
                </form>
            </div>
        </div>
    );
};

export default Chatbot;