import { BotMessageSquare } from "lucide-react";
import React from "react";

const WelcomeCard = ({ setIsOpen }) => {
  const services = [
    {
      icon: "🤖",
      title: "AI Medical Assistant",
      description: "Get instant answers to your health questions powered by advanced AI",
      color: "#4ECDC4",
      bgColor: "#E0F7F5"
    },
    {
      icon: "🔬",
      title: "Symptom Analysis",
      description: "Describe symptoms and receive preliminary assessments",
      color: "#9B8FD9",
      bgColor: "#EDE7F6"
    },
    {
      icon: "📸",
      title: "Image Diagnosis",
      description: "Upload medical images for AI-powered analysis",
      color: "#F7A072",
      bgColor: "#FFF3E0"
    },
    {
      icon: "📅",
      title: "Easy Scheduling",
      description: "Book appointments with healthcare providers instantly",
      color: "#81C784",
      bgColor: "#E8F5E9"
    },
    {
      icon: "📚",
      title: "Medical Knowledge",
      description: "Access reliable medical information from trusted sources",
      color: "#64B5F6",
      bgColor: "#E3F2FD"
    },
    {
      icon: "💬",
      title: "24/7 Support",
      description: "Our AI assistant is always available to help you",
      color: "#FFB74D",
      bgColor: "#FFF8E1"
    }
  ];

  return (
    <div className="landing-section">
      {/* Hero Section */}
      <div className="hero-card neu-card">
        <div className="hero-badge">NEW</div>
        <div className="hero-content">
          <h1 className="hero-title">
            Your Personal
            <span className="highlight-text"> AI Health </span>
            Assistant
          </h1>
          <p className="hero-subtitle">
            Experience the future of healthcare. Get instant symptom analysis, 
            schedule appointments, and access reliable health information.
          </p>
          <button className="cta-button neu-button" onClick={() => setIsOpen(true)}>
              <span className="chat-icon" >Make Your first question <BotMessageSquare size={34}/> </span>
          </button>
        </div>
        <div className="hero-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      {/* Services Section */}
      <h2 className="section-title">
        <span className="title-decoration">★</span>
        Our Services
        <span className="title-decoration">★</span>
      </h2>
      
      <div className="services-grid">
        {services.map((service, index) => (
          <div 
            key={index} 
            className="service-card neu-card"
            style={{ 
              '--accent-color': service.color,
              '--accent-bg': service.bgColor
            }}
          >
            <div className="service-icon-wrapper" style={{ backgroundColor: service.bgColor }}>
              <span className="service-icon">{service.icon}</span>
            </div>
            <h3 className="service-title">{service.title}</h3>
            <p className="service-description">{service.description}</p>
            <div className="service-arrow">→</div>
          </div>
        ))}
      </div>

      {/* Stats Section */}
      <div className="stats-section">
        <div className="stat-card neu-card stat-pink">
          <span className="stat-number">10K+</span>
          <span className="stat-label">Patients Helped</span>
        </div>
        <div className="stat-card neu-card stat-blue">
          <span className="stat-number">98%</span>
          <span className="stat-label">Satisfaction</span>
        </div>
        <div className="stat-card neu-card stat-yellow">
          <span className="stat-number">24/7</span>
          <span className="stat-label">Available</span>
        </div>
        <div className="stat-card neu-card stat-green">
          <span className="stat-number">50+</span>
          <span className="stat-label">Conditions</span>
        </div>
      </div>
    </div>
  );
};

export default WelcomeCard;