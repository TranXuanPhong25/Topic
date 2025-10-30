import React from 'react';

const WelcomeCard = () => {
  const features = [
    { icon: '📅', text: 'Schedule Appointments' },
    { icon: '❓', text: 'Answer Questions' },
    { icon: 'ℹ️', text: 'Clinic Information' },
    { icon: '💊', text: 'Services & Insurance' }
  ];

  return (
    <div className="welcome-card">
      <h2>Welcome! How can I help you today?</h2>
      <p>I can assist you with:</p>
      <div className="features">
        {features.map((feature, index) => (
          <div key={index} className="feature">
            <span className="icon">{feature.icon}</span>
            <span>{feature.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WelcomeCard;