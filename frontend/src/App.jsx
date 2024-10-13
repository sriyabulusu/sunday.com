// import React, { useState } from 'react';
// import './App.css';

// const App = () => {
//   const [formData, setFormData] = useState({
//     day: '',
//     wakeUpTime: '',
//     sleepTime: '',
//     productivityHours: '',
//   });

//   const handleChange = (e) => {
//     setFormData({
//       ...formData,
//       [e.target.name]: e.target.value,
//     });
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     console.log('Form submitted:', formData);
//   };

//   return (
//     <div className="app-container">
//       <header className="app-header">
//         <div className="logo">Sunday.com</div>
//         <nav>
//           <a href="#about">About Us</a>
//           <a href="#confess">Confess</a>
//           <a href="https://github.com" target="_blank" rel="noopener noreferrer">
//             <img src="/github-icon.svg" alt="GitHub" className="github-icon" />
//           </a>
//         </nav>
//       </header>

//       <main className="app-content">
//         <section className="calendar-section">
//           <div className="calendar-controls">
//             <button>&lt;</button>
//             <span>Sunday, Apr 5</span>
//             <button>&gt;</button>
//           </div>
//           <iframe 
//             src="https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=America%2FLos_Angeles&bgcolor=%23ffffff&showPrint=0&title=Schedule&mode=WEEK&showTabs=0&src=NTRkMzNiNWRhODVhYzg0OTYyN2NmNmQwYmYxYTdkMDllNWViOWFmZTQyZDZiZTI0YjNjNWU5YWRlMjc5Y2MzNUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%237CB342"
//             className="calendar-iframe"
//             title="Weekly Schedule"
//           ></iframe>
//         </section>

//         <section className="questionnaire-section">
//           <h2>Questionnaire</h2>
//           <form onSubmit={handleSubmit}>
//             <label>
//               Which day are you trying to optimize your schedule for?
//               <input
//                 type="date"
//                 name="day"
//                 value={formData.day}
//                 onChange={handleChange}
//                 required
//               />
//             </label>

//             <label>
//               When do you wake up?
//               <input
//                 type="time"
//                 name="wakeUpTime"
//                 value={formData.wakeUpTime}
//                 onChange={handleChange}
//                 required
//               />
//             </label>

//             <label>
//               When do you sleep?
//               <input
//                 type="time"
//                 name="sleepTime"
//                 value={formData.sleepTime}
//                 onChange={handleChange}
//                 required
//               />
//             </label>

//             <label>
//               When are you most productive?
//               <input
//                 type="text"
//                 name="productivityHours"
//                 placeholder="e.g., 9 AM - 12 PM"
//                 value={formData.productivityHours}
//                 onChange={handleChange}
//               />
//             </label>

//             <button type="submit" className="submit-button">Submit</button>
//           </form>
//         </section>
//       </main>

//       <footer className="app-footer">
//         <a href="#how-to">How to Page</a>
//       </footer>
//     </div>
//   );
// };

// export default App;

import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [formData, setFormData] = useState({
    day: '',
    wakeUpTime: '',
    sleepTime: '',
    productivityHours: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <img src="/sunday.svg" className="logo-icon" /> {/** alt="Sunday.com icon"*/} 
          <span className="logo-text">
            <span className="logo-sunday">sunday</span>
            <span className="logo-dot-com">.com</span>
          </span>
        </div>
        <nav>
          <a href="#about">About Us</a>
          <a href="#confess">Confess</a>
          <a href="https://github.com/sriyabulusu/sunday.com" target="_blank" rel="noopener noreferrer">
            <img src={`/github-mark.svg`} className="github-icon" />
          </a>
        </nav>
      </header>

      <main className="app-content">
        <section className="calendar-section">
          <iframe 
            src="https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=America%2FLos_Angeles&bgcolor=%23ffffff&showPrint=0&title=Schedule&mode=WEEK&showTabs=0&src=NTRkMzNiNWRhODVhYzg0OTYyN2NmNmQwYmYxYTdkMDllNWViOWFmZTQyZDZiZTI0YjNjNWU5YWRlMjc5Y2MzNUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%237CB342"
            className="calendar-iframe"
            title="Weekly Schedule"
          ></iframe>
        </section>

        <section className="questionnaire-section">
          <h2>Questionnaire</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Which day are you trying to optimize your schedule for?
              <input
                type="date"
                name="day"
                value={formData.day}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              When do you wake up?
              <input
                type="time"
                name="wakeUpTime"
                value={formData.wakeUpTime}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              When do you sleep?
              <input
                type="time"
                name="sleepTime"
                value={formData.sleepTime}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              When are you most productive?
              <input
                type="text"
                name="productivityHours"
                placeholder="e.g., 9 AM - 12 PM"
                value={formData.productivityHours}
                onChange={handleChange}
              />
            </label>

            <button type="submit" className="submit-button">Submit</button>
          </form>
        </section>
      </main>

      <footer className="app-footer">
        <a href="#how-to">How to Page</a>
      </footer>
    </div>
  );
};

export default App;