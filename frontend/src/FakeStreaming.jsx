import React, { useEffect, useState } from 'react';


export default function FakeStreaming({ text }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [tokens, setTokens] = useState([]);

  function getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

  useEffect(() => {
    if (!text || text.length === 0) return;
    const tokenArray = text.split(' ');
    setTokens(tokenArray);
  }, [text]);

  useEffect(() => {
    if (tokens.length === 0) return;

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => prevIndex + 1);
    }, 50 + getRandomInt(600));

    return () => clearInterval(interval);
  }, [tokens]);

  return (
    <div className="fake-streaming">
      <p>
        {tokens.slice(0, currentIndex).join(' ')}
      </p>
    </div>
  );
}
