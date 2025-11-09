import React, { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { MemoizedMarkdown } from './MemoizedMarkdown';

const ChatWidget = ({ sessionId }, ref) => {
  const [isOpen, setIsOpen] = useState(true);
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: 'Hello! I\'m your virtual assistant for Happy Health Clinic. How can I help you today?',
      sender: 'bot',
      time: 'Just now'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Expose sendMessage function to parent component
  useImperativeHandle(ref, () => ({
    sendMessage: (message, imageData = null) => {
      sendMessageInternal(message, imageData);
    }
  }));

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
      checkAPIConnection();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const addMessage = (content, sender) => {
    const newMessage = {
      id: Date.now(),
      content,
      sender,
      time: getCurrentTime()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const setTypingIndicator = (show) => {
    setIsTyping(show);
  };

  const sendMessageToAPI = async (message) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ma/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  const sendImageToAPI = async (message, imageData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ma/chat/image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message || 'Vui lòng phân tích ảnh này',
          image: imageData,
          session_id: sessionId
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error sending image:', error);
      throw error;
    }
  };

  const sendMessageInternal = async (messageToSend, externalImageData = null) => {
    const message = messageToSend ? messageToSend.trim() : inputValue.trim();

    // Determine image source: external (from quick action) or selected (from file input)
    const imageToSend = externalImageData || selectedImage;

    // Check if we have image or message
    if (!message && !imageToSend) return;

    // Save image data BEFORE clearing
    const hasImage = imageToSend !== null;

    // Add user message to chat
    if (hasImage) {
      addMessage(`📸 [Image] ${message || 'Analyzing image...'}`, 'user');
    } else {
      addMessage(message, 'user');
    }
    if (message != null) {
      setInputValue('');
    }
    setImagePreview(null);
    setSelectedImage(null);

    // Show typing indicatorr
    setTypingIndicator(true);

    try {
      let response;
      // Call appropriate API - use saved image data
      if (hasImage) {
        response = await sendImageToAPI(message, imageToSend);
      } else {
        response = await sendMessageToAPI(message);
      }

      // Hide typing indicator
      setTypingIndicator(false);

      // Add bot response
      addMessage(response, 'bot');
    } catch (error) {
      setTypingIndicator(false);
      addMessage('I apologize, but I\'m having trouble connecting right now. Please try again or call us at (555) 123-4567.', 'bot');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessageInternal();
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Vui lòng chọn file ảnh (JPEG, PNG, etc.)');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Ảnh quá lớn! Vui lòng chọn ảnh dưới 5MB.');
      return;
    }

    // Convert to base64
    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target.result;
      setSelectedImage(imageData);
      setImagePreview(imageData);

      // Update placeholder
      if (textareaRef.current) {
        textareaRef.current.placeholder = '📸 Image selected. Describe your symptoms...';
      }
    };
    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (textareaRef.current) {
      textareaRef.current.placeholder = 'Type your message here...';
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const checkAPIConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        console.log('✅ Connected to clinic API');
      } else {
        console.warn('⚠️ API connection issue');
      }
    } catch (error) {
      console.error('❌ Cannot connect to API:', error);
      addMessage('⚠️ Note: I\'m currently in offline mode. Some features may be limited. Please call (555) 123-4567 for immediate assistance.', 'bot');
    }
  };

  // Auto-resize textarea
  const handleInput = (e) => {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  return (
    <div className={`chat-widget ${isOpen ? '' : 'minimized'}`} id="chatWidget">
      <div className="chat-header">
        <div className="chat-header-content">
          <span className="status-indicator"></span>
          <span className="chat-title">Chat with Assistant</span>
        </div>
        <button className="minimize-btn" onClick={toggleChat} aria-label="Minimize chat">−</button>
      </div>

      {isOpen && (
        <>
          <div className="chat-messages" id="chatMessages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                <div className="message-avatar">{message.sender === 'user' ? '👤' : '🤖'}</div>
                <div className="message-content">
                  <MemoizedMarkdown content={message.content} id={`msg-${message.id}`} />
                  <span className="message-time">{message.time}</span>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="message bot-message typing-message">
                <div className="message-avatar">🤖</div>

                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Image Preview Area */}
          {imagePreview && (
            <div className="image-preview">
              <div className="preview-header">
                <span>📸 Image selected</span>
                <button onClick={removeImage} className="remove-image-btn" title="Remove image">✕</button>
              </div>
              <img src={imagePreview} alt="Preview" className="preview-image" />
            </div>
          )}

          <div className="chat-input-container">
            <input
              type="file"
              id="imageInput"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleImageSelect}
            />
            <button
              className="upload-btn"
              onClick={() => document.getElementById('imageInput').click()}
              title="Upload image"
              aria-label="Upload image"
            >
              📷
            </button>
            <textarea
              ref={textareaRef}
              id="chatInput"
              className="chat-input"
              placeholder={imagePreview ? '📸 Image selected. Describe your symptoms...' : 'Type your message here...'}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onInput={handleInput}
              onKeyUp={handleKeyPress}
              rows="1"
            />
            <button className="send-btn" onClick={() => sendMessageInternal()} aria-label="Send message" disabled={isTyping}>
              <span className="send-icon">➤</span>
            </button>
          </div>
        </>
      )}

      {/* Chat Toggle Button (for mobile) */}
      {!isOpen && (
        <button className="chat-toggle-btn" onClick={toggleChat} aria-label="Open chat">
          💬
        </button>
      )}
    </div>
  );
};

export default forwardRef(ChatWidget);