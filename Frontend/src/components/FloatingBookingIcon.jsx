import React, { useState } from 'react';
import './FloatingBookingIcon.css';

const FloatingBookingIcon = ({ bookingComponent }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleBooking = () => {
    setIsOpen(!isOpen);
  };

  const closeBooking = () => {
    setIsOpen(false);
  };

  return (
    <>
      <div className="floating-booking-icon" onClick={toggleBooking}>
        <div className="booking-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 3H18V1H16V3H8V1H6V3H5C3.89 3 3.01 3.9 3.01 5L3 19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H12V12H7V10ZM7 14H17V16H7V14Z" fill="white"/>
          </svg>
        </div>
      </div>

      {isOpen && (
        <div className="booking-modal-overlay" onClick={closeBooking}>
          <div className="booking-modal" onClick={(e) => e.stopPropagation()}>
            <div className="booking-modal-header">
              <h3>Book an Appointment</h3>
              <button className="close-btn" onClick={closeBooking}>
                ×
              </button>
            </div>
            <div className="booking-modal-content">
              {bookingComponent}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingBookingIcon;