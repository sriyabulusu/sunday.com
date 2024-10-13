import React from 'react';
import './App.css';

const Calendar = ({ formData, handleChange, handleSubmit }) => {
  // const history = useHistory();

  // const onSubmit = (e) => {
  //   handleSubmit(e, history);
  // };

  return (
    <div>
      <section className="calendar-section">
        <iframe 
          src="https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=America%2FLos_Angeles&bgcolor=%23ffffff&showPrint=0&title=Schedule&mode=WEEK&showTabs=0&src=NTRkMzNiNWRhODVhYzg0OTYyN2NmNmQwYmYxYTdkMDllNWViOWFmZTQyZDZiZTI0YjNjNWU5YWRlMjc5Y2MzNUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%237CB342"
          className="calendar-iframe"
          title="Weekly Schedule"
        ></iframe>
      </section>

      <section className="questionnaire-section">
        <h2>Questionnaire</h2>
        <form onSubmit={true}>
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
    </div>
  );
};

export default Calendar;