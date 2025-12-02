import React from 'react';
import { quickMessages, imageActions, symptomTests, appointmentTests } from '../constants/QuickMessages';

const QuickActions = ({ onQuickMessage, setIsOpen }) => {
  const handleClick = (message) => {
    if (onQuickMessage) {
      onQuickMessage(message);
    }
    setIsOpen(true);
  };

  const handleImageClick = async (imageAction) => {
    try {
      // Fetch the image file
      const response = await fetch(imageAction.imagePath);
      const blob = await response.blob();
      
      // Convert to base64
      const reader = new FileReader();
      reader.onload = () => {
        const imageData = reader.result;
        // Send image with message to parent
        if (onQuickMessage) {
          onQuickMessage(imageAction.message, imageData);
        }
      };
      reader.readAsDataURL(blob);

      setIsOpen(true);
    } catch (error) {
      console.error('Error loading image:', error);
      alert('Failed to load image. Please try again.');
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
      
      <h3 style={{ marginTop: '20px' }}>Sample Images</h3>
      <div className="quick-buttons">
        {imageActions.map((item, index) => (
          <button 
            key={`img-${index}`} 
            className="quick-btn quick-btn-image" 
            onClick={() => handleImageClick(item)}
          >
            {item.text}
          </button>
        ))}
      </div>

      <h3 style={{ marginTop: '20px' }}>Test Appointments ({appointmentTests.length} tests)</h3>
      
      {/* Appointment tests grouped by category */}
      {Object.entries(
        appointmentTests.reduce((acc, item) => {
          const category = item.category || 'other';
          if (!acc[category]) acc[category] = [];
          acc[category].push(item);
          return acc;
        }, {})
      ).map(([category, items]) => (
        <div key={`appt-${category}`} style={{ marginBottom: '20px' }}>
          <h4 style={{ 
            fontSize: '14px', 
            color: '#0066cc', 
            marginTop: '15px', 
            marginBottom: '10px',
            textTransform: 'capitalize'
          }}>
            📅 {category.replace('-', ' ')} ({items.length})
          </h4>
          <div className="quick-buttons">
            {items.map((item, index) => (
              <button 
                key={`appt-${category}-${index}`} 
                className={`quick-btn quick-btn-appointment quick-btn-${category}`}
                onClick={() => handleClick(item.message)}
                style={{ 
                  borderLeft: '3px solid #0066cc',
                  backgroundColor: '#f0f8ff'
                }}
              >
                {item.text}
              </button>
            ))}
          </div>
        </div>
      ))}

      <h3 style={{ marginTop: '20px' }}>Test Symptoms ({symptomTests.length} tests)</h3>
      
      {/* Symptom tests grouped by category */}
      {Object.entries(
        symptomTests.reduce((acc, item) => {
          const category = item.category || 'other';
          if (!acc[category]) acc[category] = [];
          acc[category].push(item);
          return acc;
        }, {})
      ).map(([category, items]) => (
        <div key={`symptom-${category}`} style={{ marginBottom: '20px' }}>
          <h4 style={{ 
            fontSize: '14px', 
            color: '#666', 
            marginTop: '15px', 
            marginBottom: '10px',
            textTransform: 'capitalize'
          }}>
            {category.replace('-', ' ')} ({items.length})
          </h4>
          <div className="quick-buttons">
            {items.map((item, index) => (
              <button 
                key={`symptom-${category}-${index}`} 
                className={`quick-btn quick-btn-symptom quick-btn-${category}`}
                onClick={() => handleClick(item.message)}
              >
                {item.text}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default QuickActions;