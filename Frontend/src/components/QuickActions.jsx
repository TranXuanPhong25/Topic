import React from 'react';
import { quickMessages, imageActions, symptomTests, appointmentTests, documentRetrievalTests } from '../constants/QuickMessages';

// Category labels for image actions
const imageCategoryLabels = {
  'medical': '🩺 Medical Images',
  'document': '📄 Document Images',
  'general': '🖼️ General Images (Non-medical)'
};

// Category labels for document retrieval
const docRetrievalCategoryLabels = {
  'disease-info': '📖 Disease Information',
  'treatment': '💊 Treatment Queries',
  'symptom-query': '🔍 Symptom-Based Queries',
  'prevention': '🛡️ Preventive Care',
  'dermatology': '🩺 Dermatology (Skin)'
};

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

  // Group images by category
  const imagesByCategory = imageActions.reduce((acc, item) => {
    const category = item.category || 'other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});

  // Group document retrieval tests by category
  const docRetrievalByCategory = documentRetrievalTests.reduce((acc, item) => {
    const category = item.category || 'other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});

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
      
      <h3 style={{ marginTop: '20px' }}>📷 Sample Images ({imageActions.length} tests)</h3>
      <p style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
        Test image classification: medical, document, or general photos
      </p>
      
      {/* Image actions grouped by category */}
      {Object.entries(imagesByCategory).map(([category, items]) => (
        <div key={`img-cat-${category}`} style={{ marginBottom: '15px' }}>
          <h4 style={{ 
            fontSize: '13px', 
            color: category === 'medical' ? '#28a745' : category === 'document' ? '#17a2b8' : '#6c757d',
            marginTop: '10px', 
            marginBottom: '8px'
          }}>
            {imageCategoryLabels[category] || category} ({items.length})
          </h4>
          <div className="quick-buttons">
            {items.map((item, index) => (
              <button 
                key={`img-${category}-${index}`} 
                className={`quick-btn quick-btn-image quick-btn-img-${category}`}
                onClick={() => handleImageClick(item)}
                style={{ 
                  borderLeft: `3px solid ${category === 'medical' ? '#28a745' : category === 'document' ? '#17a2b8' : '#6c757d'}`,
                  backgroundColor: category === 'medical' ? '#f0fff0' : category === 'document' ? '#f0f8ff' : '#f8f9fa'
                }}
              >
                {item.text}
              </button>
            ))}
          </div>
        </div>
      ))}

      <h3 style={{ marginTop: '25px' }}>📚 Document Retrieval Tests ({documentRetrievalTests.length} tests)</h3>
      <p style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
        Test RAG pipeline for medical knowledge retrieval
      </p>
      
      {/* Document retrieval tests grouped by category */}
      {Object.entries(docRetrievalByCategory).map(([category, items]) => (
        <div key={`doc-${category}`} style={{ marginBottom: '15px' }}>
          <h4 style={{ 
            fontSize: '13px', 
            color: '#9c27b0',
            marginTop: '10px', 
            marginBottom: '8px'
          }}>
            {docRetrievalCategoryLabels[category] || category} ({items.length})
          </h4>
          <div className="quick-buttons">
            {items.map((item, index) => (
              <button 
                key={`doc-${category}-${index}`} 
                className={`quick-btn quick-btn-doc-retrieval quick-btn-${category}`}
                onClick={() => handleClick(item.message)}
                style={{ 
                  borderLeft: '3px solid #9c27b0',
                  backgroundColor: '#f3e5f5'
                }}
              >
                {item.text}
              </button>
            ))}
          </div>
        </div>
      ))}

      <h3 style={{ marginTop: '25px' }}>📅 Test Appointments ({appointmentTests.length} tests)</h3>
      
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