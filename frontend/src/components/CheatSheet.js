import React, { useState, useEffect } from 'react';
import '../pages/PageStyles.css';
import BookIcon from '../assets/cheatsheet.png';

const cheatSheetData = [
  { emoji: '📄', description: 'Ends with a suffix - ex: _____ing' },
  { emoji: '✏️', description: 'Starts with a prefix - ex: st_____' },
  { emoji: '📂', description: 'Minimum word length' },
  { emoji: '📕', description: 'Maximum word length' },
  { emoji: '📏', description: 'Exact word length' },
  { emoji: '🖌️', description: 'Ends in any listed suffix' },
  { emoji: '📎', description: 'Repeated characters' },
  { emoji: '📖', description: 'Exact word match' },
  { emoji: '🔧', description: 'Raw custom regex' },
  { emoji: '  ', description: <span style={{ fontWeight: 'bold', textDecoration: 'underline', fontSize: '22px' }}>Sentence Regex</span> },
  { emoji: '📝', description: 'Exact sentence phrase' },
  { emoji: '📚', description: 'Sentence starts with - ex: should ____ ___ ________.' },
  { emoji: '📌', description: 'Sentence ends with - ex: __ _______ ____ ________ now.' },
  { emoji: '🔍', description: 'Sentence contains word' },
  { emoji: '🖋️', description: 'Sentence contains any listed words' },
  { emoji: '🖍️', description: 'Structured sentence pattern' },
  { emoji: '🔧', description: 'Raw sentence regex' },
];

const CheatSheet = () => {
  const [visible, setVisible] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const checkTheme = () => {
      const theme = document.documentElement.getAttribute('data-theme');
      setIsDarkMode(theme === 'dark');
    };

    // Check initially and set up a MutationObserver
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });

    return () => observer.disconnect();
  }, []);

  return (
    <>
      <div className="cheat-sheet-button" onClick={() => setVisible(true)}>
        <img src={BookIcon} alt="Cheat Sheet" className="cheat-sheet-icon" />
      </div>

      {visible && (
        <div className="cheat-sheet-modal">
          <div className={`cheat-sheet-content ${isDarkMode ? 'dark' : ''}`}>
            <h2>
              <span style={{ fontWeight: 'bold', textDecoration: 'underline', fontSize: '22px' }}>
                Cheat Regex
              </span>
            </h2>
            <ul>
              {cheatSheetData.map(({ emoji, description }, i) => (
                <li key={`${emoji}-${i}`}>
                  <span className="emoji">{emoji}</span> {description}
                </li>
              ))}
            </ul>
            <button className="popup-button" onClick={() => setVisible(false)}>Close</button>
          </div>
        </div>
      )}
    </>
  );
};

export default CheatSheet;
