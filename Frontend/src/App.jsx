import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import WelcomeCard from './components/WelcomeCard';
import ChatWidget from './components/ChatWidget';
import Booking from './components/Booking';
import FloatingBookingIcon from './components/FloatingBookingIcon';

const App = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId] = useState(() => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36);
  });

  const chatWidgetRef = useRef();

  // Lock body scroll when chat widget is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    // Cleanup on unmount
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleQuickMessage = (message, imageData = null) => {
    if (chatWidgetRef.current && chatWidgetRef.current.sendMessage) {
      chatWidgetRef.current.sendMessage(message, imageData);
    }
  };

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <div className="container">
          <WelcomeCard setIsOpen={setIsOpen} />
          <ChatWidget
            onQuickMessage={handleQuickMessage}
            ref={chatWidgetRef}
            sessionId={sessionId}
            isOpen={isOpen}
            setIsOpen={setIsOpen}
          />
        </div>
      </main>
      <FloatingBookingIcon bookingComponent={<Booking />} />
    </div>
  );
};

export default App;