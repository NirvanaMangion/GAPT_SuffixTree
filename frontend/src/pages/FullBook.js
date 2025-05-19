// src/pages/FullBook.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './FullBook.css';

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

/** returns a sorted array of page numbers to show (no ellipses) */
function getPageListNumbers(current, total) {
  const set = new Set();

  if (total <= 15) {
    for (let i = 1; i <= total; i++) set.add(i);
  } else {
    // first 3
    [1,2,3].forEach(n => set.add(n));
    // window around current
    for (let i = current - 2; i <= current + 9; i++) {
      if (i > 3 && i < total - 2) set.add(i);
    }
    // last 3
    [total-2, total-1, total].forEach(n => set.add(n));
    // ensure current
    if (current >=1 && current <= total) set.add(current);
  }

  return Array.from(set).sort((a,b) => a - b);
}

/** given that list of numbers, inject 'ELLIPSIS' markers where gaps appear */
function getPageItems(current, total) {
  const nums = getPageListNumbers(current, total);
  const items = [];
  nums.forEach((num, idx) => {
    if (idx > 0 && num !== nums[idx-1] + 1) {
      items.push('ELLIPSIS');
    }
    items.push(num);
  });
  return items;
}

const FullBook = () => {
  const { title }    = useParams();
  const navigate     = useNavigate();

  const [fullText, setFullText]   = useState('');
  const [pages, setPages]         = useState([]);
  const [currentPage, setCurrent] = useState(0);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState('');
  const [searchQuery, setSearch]  = useState('');
  const [fontSize, setFontSize]   = useState(16);

  useEffect(() => {
    const cleanTitle = title.replace(/[\s-]+$/, '');
    const filename   = `${cleanTitle}.txt`;

    fetch(`http://localhost:5000/api/book/full/${encodeURIComponent(filename)}`)
      .then(res => res.json())
      .then(data => {
        if (data.text) {
          setFullText(data.text);
          const pg = splitIntoPages(data.text);
          setPages(pg);
          setCurrent(0);
        } else {
          setError('Book content unavailable.');
        }
      })
      .catch(err => {
        console.error(err);
        setError('Failed to load book.');
      })
      .finally(() => setLoading(false));
  }, [title]);

  const total = pages.length;
  const pageText = pages[currentPage] || '';

  const highlighted = searchQuery
    ? pageText
        .split(new RegExp(`(${searchQuery})`, 'gi'))
        .map((part, i) =>
          part.toLowerCase() === searchQuery.toLowerCase()
            ? <mark key={i}>{part}</mark>
            : part
        )
    : pageText;

  const downloadBlob = (text, name) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadPage = () => {
    const clean = decodeURIComponent(title).replace(/[\s-]+$/, '');
    downloadBlob(pageText, `${clean}-page-${currentPage + 1}.txt`);
  };

  const handleDownloadFull = () => {
    const clean = decodeURIComponent(title).replace(/[\s-]+$/, '');
    downloadBlob(fullText, `${clean}.txt`);
  };

  // build our pagination items (numbers + 'ELLIPSIS')
  const pageItems = getPageItems(currentPage + 1, total);

  return (
    <div className="all-books-container full-book-container">
      <h1 className="book-title">{decodeURIComponent(title)}</h1>

      <div className="controls fullbook-controls">
        <button onClick={() => navigate(-1)} className="sort-button">
          ← Back
        </button>
        <button onClick={handleDownloadPage} className="sort-button">
          📄 Download Page
        </button>
        <button onClick={handleDownloadFull} className="sort-button">
          ⬇️ Download Full
        </button>
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
      {error   && <p className="error-message">{error}</p>}

      {!loading && !error && (
        <>
          <pre
            className="book-text"
            style={{ fontSize: `${fontSize}px` }}
          >
            {highlighted}
          </pre>

          <div className="pagination">
            <button
              onClick={() => setCurrent(p => Math.max(p - 1, 0))}
              disabled={currentPage === 0}
            >
              &laquo; Prev
            </button>

            {pageItems.map((item, idx) =>
              item === 'ELLIPSIS' ? (
                <span key={idx} className="ellipsis">…</span>
              ) : (
                <button
                  key={idx}
                  className={currentPage + 1 === item ? 'active' : ''}
                  onClick={() => setCurrent(item - 1)}
                >
                  {item}
                </button>
              )
            )}

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
