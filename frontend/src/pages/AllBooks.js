// src/pages/AllBooks.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AllBooks.css';

const AllBooks = () => {
  const [books, setBooks] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState('asc');

  const booksPerPage = 10;
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/api/books')
      .then(res => res.json())
      .then(data => {
        const formatted = data.map(filename => {
          const cleaned = filename.replace('.txt', '');
          const [title, ...authorParts] = cleaned.split(' - ');
          return {
            title: title.trim(),
            author: authorParts.join(' - ').trim()
          };
        });
        setBooks(formatted);
      })
      .catch(err => {
        console.error('Failed to fetch books:', err);
      });
  }, []);

  const sortedBooks = [...books].sort((a, b) => {
    if (sortOrder === 'asc') return a.title.localeCompare(b.title);
    return b.title.localeCompare(a.title);
  });

  const totalPages = Math.ceil(sortedBooks.length / booksPerPage);
  const startIndex = (currentPage - 1) * booksPerPage;
  const currentBooks = sortedBooks.slice(startIndex, startIndex + booksPerPage);

  const changePage = (pageNum) => {
    if (pageNum >= 1 && pageNum <= totalPages) {
      setCurrentPage(pageNum);
    }
  };

  const toggleSort = () => {
    setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
  };

  return (
    <div className="all-books-container">
      <h1>All Books</h1>

      <div className="controls">
        <button className="sort-button" onClick={toggleSort}>
          Sort: {sortOrder === 'asc' ? 'A → Z' : 'Z → A'}
        </button>
      </div>

      <div className="books-list">
        {currentBooks.length > 0 ? (
          currentBooks.map((book, index) => (
            <div
              key={index}
              className="book-card clickable"
              onClick={() =>
                navigate(`/read/${encodeURIComponent(book.title + ' - ' + book.author)}`)
              }
            >
              <span className="book-icon">📚</span>
              <div className="book-details">
                <h3 className="book-title">{book.title}</h3>
                <p className="book-author">{book.author}</p>
              </div>
            </div>
          ))
        ) : (
          <p>No books found.</p>
        )}
      </div>

      <div className="pagination">
        <button onClick={() => changePage(currentPage - 1)} disabled={currentPage === 1}>
          &laquo; Prev
        </button>
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i}
            className={currentPage === i + 1 ? 'active' : ''}
            onClick={() => changePage(i + 1)}
          >
            {i + 1}
          </button>
        ))}
        <button onClick={() => changePage(currentPage + 1)} disabled={currentPage === totalPages}>
          Next &raquo;
        </button>
      </div>
    </div>
  );
};

export default AllBooks;
