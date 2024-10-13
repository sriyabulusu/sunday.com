import React, { useState } from 'react'
import './App.css'

const App = () => {
  const [formData, setFormData] = useState({
    day: '',
    wakeUpTime: '',
    sleepTime: '',
    productivityHours: '',
    text: ''
  })

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = e => {
    e.preventDefault()
    console.log('Form submitted:', formData)
  }

  return (
    <div className='app-container'>
      <header className='app-header'>
        <div className='logo-container'>
          <img src='/sunday.svg' className='logo-icon' />{' '}
          {/** alt="Sunday.com icon"*/}
          <span className='logo-text'>
            <span className='logo-sunday'>sunday</span>
            <span className='logo-dot-com'>.com</span>
          </span>
        </div>
        <nav>
          <a href='#about'>About Us</a>
          <a href='#confess'>Confess</a>
          <a
            href='https://github.com/sriyabulusu/sunday.com'
            target='_blank'
            rel='noopener noreferrer'
          >
            <img src={`/github-mark.svg`} className='github-icon' />
          </a>
        </nav>
      </header>

      <main className='app-content'>
        <section className='calendar-section'>
          <iframe
            src='https://calendar.google.com/calendar/embed?height=600&wkst=2&ctz=America%2FLos_Angeles&bgcolor=%23ffffff&mode=WEEK&src=ZGl2aW5lc2NoZWR1bGVyYWlAZ21haWwuY29t&src=YWRkcmVzc2Jvb2sjY29udGFjdHNAZ3JvdXAudi5jYWxlbmRhci5nb29nbGUuY29t&src=NTRkMzNiNWRhODVhYzg0OTYyN2NmNmQwYmYxYTdkMDllNWViOWFmZTQyZDZiZTI0YjNjNWU5YWRlMjc5Y2MzNUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&src=ZW4udXNhI2hvbGlkYXlAZ3JvdXAudi5jYWxlbmRhci5nb29nbGUuY29t&color=%23039BE5&color=%2333B679&color=%237CB342&color=%230B8043'
            width='800'
            height='600'
            frameborder='0'
            scrolling='no'
          ></iframe>
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
              Anything else you'd like to share?
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
      </main>

      <footer className='app-footer'>
        <a href='#how-to'>How to Page</a>
      </footer>
    </div>
  )
}

export default App
