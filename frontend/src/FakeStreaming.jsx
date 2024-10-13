import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function FakeStreaming({ text }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [tokens, setTokens] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  function getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

  useEffect(() => {
    if (!text || text.length === 0) return;

    const loadingTime = setTimeout(() => {
      const tokenArray = text.split(' ');
      setTokens(tokenArray);
      setIsLoading(false);
    }, 1);

    return () => clearTimeout(loadingTime);
  }, [text]);

  useEffect(() => {
    if (tokens.length === 0 || isLoading) return;

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => prevIndex + 1);
    }, 50 + getRandomInt(600)); // Random interval for token appearance

    return () => clearInterval(interval);
  }, [tokens, isLoading]);

  return (
    <div className="fake-streaming">
      {/* Display loading animation while loading */}
      {isLoading ? (
        <motion.div
          className="loading-animation"
          animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1, repeat: Infinity }}
          style={{ textAlign: 'center', fontSize: '2em', color: 'gray' }}
        >
          Loading...
        </motion.div>
      ) : (
        <p>
          {tokens.slice(0, currentIndex).join(' ')}
        </p>
      )}
    </div>
  );
}
