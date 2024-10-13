import React from 'react';
import './App.css';

const AboutUs = () => {
  return (
    <div style={styles.container}>
      <section style={styles.headerSection}>
        <h1 style={styles.header}>Welcome to sunday.com</h1>
        <p style={styles.subHeader}>
          Your all-in-one productivity tool for smarter scheduling.
        </p>
      </section>

      <section style={styles.bodySection}>
        <p style={styles.text}>
          At sunday.com, we strive to be your all-in-one productivity tool, driven by research showing that effective schedule management is the top productivity enhancer. 
          Leveraging cutting-edge Generative AI, we optimize your tasks and events around your unique schedule and energy patterns. 
        </p>
        <p style={styles.text}>
          Our tool goes beyond basic scheduling by offering personalized feedback and engagement from one of four specialized "agents":
          <ul style={styles.list}>
            <li>A lawyer</li>
            <li>A monk</li>
            <li>A productivity specialist</li>
            <li>A philosopher</li>
          </ul>
        </p>
        <p style={styles.text}>
          Each agent is powered by a unique RAG (Retrieval-Augmented Generation) pipeline, synthesizing insights from hundreds of books and papers to deliver accurate, sourced, 
          and tailored information to maximize your productivity.
        </p>
      </section>
    </div>
  );
};

// Styling using JavaScript Object for inline styles
const styles = {
  container: {
    padding: '10',
    maxWidth: '800px',
    margin: '0 auto',
    fontFamily: 'Poppins, sans-serif',
    color: '#333',
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  },
  headerSection: {
    marginTop: '30px'
  },
  header: {
    margin: '0 auto',
    fontSize: '2.5em',
    color: '#333',
    textAlign: 'center',
  },
  subHeader: {
    margin: '10px',
    fontSize: '1.2em',
    color: '#7f8c8d',
    textAlign: 'center',
  },
  bodySection: {
    margin: '0 auto',
    lineHeight: '1.6',
    fontSize: '1.1em',
  },
  text: {
    marginLeft: '25px',
    marginTop: '25px',
  },
  list: {
    marginLeft: '20px',
    listStyleType: 'circle',
  }
};


export default AboutUs;