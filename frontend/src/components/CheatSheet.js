import React, { useState, useEffect } from 'react';
import '../pages/PageStyles.css';
import BookIcon from '../assets/cheatsheet.png';

const cheatSheetData = [
  { emoji: '📄', description: 'Ends with a suffix - ex: ________ment' },
  { emoji: '✏️', description: 'Starts with a prefix - ex: st______' },
  { emoji: '📂', description: 'Minimum word length - ex: 5' },
  { emoji: '📕', description: 'Maximum word length - ex: 3' },
  { emoji: '📏', description: 'Exact word length - ex: 5' },
  { emoji: '🖌️', description: 'Ends in any listed suffix - ex: ed|ing' },
  { emoji: '📎', description: 'Repeated characters - ex: 2 matches book, cool' },
  { emoji: '📖', description: 'Exact word match - ex: freedom' },
  { emoji: '🔧', description: 'Raw custom regex - ex: ^[bcd].*ing$' },
  { emoji: '  ', description: <span style={{ fontWeight: 'bold', textDecoration: 'underline', fontSize: '22px' }}>Sentence Regex</span> },
  { emoji: '📝', description: 'Exact sentence phrase - ex: once upon a time' },
  { emoji: '📚', description: 'Sentence starts with - ex: freedom ____ ___ ________.' },
  { emoji: '📌', description: 'Sentence ends with - ex: __ _______ ____ ________ now.' },
  { emoji: '🔍', description: 'Sentence contains word' },
  { emoji: '🖋️', description: 'Sentence contains any listed words - ex: life|death|hope' },
  { emoji: '🖍️', description: 'Structured sentence pattern - ex: [A-Z][^.!?]*war' },
  { emoji: '🛠️', description: 'Raw sentence regex - ex: ^The.*end$' },
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
