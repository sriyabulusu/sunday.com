import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import or create these components
import AboutUs from './AboutUs';
import HowTo from './HowTo';
import Advice from './Advice';
import Confess from './Confess';
import MainContent from './MainContent';

//   <div className="app-content-mod">
//     {!showResults ? (
//       <>
//         <section className='calendar-section'>
//           <h2>Manage Calendar IDs</h2>
//           <form onSubmit={handleAddCalendarId} className="calendar-id-form">
//             <div className="input-wrapper">
//               <input
//                 type='text'
//                 value={newCalendarId}
//                 onChange={(e) => setNewCalendarId(e.target.value)}
//                 placeholder='Enter calendar ID (e.g. divineschedulerai@gmail.com)'
//                 className="calendar-id-input"
//                 id="calendar-id-input"
//                 name="calendar-id-input"
//               />
//               <button type='submit' className='add-button'>+</button>
//             </div>
//           </form>
//           <div className="calendar-id-list">
//             {calendarIds.map((id, index) => (
//               <div key={index} className="calendar-id-item">
//                 <span onClick={() => handleRemoveCalendarId(id)}>{id}</span>
//               </div>
//             ))}
//           </div>
//           {calendarIds.length > 0 && (
//             <div className="calendar-container">
//               <iframe
//                 src={sourceString}
//                 width='100%'
//                 height='70%'
//                 frameBorder='0'
//                 scrolling='no'
//                 title="Google Calendar"
//               ></iframe>
//             </div>
//           )}
//         </section>

//         <section className='questionnaire-section'>
//           <h2>Questionnaire</h2>
//           <form onSubmit={handleSubmit}>
//             <label htmlFor="day">
//               Which day are you trying to optimize your schedule for?
//               <input
//                 type='date'
//                 id="day"
//                 name='day'
//                 value={day}
//                 onChange={(e) => setDay(e.target.value)}
//                 required
//               />
//             </label>

//             <label htmlFor="wakeUpTime">
//               When do you wake up?
//               <input
//                 type='time'
//                 id="wakeUpTime"
//                 name='wakeUpTime'
//                 value={wakeUpTime}
//                 onChange={(e) => setWakeUpTime(e.target.value)}
//                 required
//               />
//             </label>

//             <label htmlFor="sleepTime">
//               When do you sleep?
//               <input
//                 type='time'
//                 id="sleepTime"
//                 name='sleepTime'
//                 value={sleepTime}
//                 onChange={(e) => setSleepTime(e.target.value)}
//                 required
//               />
//             </label>

//             <label htmlFor="productivityHours">
//               When are you most productive?
//               <input
//                 type='text'
//                 id="productivityHours"
//                 name='productivityHours'
//                 placeholder='e.g., 9 AM - 12 PM'
//                 value={productivityHours}
//                 onChange={(e) => setProductivityHours(e.target.value)}
//                 required
//               />
//             </label>

//             <label htmlFor="text">
//               What else do you need to get done?
//               <textarea
//                 id="text"
//                 name='text'
//                 value={text}
//                 onChange={(e) => setText(e.target.value)}
//                 required
//               />
//             </label>

//             <button 
//               type='submit' 
//               className='submit-button'
//               disabled={loading}
//             >
//               {loading ? (
//                 <div className="loading-spinner"></div>
//               ) : (
//                 'Submit'
//               )}
//             </button>
//           </form>
//           {error && <p className="error-message">{error}</p>}
//         </section>
//       </>
//     ) : (
//       <div className="results-page">
//         <section className='updated-calendar-section'>
//           <h2>Updated Calendar</h2>
//           <div className="calendar-container">
//             <iframe
//               src={sourceString}
//               width='100%'
//               height='70%'
//               frameBorder='0'
//               scrolling='no'
//               title="Updated Google Calendar"
//             ></iframe>
//           </div>
//         </section>
//         <section className='thinking-section'>
//           <h2>Thinking...</h2>
//           <div className="results-container">
//             <p>You got:</p>
//             <div className="badge">
//               <span className="badge-text">Lawyer</span>
//             </div>
//           </div>
//         </section>
//       </div>
//     )}
//   </div>
// };

const App = () => {
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

  const sourceString = `https://calendar.google.com/calendar/embed?height=600&wkst=2&ctz=America%2FLos_Angeles&bgcolor=%23f1f3ff&showTitle=0&showPrint=0&showTabs=0&showTz=0&mode=WEEK&${calendarIds
    .map(id => `src=${encodeURIComponent(id)}`)
    .join('&')}&color=%23039BE5&color=%2333B679&color=%237CB342&color=%230B8043`;

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
            <Link to="/how-to">How To</Link>
            {/* <Link to="/confess">Confess</Link> */}
            <a href="https://github.com/sriyabulusu/sunday.com" target="_blank" rel="noopener noreferrer">
              <img src={`/github-mark.svg`} className="github-icon" alt="GitHub" />
            </a>
          </nav>
        </header>

        <main className="app-content">
          <Routes>
            <Route path="/" element={<MainContent />} />
            <Route path="/about" element={<AboutUs />} />
            <Route path="/how-to" element={<HowTo />} />
            <Route path="/advice" element={<Advice />} />
            <Route path="/confess" element={<Confess />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;