import React, { useState, useRef } from 'react';
import './App.css';
import Header from './components/Header';
import WelcomeCard from './components/WelcomeCard';
import QuickActions from './components/QuickActions';
import ChatWidget from './components/ChatWidget';
import Footer from './components/Footer';

const App = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId] = useState(() => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  });
  
  const chatWidgetRef = useRef();

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
          <WelcomeCard />
          <QuickActions onQuickMessage={handleQuickMessage} setIsOpen={setIsOpen} />
          <ChatWidget 
            onQuickMessage={handleQuickMessage} 
            ref={chatWidgetRef} 
            sessionId={sessionId} 
            isOpen={isOpen} 
            setIsOpen={setIsOpen} 
          />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default App;