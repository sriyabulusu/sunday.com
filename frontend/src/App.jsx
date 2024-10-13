import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import or create these components
import AboutUs from './AboutUs';
import HowTo from './HowTo';
import Advice from './Advice';
import Confess from './Confess';

const App = () => {
  const [formData, setFormData] = useState({
    day: '',
    wakeUpTime: '',
    sleepTime: '',
    productivityHours: '',
    text: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [calendarIds, setCalendarIds] = useState([])
  const [newCalendarId, setNewCalendarId] = useState('')

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = e => {
    e.preventDefault()
    console.log('Form submitted:', formData)
    console.log('Calendars:', calendarIds)

    setLoading(true)
    setError(null)

    // post request to localhost:8000/prompt with the following body:
    /**
     * metadata = {
        "date": request.date,
        "time_wake": request.time_wake,
        "time_sleep": request.time_sleep,
        "most_productive": request.most_productive,
        "todo": request.todo,
    }
     */

    const body = {
      date: formData.day,
      time_wake: formData.wakeUpTime,
      time_sleep: formData.sleepTime,
      most_productive: formData.productivityHours,
      calendar_ids: calendarIds,
      todo: formData.text
    }

    fetch('http://localhost:8000/prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to submit form')
        }
        return response.json()
      })
      .then(data => {
        console.log('Success:', data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error:', error)
        setError(error)
        setLoading(false)
      })
  }

  const handleAddCalendarId = e => {
    e.preventDefault()
    if (newCalendarId && !calendarIds.includes(newCalendarId)) {
      setCalendarIds([...calendarIds, newCalendarId])
      setNewCalendarId('')
    }
  }

  const handleRemoveCalendarId = id => {
    setCalendarIds(calendarIds.filter(calendarId => calendarId !== id))
  }

  const sourceString = `https://calendar.google.com/calendar/embed?height=600&wkst=2&ctz=America%2FLos_Angeles&bgcolor=%23ffffff&mode=WEEK&${calendarIds
    .map(id => `src=${encodeURIComponent(id)}`)
    .join('&')}&color=%23039BE5&color=%2333B679&color=%237CB342&color=%230B8043`

  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <div className="logo-container">
            <Link className="home-link" to="/">
              <img src="/sunday-logo.svg" className="logo-icon" alt="Sunday.com icon" />
              <span className="logo-text">
                <span className="logo-sunday">sunday</span>
                <span className="logo-dot-com">.com</span>
              </span>
            </Link>
          </div>
          <nav>
            <Link to="/about">About Us</Link>
            <Link to="/confess">Confess</Link>
            <a href="https://github.com/sriyabulusu/sunday.com" target="_blank" rel="noopener noreferrer">
              <img src={`/github-mark.svg`} className="github-icon" alt="GitHub" />
            </a>
          </nav>
        </header>

        <main className="app-content">
          <Routes>
            <Route path="/" element={
              <div className="app-content-mod">
                <section className='calendar-section'>
                  <h2>Manage Calendar IDs</h2>
                  <form onSubmit={handleAddCalendarId}>
                    <input
                      type='text'
                      value={newCalendarId}
                      onChange={e => setNewCalendarId(e.target.value)}
                      placeholder='Enter calendar ID'
                    />
                    <button type='submit' className='submit-button'>Add Calendar</button>
                  </form>
                  <ul>
                    {calendarIds.map((id, index) => (
                      <li key={index}>
                        {id}
                    <button onClick={() => handleRemoveCalendarId(id)}>
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
              {calendarIds.length > 0 && (
                <iframe
                  src={sourceString}
                  width='800'
                  height='600'
                  frameBorder='0'
                  scrolling='no'
                  title='Google Calendar'
                ></iframe>
              )}
            </section>
    
            <section className='questionnaire-section'>
              <h2>Questionnaire</h2>
              <form onSubmit={handleSubmit}>
                <label>
                  Which day are you trying to optimize your schedule for?
                  <input
                    type='date'
                    name='day'
                    value={formData.day}
                    onChange={handleChange}
                    required
                  />
                </label>
    
                <label>
                  When do you wake up?
                  <input
                    type='time'
                    name='wakeUpTime'
                    value={formData.wakeUpTime}
                    onChange={handleChange}
                    required
                  />
                </label>
    
                <label>
                  When do you sleep?
                  <input
                    type='time'
                    name='sleepTime'
                    value={formData.sleepTime}
                    onChange={handleChange}
                    required
                  />
                </label>
    
                <label>
                  When are you most productive?
                  <input
                    type='text'
                    name='productivityHours'
                    placeholder='e.g., 9 AM - 12 PM'
                    value={formData.productivityHours}
                    onChange={handleChange}
                  />
                </label>
    
                <label>
                  What else do you need to get done?
                  <textarea
                    name='text'
                    value={formData.text}
                    onChange={handleChange}
                  />
                </label>
    
                <button type='submit' className='submit-button'>
                  Submit
                </button>
              </form>
            </section>

            </div>} />
            <Route path="/about" element={<AboutUs />} />
            <Route path="/how-to" element={<HowTo />} />
            <Route path="/advice" element={<Advice />} />
            <Route path="/confess" element={<Confess />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <Link to="/how-to">How to Page</Link>
        </footer>
      </div>
    </Router>
  );
};

export default App
