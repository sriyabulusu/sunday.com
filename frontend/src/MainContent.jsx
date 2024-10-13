// MainContent.jsx
import React, { useState, useCallback } from 'react';
import './App.css'; // Create this file for MainContent-specific styles
import ReactMarkdown from 'react-markdown';


const MainContent = () => {
  // State variables
  const [day, setDay] = useState('');
  const [wakeUpTime, setWakeUpTime] = useState('');
  const [sleepTime, setSleepTime] = useState('');
  const [productivityHours, setProductivityHours] = useState('');
  const [text, setText] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [calendarIds, setCalendarIds] = useState([]);
  const [newCalendarId, setNewCalendarId] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);

    // Add new state variables
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('lawyer');

  // Add a function to handle sending messages
  const handleSendMessage = async () => {
    if (currentMessage.trim() === '') return;

    const newMessage = { text: currentMessage, sender: 'user' };
    setMessages(prevMessages => [...prevMessages, newMessage]);
    setCurrentMessage('');

    try {
      const response = await fetch('http://localhost:8000/query_chat_bot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentMessage, agent: selectedAgent, calendar_ids: calendarIds, date: day}),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prevMessages => [...prevMessages, { text: data.response, sender: 'bot' }]);
      } else {
        console.error('Failed to get response from chatbot');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Handlers
  const handleAddCalendarId = useCallback((e) => {
    e.preventDefault();
    if (newCalendarId && !calendarIds.includes(newCalendarId)) {
      setCalendarIds(prevIds => [...prevIds, newCalendarId]);
      setNewCalendarId('');
    }
  }, [newCalendarId, calendarIds]);

  const handleRemoveCalendarId = useCallback((id) => {
    setCalendarIds(prevIds => prevIds.filter(calendarId => calendarId !== id));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (calendarIds.length === 0 || !day || !wakeUpTime || !sleepTime || !productivityHours || !text) {
      setError('Please add a calendar ID and fill out all fields in the questionnaire.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = {
      day,
      wakeUpTime,
      sleepTime,
      productivityHours,
      text
    };

    const prompt = `
      Here are some things you need to know about me:
      - I wake up at ${formData.wakeUpTime} and sleep at ${formData.sleepTime}.
      - I am most productive during ${formData.productivityHours}.
      - I want to accomplish the following on ${formData.day}: ${formData.text}.
    `;

    const body = {
      questionnaire: prompt,
      calendar_ids: calendarIds,
      date: formData.day
    };

    try {
      const response = await fetch('http://localhost:8000/process_calendar_events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        throw new Error('Failed to submit form');
      }

      const data = await response.json();
      setResults(data);
      setShowResults(true);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to submit form. Please check your network connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Generate the calendar source string
  const sourceString = `https://calendar.google.com/calendar/embed?height=600&wkst=1&bgcolor=%23ffffff&ctz=America%2FLos_Angeles&showTitle=0&showNav=1&showDate=1&showPrint=0&showTabs=0&showCalendars=0&showTz=1&mode=WEEK&${calendarIds
    .map(id => `src=${encodeURIComponent(id)}`)
    .join('&')}&color=%234285F4&color=%23039BE5&color=%2333B679&color=%23D81B60`;

  return (
    <div className="app-content-mod">
      {!showResults ? (
        <>
          <section className="calendar-section">
            <h2>Manage Calendar IDs</h2>
            <form onSubmit={handleAddCalendarId} className="calendar-id-form">
              <div className="input-wrapper">
                <input
                  type="text"
                  value={newCalendarId}
                  onChange={(e) => setNewCalendarId(e.target.value)}
                  placeholder="Enter calendar ID (e.g. divineschedulerai@gmail.com)"
                  className="calendar-id-input"
                  id="calendar-id-input"
                  name="calendar-id-input"
                />
                <button type="submit" className="add-button">
                  +
                </button>
              </div>
            </form>
            <div className="calendar-id-list">
              {calendarIds.map((id, index) => (
                <div key={index} className="calendar-id-item">
                  <span onClick={() => handleRemoveCalendarId(id)}>{id}</span>
                </div>
              ))}
            </div>
            {calendarIds.length > 0 && (
              <div className="calendar-container">
                <iframe
                  src={sourceString}
                  width="100%"
                  height="70%"
                  frameBorder="0"
                  scrolling="no"
                  title="Google Calendar"
                ></iframe>
              </div>
            )}
          </section>

          <section className="questionnaire-section">
            <h2>Questionnaire</h2>
            <form onSubmit={handleSubmit}>
              <label htmlFor="day">
                Which day are you trying to optimize your schedule for?
                <input
                  type="date"
                  id="day"
                  name="day"
                  value={day}
                  onChange={(e) => setDay(e.target.value)}
                  required
                />
              </label>

              <label htmlFor="wakeUpTime">
                When do you wake up?
                <input
                  type="time"
                  id="wakeUpTime"
                  name="wakeUpTime"
                  value={wakeUpTime}
                  onChange={(e) => setWakeUpTime(e.target.value)}
                  required
                />
              </label>

              <label htmlFor="sleepTime">
                When do you sleep?
                <input
                  type="time"
                  id="sleepTime"
                  name="sleepTime"
                  value={sleepTime}
                  onChange={(e) => setSleepTime(e.target.value)}
                  required
                />
              </label>

              <label htmlFor="productivityHours">
                When are you most productive?
                <input
                  type="text"
                  id="productivityHours"
                  name="productivityHours"
                  placeholder="e.g., 9 AM - 12 PM"
                  value={productivityHours}
                  onChange={(e) => setProductivityHours(e.target.value)}
                  required
                />
              </label>

              <label htmlFor="text">
                What else do you need to get done?
                <textarea
                  id="text"
                  name="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  required
                />
              </label>

              <button type="submit" className="submit-button" disabled={loading}>
                {loading ? <div className="loading-spinner"></div> : 'Submit'}
              </button>
            </form>
            {error && <p className="error-message">{error}</p>}
          </section>
        </>
      ) : (
        <div className="results-page">
          <section className="updated-calendar-section">
            <h2>Updated Calendar</h2>
            <div className="calendar-container">
              <iframe
                src={sourceString}
                width="100%"
                height="70%"
                frameBorder="0"
                scrolling="no"
                title="Updated Google Calendar"
              ></iframe>
            </div>
          </section>
          <section className="chatbot-section">
            <h2>Talk to an Advisor!</h2>
            <div className="agent-selector">
              <select value={selectedAgent} onChange={(e) => setSelectedAgent(e.target.value)}>
                <option value="lawyer">Lawyer</option>
                <option value="philosopher">Philosopher</option>
                <option value="monk">Monk</option>
                <option value="productivity">Productivity Expert</option>
              </select>
            </div>
            <div className="chat-messages">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.sender}`}>
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>
              ))}
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message..."
              />
              <button onClick={handleSendMessage}>Send</button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
};

export default MainContent;
