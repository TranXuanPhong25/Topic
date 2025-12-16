import React, { useState } from 'react';
import './SuccessDialog.css';

const SuccessDialog = ({ isOpen, onClose, appointmentId }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(appointmentId);
    setCopied(true);
   //  setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="success-dialog-overlay" onClick={onClose}>
      <div className="success-dialog-container" onClick={(e) => e.stopPropagation()}>
        <div className="success-dialog-header">
          <h3>Booking Created Successfully!</h3>
        </div>
        <div className="success-dialog-body">
          <p className="success-message">Your appointment has been scheduled.</p>
          
          <div className="appointment-id-section">
            <p className="important-label">IMPORTANT: Save your Appointment ID</p>
            <div className="id-display">
              <code className="appointment-id">{appointmentId}</code>
              <button 
                className={`copy-btn ${copied ? 'copied' : ''}`}
                onClick={handleCopy}
              >
                {copied ? '✓ Copied!' : 'Copy'}
              </button>
            </div>
            <p className="id-note">
              You will need this ID to reschedule or cancel your appointment.
              Please save it now!
            </p>
          </div>
        </div>
        <div className="success-dialog-footer">
          <button className="success-dialog-btn" onClick={onClose}>
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};

export default SuccessDialog;
