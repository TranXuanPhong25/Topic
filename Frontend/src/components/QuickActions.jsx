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

      <h3 style={{ marginTop: '20px' }}>Symptom Tests (Agent Autonomy)</h3>
      
      {/* Group by category */}
      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          ✅ Basic (Simple Diagnosis)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'basic').map((item, index) => (
            <button 
              key={`symptom-basic-${index}`} 
              className="quick-btn quick-btn-symptom" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          🔬 Multi-Symptom (Extraction + Diagnosis)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'multi-symptom').map((item, index) => (
            <button 
              key={`symptom-multi-${index}`} 
              className="quick-btn quick-btn-symptom" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          🧪 Complex (Diagnosis + Investigation)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'complex').map((item, index) => (
            <button 
              key={`symptom-complex-${index}`} 
              className="quick-btn quick-btn-symptom" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#ff4444', marginBottom: '8px' }}>
          🚨 Emergency (Red Flag Detection)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'emergency').map((item, index) => (
            <button 
              key={`symptom-emergency-${index}`} 
              className="quick-btn quick-btn-emergency" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          ❓ Vague (Should Ask for Info)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'vague').map((item, index) => (
            <button 
              key={`symptom-vague-${index}`} 
              className="quick-btn quick-btn-vague" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button> 
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          💊 Recommendation Requests
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'recommendation').map((item, index) => (
            <button 
              key={`symptom-rec-${index}`} 
              className="quick-btn quick-btn-recommendation" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          🔄 Incomplete Info (Multi-turn)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'incomplete').map((item, index) => (
            <button 
              key={`symptom-incomplete-${index}`} 
              className="quick-btn quick-btn-incomplete" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          🇻🇳 Vietnamese Language
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'vietnamese').map((item, index) => (
            <button 
              key={`symptom-vn-${index}`} 
              className="quick-btn quick-btn-vietnamese" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          🔬 Investigation Focus
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'investigation').map((item, index) => (
            <button 
              key={`symptom-inv-${index}`} 
              className="quick-btn quick-btn-investigation" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
          🔀 Mixed Intent (Multi-agent)
        </h4>
        <div className="quick-buttons">
          {symptomTests.filter(t => t.category === 'mixed').map((item, index) => (
            <button 
              key={`symptom-mixed-${index}`} 
              className="quick-btn quick-btn-mixed" 
              onClick={() => handleClick(item.message)}
              title={item.message}
            >
              {item.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuickActions;