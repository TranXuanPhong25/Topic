import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <p>&copy; 2025 Happy Health Clinic. All rights reserved.</p>
        <p className="footer-note">
          <strong>Emergency?</strong> Call 115 immediately.
          This chatbot is for general information and appointment scheduling only.
        </p>
        <p className="contact-info">
          📞 (555) 123-4567 | 📍 123 Main Street, Anytown, USA | 🕐 Mon-Fri 9AM-5PM, Sat 9AM-12PM
        </p>
      </div>
    </footer>
  );
};

export default Footer;