import React from "react";
import { BotMessageSquare, ArrowRight, Calendar, Activity, ShieldCheck, Clock, FileText, HeartPulse } from "lucide-react";
import "./WelcomeCard.css";

const WelcomeCard = ({ setIsOpen }) => {
  const features = [
    {
      icon: <Activity size={24} />,
      title: "Symptom Analysis",
      description: "Advanced AI algorithms to analyze your symptoms and provide preliminary assessments instantly.",
      color: "#E0F7F5",
      iconColor: "#4ECDC4"
    },
    {
      icon: <Calendar size={24} />,
      title: "Smart Scheduling",
      description: "Book appointments with the right specialists at times that work for you.",
      color: "#EDE7F6",
      iconColor: "#9B8FD9"
    },
    {
      icon: <FileText size={24} />,
      title: "Medical Records",
      description: "Securely store and access your medical history and prescriptions in one place.",
      color: "#FFF3E0",
      iconColor: "#F7A072"
    },
    {
      icon: <ShieldCheck size={24} />,
      title: "Data Privacy",
      description: "Enterprise-grade security ensuring your personal health data remains private and protected.",
      color: "#E8F5E9",
      iconColor: "#81C784"
    },
    {
      icon: <Clock size={24} />,
      title: "24/7 Availability",
      description: "Round-the-clock support for all your medical queries and emergency guidance.",
      color: "#E3F2FD",
      iconColor: "#64B5F6"
    },
    {
      icon: <HeartPulse size={24} />,
      title: "Health Monitoring",
      description: "Continuous tracking of your vitals and health metrics for proactive care.",
      color: "#FFF8E1",
      iconColor: "#FFB74D"
    }
  ];

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="badge">AI-Powered Healthcare</div>
          <h1 className="display-title">
            Your Personal <br />
            <span className="highlight">Medical Assistant</span>
          </h1>
          <p className="hero-text">
            Experience the future of healthcare with our advanced AI chatbot. 
            Get instant symptom analysis, schedule appointments, and manage your health journey 24/7.
          </p>
          <div className="cta-group">
            <button className="primary-btn" onClick={() => setIsOpen(true)}>
              Start Chatting <ArrowRight size={20} />
            </button>
            <button className="secondary-btn">Learn More</button>
          </div>
          <div className="trust-indicators">
            <div className="trust-item">
              <span className="trust-number">10k+</span>
              <span className="trust-label">Active Users</span>
            </div>
            <div className="trust-item">
              <span className="trust-number">99%</span>
              <span className="trust-label">Accuracy Rate</span>
            </div>
            <div className="trust-item">
              <span className="trust-number">24/7</span>
              <span className="trust-label">Support</span>
            </div>
          </div>
        </div>

        {/* Conversational UI Preview */}
        <div className="hero-visual">
          <div className="chat-preview-card">
            <div className="chat-header-preview">
              <div className="bot-avatar-preview">
                <BotMessageSquare size={24} color="#1a1a2e" />
              </div>
              <div className="bot-info-preview">
                <span className="name">Dr. AI Assistant</span>
                <span className="status">● Online Now</span>
              </div>
            </div>
            <div className="chat-body-preview">
              <div className="message-preview bot">
                Hello! I'm your AI medical assistant. How can I help you today?
              </div>
              <div className="message-preview user">
                I've been having a persistent headache for 2 days.
              </div>
              <div className="message-preview bot">
                I understand. On a scale of 1-10, how severe is the pain? And do you have any other symptoms?
              </div>
              <div className="typing-indicator-preview">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          
          {/* Floating Elements */}
          <div className="floating-card card-1">
            <Calendar size={20} color="#1a1a2e" />
            <span>Easy Scheduling</span>
          </div>
          <div className="floating-card card-2">
            <Activity size={20} color="#1a1a2e" />
            <span>Symptom Check</span>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <div className="section-header">
          <h2>Why Choose Us</h2>
          <p>Comprehensive healthcare support at your fingertips</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div 
                className="feature-icon"
                style={{ backgroundColor: feature.color, color: feature.iconColor, borderColor: feature.iconColor }}
              >
                {feature.icon}
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeCard;
