import React from 'react';
import './App.css';
import FakeStreaming from './FakeStreaming';
import ImageUpload from './ImageUpload';

const HowTo = ({ formData, handleChange, handleSubmit }) => {

  const message = `
  To obtain your Google calendar link…
  Open Google Calendar:
  Go to Google Calendar and sign in with your Google account.
  Select the Calendar:
  On the left side, find the calendar you want to get the ID for under "My calendars."
  Open Calendar Settings:
  Hover over the calendar name, click on the three vertical dots (more options), and select Settings.
  Find the Calendar ID:
  Scroll down to the Integrate calendar section.
  You will see the Calendar ID listed there. It usually looks like an email address (e.g., yourcalendarid@group.calendar.google.com).
  Copy the Calendar ID:
  Click on the Calendar ID to highlight it, then right-click and select Copy or use Ctrl + C (Windows) or Command + C (Mac) to copy it.
  `
  return (
    <div>
      <ImageUpload />
      <FakeStreaming text={message} />
    </div>
  );
};

export default HowTo;