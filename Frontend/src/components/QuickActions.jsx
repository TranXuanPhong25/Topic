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
      message: 'My skin looks like this. What could be the diagnosis?'
    },
    { 
      text: '📸 Jaundice Sample', 
      imagePath: '/src/public/350--trieu-chung-vang-da-la-dau-hieu-cua-nhung-benh-gi1_41181.jpg',
      message: 'My hand looks like this. What could be the issue?'
    }
  ];

  const symptomTests = [
    // Basic single-symptom tests
    { 
      text: '🤒 Simple Fever', 
      message: 'I have a fever of 38.5°C for 2 days',
      category: 'basic'
    },
    { 
      text: '🤕 Just Headache', 
      message: 'I have a severe headache since this morning',
      category: 'basic'
    },
    
    // Multi-symptom tests (should trigger symptom extraction)
    { 
      text: '🤒 Fever + Headache', 
      message: 'I have a high fever (39°C), severe headache, and body aches for 3 days. What could this be?',
      category: 'multi-symptom'
    },
    { 
      text: '🤧 Cold Symptoms', 
      message: 'I have runny nose, sore throat, sneezing, and mild cough for 2 days',
      category: 'multi-symptom'
    },
    
    // Complex cases (should trigger diagnosis + investigation)
    { 
      text: '😷 COVID-like Symptoms', 
      message: 'I have fever 38°C, dry cough, loss of taste and smell, and fatigue for 4 days. Could this be COVID-19?',
      category: 'complex'
    },
    { 
      text: '🤢 Gastro Symptoms', 
      message: 'I have been experiencing nausea, vomiting, diarrhea, and abdominal pain since last night. Also feeling dizzy.',
      category: 'complex'
    },
    { 
      text: '🩸 Diabetes Indicators', 
      message: 'Excessive thirst, frequent urination, unexplained weight loss 5kg in 2 months, constant fatigue. Family history of diabetes.',
      category: 'complex'
    },
    
    // Emergency cases (should detect red flags)
    { 
      text: '💔 Chest Pain (Emergency)', 
      message: 'Đau ngực dữ dội lan ra cánh tay trái, ra mồ hôi lạnh, khó thở. Nam 55 tuổi.',
      category: 'emergency'
    },
    { 
      text: '🧠 Stroke Symptoms', 
      message: 'Sudden weakness on right side of body, difficulty speaking, facial drooping, severe headache. Started 30 minutes ago.',
      category: 'emergency'
    },
    { 
      text: '🚨 Severe Allergic Reaction', 
      message: 'Throat swelling, difficulty breathing, hives all over body, tongue feels thick after eating peanuts 10 minutes ago.',
      category: 'emergency'
    },
    
    // Vague symptoms (should ask for more info)
    { 
      text: '😕 Vague: Tired', 
      message: 'I feel tired all the time',
      category: 'vague'
    },
    { 
      text: '😕 Vague: Not Well', 
      message: 'I don\'t feel well',
      category: 'vague'
    },
    { 
      text: '😕 Vague: Pain', 
      message: 'I have some pain',
      category: 'vague'
    },
    
    // Tests for recommendation requests
    { 
      text: '💊 Ask Treatment', 
      message: 'I have the flu. What medication should I take?',
      category: 'recommendation'
    },
    { 
      text: '🏃 Ask Lifestyle Advice', 
      message: 'I was diagnosed with high blood pressure. What should I do?',
      category: 'recommendation'
    },
    
    // Multi-turn conversation tests
    { 
      text: '🔄 Incomplete Info', 
      message: 'I have fever and cough',
      category: 'incomplete'
    },
    { 
      text: '🔄 Needs Clarification', 
      message: 'My child is sick',
      category: 'incomplete'
    },
    
    // Vietnamese language tests
    { 
      text: '🇻🇳 Sốt & Ho', 
      message: 'Con tôi bị sốt 39 độ và ho nhiều từ 3 ngày nay. Con 5 tuổi.',
      category: 'vietnamese'
    },
    { 
      text: '🇻🇳 Đau Bụng', 
      message: 'Tôi bị đau bụng quặn thắt, buồn nôn, tiêu chảy từ tối qua. Ăn hải sản hôm qua.',
      category: 'vietnamese'
    },
    
    // Edge cases
    { 
      text: '🔬 Asks for Tests', 
      message: 'What blood tests should I get for my annual checkup?',
      category: 'investigation'
    },
    { 
      text: '📊 Has Test Results', 
      message: 'My blood sugar is 180 mg/dL fasting. What does this mean?',
      category: 'investigation'
    },
    
    // Mixed intent (symptom + appointment)
    { 
      text: '📅 Symptom + Appointment', 
      message: 'I have severe back pain for a week. Can I book an appointment for tomorrow?',
      category: 'mixed'
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