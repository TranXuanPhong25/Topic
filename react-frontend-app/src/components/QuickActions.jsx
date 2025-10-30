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

  const imageActions = [
    { 
      text: '📸 Vitiligo Sample', 
      imagePath: '/src/public/12419-vitiligo.jpg',
      message: 'Please analyze this vitiligo (bạch biến) image and provide diagnosis'
    },
    { 
      text: '📸 Jaundice Sample', 
      imagePath: '/src/public/350--trieu-chung-vang-da-la-dau-hieu-cua-nhung-benh-gi1_41181.jpg',
      message: 'My hand looks like this. What could be the issue?'
    }
  ];

  const symptomTests = [
    { 
      text: '🤒 Fever & Headache', 
      message: 'I have a high fever (39°C), severe headache, and body aches for 3 days. What could this be?'
    },
    { 
      text: '🤧 Cold Symptoms', 
      message: 'I have runny nose, sore throat, sneezing, and mild cough for 2 days. What should I do?'
    },
    { 
      text: '😷 COVID-19 Symptoms', 
      message: 'I have fever, dry cough, loss of taste and smell, and fatigue. Could this be COVID-19?'
    },
    { 
      text: '🤢 Nausea & Vomiting', 
      message: 'I have been experiencing nausea, vomiting, and diarrhea since last night. What might be the cause?'
    },
    { 
      text: '💔 Chest Pain', 
      message: 'I feel chest pain and shortness of breath when exercising. Should I be concerned?'
    },
    { 
      text: '🩸 Diabetes Symptoms', 
      message: 'I have excessive thirst, frequent urination, and unexplained weight loss. Could this be diabetes?'
    }
  ];

  const handleClick = (message) => {
    if (onQuickMessage) {
      onQuickMessage(message);
    }
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