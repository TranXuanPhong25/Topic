import React from 'react';
import { quickMessages, imageActions, symptomTests } from '../constants/QuickMessages';

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

      <h3 style={{ marginTop: '20px' }}>Test Symptoms</h3>
      <div className="quick-buttons">
        {symptomTests.map((item, index) => (
          <button 
            key={`symptom-${index}`} 
            className="quick-btn quick-btn-symptom" 
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