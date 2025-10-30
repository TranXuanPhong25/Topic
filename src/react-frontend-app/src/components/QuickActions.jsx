import React from 'react';

const QuickActions = ({ onQuickMessage }) => {
  const quickMessages = [
    { text: '🕐 Hours', message: 'What are your hours?' },
    { text: '📍 Location', message: 'Where are you located?' },
    { text: '💳 Insurance', message: 'Do you accept insurance?' },
    { text: '📅 Book Appointment', message: 'I need to schedule an appointment' },
    { text: '🏥 Services', message: 'What services do you offer?' },
    { text: '💰 Pricing', message: 'How much does a visit cost?' }
  ];

  const handleClick = (message) => {
    if (onQuickMessage) {
      onQuickMessage(message);
    }
  };

  return (
    <div className="quick-actions">
      <h3>Quick Questions</h3>
      <div className="quick-buttons">
        {quickMessages.map((item, index) => (
          <button 
            key={index} 
            className="quick-btn" 
            onClick={() => handleClick(item.message)}
          >
            {item.text}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;