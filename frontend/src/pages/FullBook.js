// src/pages/FullBook.js
import React, { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './FullBook.css';
import { highlightMatch } from './highlighting';

const PAGE_SIZE = 1800;

function splitIntoPages(text, pageSize = PAGE_SIZE) {
  const pages = [];
  let start = 0, n = text.length;
  while (start < n) {
    let end = Math.min(start + pageSize, n);
    if (end < n && text[end] !== ' ') {
      const nextSpace = text.indexOf(' ', end);
      end = nextSpace === -1 ? n : nextSpace;
    }
    pages.push(text.slice(start, end));
    start = end + 1;
  }
  return pages;
}

const FullBook = () => {
  const { title } = useParams();
  const navigate = useNavigate();

  const [fullText, setFullText] = useState('');
  const [pages, setPages] = useState([]);
  const [currentPage, setCurrent] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [fontSize, setFontSize] = useState(16);

  const [searchQuery, setSearch] = useState('');
  const [regex, setRegex] = useState('');
  const [emoji, setEmoji] = useState('');
  const [queryArg, setQueryArg] = useState('');

  useEffect(() => {
    const cleanTitle = title.replace(/[\s-]+$/, '');
    const filename = `${cleanTitle}.txt`;

    const search = new URLSearchParams(window.location.search).get("word") || "";
    setSearch(search);

    // load book text
    fetch(`http://localhost:5000/api/book/full/${encodeURIComponent(filename)}`)
      .then(res => res.json())
      .then(data => {
        if (data.text) {
          setFullText(data.text);
          setPages(splitIntoPages(data.text));
        } else {
          setError("Book content unavailable.");
        }
      })
      .catch(err => {
        console.error(err);
        setError("Failed to load book.");
      })
      .finally(() => setLoading(false));

    // load regex info
    if (search) {
      fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(search)}`)
        .then(res => res.json())
        .then(data => {
          if (data.regex) setRegex(data.regex);
          if (data.emoji) setEmoji(data.emoji);
          if (data.query && data.query.includes(":")) {
            const [, arg] = data.query.split(":", 2);
            setQueryArg(arg);
          }
        })
        .catch(err => console.error("Regex fetch error:", err));
    }
  }, [title]);

  const total = pages.length;
  const pageText = pages[currentPage] || '';

  const highlightedPage = useMemo(() => {
    return searchQuery && regex
      ? highlightMatch(pageText, regex, emoji, queryArg)
      : pageText;
  }, [pageText, regex, emoji, queryArg, searchQuery]);

  const handleDownloadBlob = (text, name) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadPage = () => {
    const safeName = decodeURIComponent(title).replace(/[\s-]+$/, '');
    handleDownloadBlob(pageText, `${safeName}-page-${currentPage + 1}.txt`);
  };

  const handleDownloadFull = () => {
    const safeName = decodeURIComponent(title).replace(/[\s-]+$/, '');
    handleDownloadBlob(fullText, `${safeName}.txt`);
  };

  const pageItems = useMemo(() => {
    const range = [];
    for (let i = 0; i < total; i++) range.push(i);
    return range;
  }, [total]);

  return (
    <div className="all-books-container full-book-container">
      <h1 className="book-title">{decodeURIComponent(title)}</h1>

      <div className="controls fullbook-controls">
        <button onClick={() => navigate(-1)} className="sort-button">← Back</button>
        <button onClick={handleDownloadPage} className="sort-button">📄 Download Page</button>
        <button onClick={handleDownloadFull} className="sort-button">⬇️ Download Full</button>
        <input
          type="text"
          placeholder="Search in page..."
          value={searchQuery}
          onChange={e => setSearch(e.target.value)}
          className="search-input"
        />
        <label className="toolbar-button">
          A+
          <input
            type="range"
            min="12"
            max="28"
            value={fontSize}
            onChange={e => setFontSize(e.target.value)}
          />
        </label>
      </div>

      {loading && <div className="spinner"></div>}
      {error && <p className="error-message">{error}</p>}

      {!loading && !error && (
        <>
          <pre
            className="book-text"
            style={{ fontSize: `${fontSize}px` }}
          >
            {highlightedPage}
          </pre>

          <div className="pagination">
            <button
              onClick={() => setCurrent(p => Math.max(p - 1, 0))}
              disabled={currentPage === 0}
            >
              &laquo; Prev
            </button>

            {pageItems.map((item) => (
              <button
                key={item}
                className={currentPage === item ? 'active' : ''}
                onClick={() => setCurrent(item)}
              >
                {item + 1}
              </button>
            ))}

            <button
              onClick={() => setCurrent(p => Math.min(p + 1, total - 1))}
              disabled={currentPage === total - 1}
            >
              Next &raquo;
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default FullBook;
