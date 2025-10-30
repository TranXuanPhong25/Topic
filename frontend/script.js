// Medical Clinic Chat Interface JavaScript

// Configuration
const API_BASE_URL = 'http://localhost:8000';
let sessionId = generateSessionId();

// Generate unique session ID
function generateSessionId() {
   return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Get current time string
function getCurrentTime() {
   const now = new Date();
   return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// Add message to chat
function addMessage(content, isUser = false) {
   const messagesContainer = document.getElementById('chatMessages');
   const messageDiv = document.createElement('div');
   messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

   const avatar = document.createElement('div');
   avatar.className = 'message-avatar';
   avatar.textContent = isUser ? '👤' : '🤖';

   const contentDiv = document.createElement('div');
   contentDiv.className = 'message-content';

   // Parse markdown-style formatting
   const formattedContent = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');

   contentDiv.innerHTML = `
        <p>${formattedContent}</p>
        <span class="message-time">${getCurrentTime()}</span>
    `;

   messageDiv.appendChild(avatar);
   messageDiv.appendChild(contentDiv);
   messagesContainer.appendChild(messageDiv);

   // Scroll to bottom
   messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show/hide typing indicator
function setTypingIndicator(show) {
   const indicator = document.getElementById('typingIndicator');
   indicator.style.display = show ? 'flex' : 'none';

   if (show) {
      const messagesContainer = document.getElementById('chatMessages');
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
   }
}

// Send message to API
async function sendMessageToAPI(message) {
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
}

// Image handling
let selectedImageData = null;

function handleImageSelect(event) {
   const file = event.target.files[0];
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
      selectedImageData = e.target.result;
      // Show preview
      document.getElementById('previewImg').src = selectedImageData;
      document.getElementById('imagePreview').style.display = 'block';

      // Update placeholder
      const input = document.getElementById('chatInput');
      input.placeholder = '📸 Image selected. Describe your symptoms...';
   };
   reader.readAsDataURL(file);
}

function removeImage() {
   selectedImageData = null;
   document.getElementById('imagePreview').style.display = 'none';
   document.getElementById('imageInput').value = '';
   document.getElementById('chatInput').placeholder = 'Type your message here...';
}

// Send image with message to API
async function sendImageToAPI(message, imageData) {
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
}

// Send message
async function sendMessage() {
   const input = document.getElementById('chatInput');
   const message = input.value.trim();

   // Check if we have image or message
   if (!message && !selectedImageData) return;

   // Save image data BEFORE clearing (important!)
   const hasImage = selectedImageData !== null;
   const imageDataToSend = selectedImageData; // Store before clearing

   // Add user message to chat
   if (hasImage) {
      addMessage(`📸 [Image] ${message || 'Analyzing image...'}`, true);
   } else {
      addMessage(message, true);
   }

   input.value = '';

   // Clear image preview AFTER saving the data
   if (hasImage) {
      removeImage();
   }

   // Resize textarea back to 1 row
   input.rows = 1;

   // Show typing indicator
   setTypingIndicator(true);

   // Disable send button
   const sendBtn = document.querySelector('.send-btn');
   sendBtn.disabled = true;

   try {
      let response;

      // Call appropriate API - use saved image data
      if (hasImage) {
         response = await sendImageToAPI(message, imageDataToSend);
      } else {
         response = await sendMessageToAPI(message);
      }

      // Hide typing indicator
      setTypingIndicator(false);

      // Add bot response
      addMessage(response, false);
   } catch (error) {
      setTypingIndicator(false);
      addMessage('I apologize, but I\'m having trouble connecting right now. Please try again or call us at (555) 123-4567.', false);
   } finally {
      // Re-enable send button
      sendBtn.disabled = false;
      input.focus();
   }
}

// Send quick message
function sendQuickMessage(message) {
   const input = document.getElementById('chatInput');
   input.value = message;
   sendMessage();

   // Scroll to chat widget
   const chatWidget = document.getElementById('chatWidget');
   chatWidget.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

// Handle Enter key press
function handleKeyPress(event) {
   if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
   }
}

// Toggle chat minimize/maximize
function toggleChat() {
   const chatWidget = document.getElementById('chatWidget');
   chatWidget.classList.toggle('minimized');
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', () => {
   const textarea = document.getElementById('chatInput');

   textarea.addEventListener('input', function () {
      this.rows = 1;
      const rows = Math.min(5, Math.floor(this.scrollHeight / 24));
      this.rows = rows;
   });

   // Focus input on load
   textarea.focus();

   // Check API connection
   checkAPIConnection();
});

// Check API connection
async function checkAPIConnection() {
   try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
         console.log('✅ Connected to clinic API');
      } else {
         console.warn('⚠️ API connection issue');
      }
   } catch (error) {
      console.error('❌ Cannot connect to API:', error);
      addMessage('⚠️ Note: I\'m currently in offline mode. Some features may be limited. Please call (555) 123-4567 for immediate assistance.', false);
   }
}

// Example: Load chat history on page load
async function loadChatHistory() {
   try {
      const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}`);
      if (response.ok) {
         const data = await response.json();
         if (data.messages && data.messages.length > 0) {
            // Display previous messages
            data.messages.forEach(msg => {
               if (msg.role !== 'system') {
                  addMessage(msg.content, msg.role === 'user');
               }
            });
         }
      }
   } catch (error) {
      console.log('No previous chat history');
   }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
   // Escape to minimize chat
   if (e.key === 'Escape') {
      const chatWidget = document.getElementById('chatWidget');
      if (!chatWidget.classList.contains('minimized')) {
         toggleChat();
      }
   }
});

// Handle visibility change (tab switching)
document.addEventListener('visibilitychange', () => {
   if (!document.hidden) {
      // Page became visible, could refresh data here
      console.log('Tab is now visible');
   }
});

// Export functions for use in HTML
window.sendMessage = sendMessage;
window.sendQuickMessage = sendQuickMessage;
window.handleKeyPress = handleKeyPress;
window.toggleChat = toggleChat;

