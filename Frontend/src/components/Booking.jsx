import React, { useState, useEffect, useRef } from 'react';
import './Booking.css';
import Dialog from './Dialog';
import SuccessDialog from './SuccessDialog';

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
  const [showAll, setShowAll] = useState(false); // Track if showing all appointments from API

  // Dialog states
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [newAppointmentId, setNewAppointmentId] = useState('');
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleteBookingId, setDeleteBookingId] = useState('');
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [savedBookingsLoaded, setSavedBookingsLoaded] = useState(false);
  // Load bookings from localStorage on mount
  useEffect(() => {
    const savedBookings = localStorage.getItem('appointments');
    if (savedBookings) {
      try {
        setBookings(JSON.parse(savedBookings));
      } catch (err) {
        console.error('Error parsing saved appointments:', err);
        setBookings([]);
      }
    }
    setSavedBookingsLoaded(true);
  }, []);

  // Save bookings to localStorage whenever they change
  useEffect(() => {
    if (!savedBookingsLoaded || showAll) return;
    if (bookings.length >= 0) {
      localStorage.setItem('appointments', JSON.stringify(bookings));
    }
  }, [bookings, savedBookingsLoaded, showAll]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`${API_BASE_URL}/list`);
      await new Promise(resolve => setTimeout(resolve, 400)); // Allow loading state to render

      if (response.ok) {
        const data = await response.json();
        setBookings(data);
        setShowAll(true); // Mark as showing all appointments
        setShowHistory(true); // Auto-show history when loading all
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch appointments');
      }
    } catch (err) {
      console.error('Failed to fetch bookings:', err);
      setError('Network error. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleShowLocalOnly = () => {
    // Reload from localStorage
    const savedBookings = localStorage.getItem('appointments');
    if (savedBookings) {
      try {
        setBookings(JSON.parse(savedBookings));
        console.log(savedBookings)
        setShowAll(false);
      } catch (err) {
        console.error('Error parsing saved appointments:', err);
        setBookings([]);
      }
    } else {
      setBookings([]);
      setShowAll(false);
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

        // Add to localStorage (not from API)
        setBookings(prevBookings => [...prevBookings, newBooking]);

        // Reset form
        setPatientName('');
        setReason('');
        setDate('');
        setTime('');
        setPhone('');

        // Show success dialog with appointment ID
        setNewAppointmentId(newBooking.id);
        setShowSuccessDialog(true);
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
    setDeleteBookingId(id);
    setShowDeleteDialog(true);
  };

  const confirmDeleteBooking = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/${deleteBookingId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove from localStorage
        setBookings(prevBookings => prevBookings.filter(booking => booking.id !== deleteBookingId));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to cancel booking');
      }
    } catch (err) {
      console.error('Failed to cancel booking:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
      setDeleteBookingId('');
    }
  };

  const handleClearAllBookings = () => {
    setShowClearDialog(true);
  };

  const confirmClearAllBookings = () => {
    // Just clear localStorage (not API)
    setBookings([]);
    localStorage.removeItem('appointments');
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

        <button
          className={`show-all-btn ${showAll ? 'active' : ''}`}
          onClick={showAll ? handleShowLocalOnly : fetchBookings}
          disabled={loading}
        >
          {showAll ? 'Show Local Only' : 'Show All Appointments'}
        </button>

      </div>

      {showHistory && (
        <div className="booking-history">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Appointment History {showAll && <span className="source-badge">Database</span>}{!showAll && <span className="source-badge">Local</span>}</h3>
            {bookings.length > 0 && (
              <button
                className="clear-btn"
                onClick={handleClearAllBookings}
                disabled={loading}
              >
                Clear All
              </button>
            )}
          </div>
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
                      <strong>ID:</strong> <code>{booking.id}</code>
                    </div>
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

      {/* Success Dialog for new appointment */}
      <SuccessDialog
        isOpen={showSuccessDialog}
        onClose={() => setShowSuccessDialog(false)}
        appointmentId={newAppointmentId}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        isOpen={showDeleteDialog}
        onClose={() => {
          setShowDeleteDialog(false);
          setDeleteBookingId('');
        }}
        onConfirm={confirmDeleteBooking}
        title="Cancel Appointment"
        message="Are you sure you want to cancel this booking? This action cannot be undone."
        type="danger"
        confirmText="Yes, Cancel"
        cancelText="No, Keep It"
      />

      {/* Clear All Confirmation Dialog */}
      <Dialog
        isOpen={showClearDialog}
        onClose={() => setShowClearDialog(false)}
        onConfirm={confirmClearAllBookings}
        title="Clear All Bookings"
        message="Are you sure you want to clear all bookings from your local history? This will only remove them from your browser storage, not from the server."
        type="warning"
        confirmText="Yes, Clear All"
        cancelText="Cancel"
      />
    </div>
  );
};

export default Booking;