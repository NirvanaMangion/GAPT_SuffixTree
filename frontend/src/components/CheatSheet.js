import React, { useState } from 'react';
import '../pages/PageStyles.css';
import BookIcon from '../assets/cheatsheet.png';

const cheatSheetData = [
  { emoji: '📄', description: 'Ends with a suffix' },
  { emoji: '✏️', description: 'Starts with a prefix' },
  { emoji: '📂', description: 'Minimum word length' },
  { emoji: '📕', description: 'Maximum word length' },
  { emoji: '📏', description: 'Exact word length' },
  { emoji: '🖌️', description: 'Ends in any listed suffix' },
  { emoji: '📎', description: 'Repeated characters' },
  { emoji: '📖', description: 'Exact word match' },
  { emoji: '🔧', description: 'Raw custom regex' },
  { emoji : '  ', description: <span style={{ fontWeight: 'bold', textDecoration: 'underline', fontSize: '22px' }}>Sentence Regex</span> },
  { emoji: '📝', description: 'Exact sentence phrase' },
  { emoji: '🖌️', description: 'Sentence starts with' },
  { emoji: '📌', description: 'Sentence ends with' },
  { emoji: '🔍', description: 'Sentence contains word' },
  { emoji: '🖋️', description: 'Sentence contains any listed words' },
  { emoji: '🖍️', description: 'Structured sentence pattern' },
  { emoji: '🔧', description: 'Raw sentence regex' },
];

const CheatSheet = () => {
  const [visible, setVisible] = useState(false);

  return (
    <>
      <div className="cheat-sheet-button" onClick={() => setVisible(true)}>
        <img src={BookIcon} alt="Cheat Sheet" className="cheat-sheet-icon" />
      </div>

      {visible && (
        <div className="cheat-sheet-modal">
          <div className="cheat-sheet-content">
            <h2>📚 Cheat Sheet</h2>
            <ul>
              {cheatSheetData.map(({ emoji, description }) => (
                <li key={emoji}>
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
