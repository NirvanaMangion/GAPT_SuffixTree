import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './FullBook.css';

const FullBook = () => {
  const { title } = useParams();
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [fontSize, setFontSize] = useState(16);

  useEffect(() => {
    fetch(`http://localhost:5000/api/book/full/${encodeURIComponent(title + '.txt')}`)
      .then(res => res.json())
      .then(data => {
        if (data.text) {
          setContent(data.text);
        } else {
          setError("Book content unavailable.");
        }
      })
      .catch(err => {
        console.error(err);
        setError("Failed to load book.");
      })
      .finally(() => setLoading(false));
  }, [title]);

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${decodeURIComponent(title)}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const highlightedText = searchQuery
    ? content.split(new RegExp(`(${searchQuery})`, 'gi')).map((part, i) =>
        part.toLowerCase() === searchQuery.toLowerCase()
          ? <mark key={i}>{part}</mark>
          : part
      )
    : content;

  return (
    <div className="full-book-container">
      <div className="toolbar">
        <button onClick={() => navigate(-1)} className="back-button">← Back</button>
        <button onClick={handleDownload} className="toolbar-button">⬇️ Download</button>
        <input
          type="text"
          placeholder="Search in book..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <label className="toolbar-button">
          A+
          <input type="range" min="12" max="28" value={fontSize} onChange={(e) => setFontSize(e.target.value)} />
        </label>
      </div>

      <h1 className="book-title">{decodeURIComponent(title)}</h1>

      {loading && <div className="spinner"></div>}
      {error && <p className="error-message">{error}</p>}

      {!loading && !error && (
        <pre className="book-text" style={{ fontSize: `${fontSize}px` }}>
          {highlightedText}
        </pre>
      )}
    </div>
  );
};

export default FullBook;
