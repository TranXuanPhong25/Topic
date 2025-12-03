import React, { useState, useEffect, useRef } from 'react';
import './Booking.css';

const API_BASE_URL = 'http://localhost:8000/appointments';

const Booking = () => {
  const [patientName, setPatientName] = useState('');
  const [reason, setReason] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [phone, setPhone] = useState('');
  const [bookings, setBookings] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Track if data was loaded from API to prevent localStorage overwrite on F5
  const isInitialLoad = useRef(true);

  // Load bookings from API on component mount
  useEffect(() => {
    fetchBookings();
  }, []);

  // Only save to localStorage after user actions, not initial load
  useEffect(() => {
    if (!isInitialLoad.current && bookings.length >= 0) {
      localStorage.setItem('appointments', JSON.stringify(bookings));
    }
  }, [bookings]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/list`);
      
      if (response.ok) {
        const data = await response.json();
        setBookings(data);
        isInitialLoad.current = false; // Mark initial load as complete
      } else {
        // Fallback to localStorage if API fails
        const savedBookings = localStorage.getItem('appointments');
        if (savedBookings) {
          setBookings(JSON.parse(savedBookings));
        }
        isInitialLoad.current = false;
      }
    } catch (err) {
      console.error('Failed to fetch bookings:', err);
      // Fallback to localStorage
      const savedBookings = localStorage.getItem('appointments');
      if (savedBookings) {
        setBookings(JSON.parse(savedBookings));
      }
      isInitialLoad.current = false;
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBooking = async (e) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    if (!patientName.trim() || !reason.trim() || !date || !time || !phone.trim()) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_name: patientName.trim(),
          reason: reason.trim(),
          date: date,
          time: time,
          phone: phone.trim(),
        }),
      });

      if (response.ok) {
        const newBooking = await response.json();
        setBookings(prevBookings => [...prevBookings, newBooking]);
        
        // Reset form
        setPatientName('');
        setReason('');
        setDate('');
        setTime('');
        setPhone('');
        
        alert('Booking created successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create booking');
      }
    } catch (err) {
      console.error('Failed to create booking:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBooking = async (id) => {
    if (!window.confirm('Are you sure you want to delete this booking?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setBookings(prevBookings => prevBookings.filter(booking => booking.id !== id));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete booking');
      }
    } catch (err) {
      console.error('Failed to delete booking:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearAllBookings = async () => {
    if (!window.confirm('Are you sure you want to clear all bookings?')) {
      return;
    }

    try {
      setLoading(true);
      // Delete all bookings one by one
      for (const booking of bookings) {
        await fetch(`${API_BASE_URL}/${booking.id}`, { method: 'DELETE' });
      }
      setBookings([]);
      localStorage.removeItem('appointments');
    } catch (err) {
      console.error('Failed to clear bookings:', err);
      setError('Failed to clear some bookings. Please refresh.');
    } finally {
      setLoading(false);
    }
  };

  // Generate time slots (9:00 - 17:00, 15-minute intervals)
  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 9; hour < 17; hour++) {
      for (let minute = 0; minute < 60; minute += 15) {
        const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        slots.push(timeStr);
      }
    }
    return slots;
  };

  return (
    <div className="booking-container">
      {error && <div className="error-message">{error}</div>}
      
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
            disabled={loading}
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
            disabled={loading}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="date">Date *</label>
            <input
              type="date"
              id="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="time">Time *</label>
            <select
              id="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              required
              disabled={loading}
            >
              <option value="">Select time</option>
              {generateTimeSlots().map(slot => (
                <option key={slot} value={slot}>{slot}</option>
              ))}
            </select>
          </div>
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
            disabled={loading}
          />
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Processing...' : 'Book Appointment'}
        </button>
      </form>

      <div className="booking-actions">
        <button
          className={`history-toggle-btn ${showHistory ? 'active' : ''}`}
          onClick={() => setShowHistory(!showHistory)}
          disabled={loading}
        >
          {showHistory ? 'Hide' : 'Show'} Booking History ({bookings.length})
        </button>

        {bookings.length > 0 && (
          <button
            className="clear-btn"
            onClick={handleClearAllBookings}
            disabled={loading}
          >
            Clear All Bookings
          </button>
        )}
      </div>

      {showHistory && (
        <div className="booking-history">
          <h3>Appointment History</h3>

          {loading ? (
            <p className="loading">Loading...</p>
          ) : bookings.length === 0 ? (
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
                      <strong>Date:</strong> {booking.date}
                    </div>
                    <div className="booking-info">
                      <strong>Time:</strong> {booking.time}
                    </div>
                    <div className="booking-info">
                      <strong>Phone:</strong> {booking.phone}
                    </div>
                    {booking.provider && (
                      <div className="booking-info">
                        <strong>Provider:</strong> {booking.provider}
                      </div>
                    )}
                    <div className="booking-info">
                      <strong>Status:</strong> 
                      <span className={`status-badge ${booking.status}`}>
                        {booking.status || 'scheduled'}
                      </span>
                    </div>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteBooking(booking.id)}
                    disabled={loading}
                  >
                    Cancel
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