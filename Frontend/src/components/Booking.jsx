import React, { useState, useEffect } from 'react';
import './Booking.css';

const Booking = () => {
  const [patientName, setPatientName] = useState('');
  const [reason, setReason] = useState('');
  const [time, setTime] = useState('');
  const [phone, setPhone] = useState('');
  const [bookings, setBookings] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load bookings from localStorage on component mount
  useEffect(() => {
    const savedBookings = localStorage.getItem('appointments');
    if (savedBookings) {
      setBookings(JSON.parse(savedBookings));
    }
  }, []);

  // Save bookings to localStorage whenever bookings change
  useEffect(() => {
    localStorage.setItem('appointments', JSON.stringify(bookings));
  }, [bookings]);

  const handleCreateBooking = (e) => {
    e.preventDefault();

    // Validate inputs
    if (!patientName.trim() || !reason.trim() || !time || !phone.trim()) {
      alert('Please fill in all fields');
      return;
    }

    // Create new booking
    const newBooking = {
      id: Date.now().toString(), // Using timestamp as ID since we're using localStorage
      patient_name: patientName.trim(),
      reason: reason.trim(),
      time: time,
      phone: phone.trim(),
      createdAt: new Date().toISOString()
    };

    // Add to bookings array
    setBookings(prevBookings => [...prevBookings, newBooking]);

    // Reset form
    setPatientName('');
    setReason('');
    setTime('');
    setPhone('');

    // Show success message
    alert('Booking created successfully!');
  };

  const handleDeleteBooking = (id) => {
    if (window.confirm('Are you sure you want to delete this booking?')) {
      setBookings(prevBookings => prevBookings.filter(booking => booking.id !== id));
    }
  };

  const handleClearAllBookings = () => {
    if (window.confirm('Are you sure you want to clear all bookings?')) {
      setBookings([]);
    }
  };

  return (
    <div className="booking-container">
      <form className="booking-form" onSubmit={handleCreateBooking}>
        <div className="form-group">
          <label htmlFor="patientName">Patient Name *</label>
          <input
            type="text"
            id="patientName"
            value={patientName}
            onChange={(e) => setPatientName(e.target.value)}
            placeholder="Enter patient name"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reason">Reason for Visit *</label>
          <textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Describe the reason for your visit"
            required
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="time">Preferred Time *</label>
          <input
            type="datetime-local"
            id="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="phone">Phone Number *</label>
          <input
            type="tel"
            id="phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Enter phone number"
            required
          />
        </div>

        <button type="submit" className="submit-btn">
          Book Appointment
        </button>
      </form>

      <div className="booking-actions">
        <button
          className={`history-toggle-btn ${showHistory ? 'active' : ''}`}
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? 'Hide' : 'Show'} Booking History ({bookings.length})
        </button>

        {bookings.length > 0 && (
          <button
            className="clear-btn"
            onClick={handleClearAllBookings}
          >
            Clear All Bookings
          </button>
        )}
      </div>

      {showHistory && (
        <div className="booking-history">
          <h3>Appointment History</h3>

          {bookings.length === 0 ? (
            <p className="no-bookings">No bookings found. Create your first appointment!</p>
          ) : (
            <div className="bookings-list">
              {bookings.map((booking) => (
                <div key={booking.id} className="booking-item">
                  <div className="booking-details">
                    <div className="booking-info">
                      <strong>Patient:</strong> {booking.patient_name}
                    </div>
                    <div className="booking-info">
                      <strong>Reason:</strong> {booking.reason}
                    </div>
                    <div className="booking-info">
                      <strong>Time:</strong> {new Date(booking.time).toLocaleString()}
                    </div>
                    <div className="booking-info">
                      <strong>Phone:</strong> {booking.phone}
                    </div>
                    <div className="booking-info">
                      <strong>Booked:</strong> {new Date(booking.createdAt).toLocaleString()}
                    </div>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteBooking(booking.id)}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Booking;