import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
    const [query, setQuery] = useState('');
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [orderNumber, setOrderNumber] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState('initial'); // Track the current step in the process

    const handleInputChange = (e) => {
        setQuery(e.target.value);
    };

    const handleEmailChange = (e) => {
        setEmail(e.target.value);
    };

    const handleOtpChange = (e) => {
        setOtp(e.target.value);
    };

    const handleOrderNumberChange = (e) => {
        setOrderNumber(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query && step === 'initial') return;
        if (!email && step === 'requestEmail') return;
        if (!otp && step === 'requestOtp') return;
        if (!orderNumber && step === 'requestOrderNumber') return;

        const userMessage = { text: step === 'initial' ? query : step === 'requestEmail' ? email : step === 'requestOtp' ? otp : orderNumber, sender: 'user' };
        setMessages([...messages, userMessage]);

        setQuery('');
        setEmail('');
        setOtp('');
        setOrderNumber('');
        setLoading(true);

        try {
            const data = {};
            if (step === 'initial') {
                data.query = query;
            } else if (step === 'requestEmail') {
                data.query = query;
                data.email = email;
            } else if (step === 'requestOtp') {
                data.query = query;
                data.email = email;
                data.otp = otp;
            } else if (step === 'requestOrderNumber') {
                data.query = query;
                data.email = email;
                data.otp = otp;
                data.order_number = orderNumber;
            }

            const response = await axios.post('http://127.0.0.1:5000/handle_query', data);
            const botMessage = { text: response.data.prompt || response.data.answer || `Order Details: ${JSON.stringify(response.data.OrderDetails)}`, sender: 'bot' };
            setMessages([...messages, userMessage, botMessage]);

            if (response.data.prompt === 'Please provide your email address to track your order') {
                setStep('requestEmail');
            } else if (response.data.prompt === 'An OTP has been sent to your email. Please provide the OTP to continue.') {
                setStep('requestOtp');
            } else if (response.data.prompt === 'Please provide the OTP sent to your email') {
                setStep('requestOtp');
            } else if (response.data.prompt === 'Please provide your order number') {
                setStep('requestOrderNumber');
            } else {
                setStep('initial'); // Reset to initial step after completing the process
            }
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
                    {step === 'initial' && (
                        <input
                            type="text"
                            value={query}
                            onChange={handleInputChange}
                            placeholder="Ask a question..."
                            className="chat-input"
                        />
                    )}
                    {step === 'requestEmail' && (
                        <input
                            type="email"
                            value={email}
                            onChange={handleEmailChange}
                            placeholder="Enter your email..."
                            className="chat-input"
                        />
                    )}
                    {step === 'requestOtp' && (
                        <input
                            type="text"
                            value={otp}
                            onChange={handleOtpChange}
                            placeholder="Enter the OTP..."
                            className="chat-input"
                        />
                    )}
                    {step === 'requestOrderNumber' && (
                        <input
                            type="text"
                            value={orderNumber}
                            onChange={handleOrderNumberChange}
                            placeholder="Enter your order number..."
                            className="chat-input"
                        />
                    )}
                    <button type="submit" className="chat-submit-button">Send</button>
                </form>
            </div>
        </div>
    );
};

export default Chatbot;
