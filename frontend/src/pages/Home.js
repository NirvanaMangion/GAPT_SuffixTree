import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import './PageStyles.css'; // Your global styles

const Home = () => {
  const [query, setQuery] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleSearch = () => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click(); // 👈 This opens the File Explorer
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.txt')) {
      toast.error('Only .txt files are allowed.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        if (data.message) {
          toast.success(data.message);
        } else {
          toast.error('Upload failed.');
        }
      })
      .catch(() => {
        toast.error('Failed to upload the book.');
      });
  };

  return (
    <div className="home-page">
      <h1 className="title">Search the documents</h1>
      
      <div className="search-wrapper">
        <input
          type="text"
          placeholder="Search for a word..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
          className="search-input"
        />
        <button className="search-button" onClick={handleSearch}>
          <span role="img" aria-label="search">🔍</span>
        </button>
      </div>

      {/* Hidden input for uploading */}
      <input
        type="file"
        accept=".txt"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <div style={{ marginTop: "30px" }}>
        <button className="upload-button" onClick={handleUploadClick}>
          📤 Upload a New Book
        </button>
      </div>
    </div>
  );
};

export default Home;
