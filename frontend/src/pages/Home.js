import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import '../pages/PageStyles.css';
import Logo from '../assets/logo.png';
import CheatSheet from '../components/CheatSheet';

const wordEmojis = ["📄", "✏️", "📂", "📕", "📏", "🖌️", "📎", "📖", "🔧"];
const sentenceEmojis = ["📝", "🖌️", "📌", "🔍", "🖋️", "🖍️", "🔧"];

const Home = () => {
  const [query, setQuery] = useState('');
  const [selectedEmoji, setSelectedEmoji] = useState("📄");
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchType, setSearchType] = useState('word');
  const [showSuccessPopup, setShowSuccessPopup] = useState(false);
  const [showOverwritePopup, setShowOverwritePopup] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const getEmojiOptions = () => (searchType === 'word' ? wordEmojis : sentenceEmojis);

  const handleSearch = () => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}&mode=${encodeURIComponent(selectedEmoji)}&type=${searchType}`);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleEmojiSelect = (emoji) => {
    setSelectedEmoji(emoji);
    setShowDropdown(false);
  };

  const uploadFile = (file) => {
    const formData = new FormData();
    formData.append('file', file);

    fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        if (data.message) {
          setShowSuccessPopup(true);
        } else {
          toast.error('Upload failed.');
        }
      })
      .catch(() => {
        toast.error('Failed to upload the book.');
      });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.txt')) {
      toast.error('Only .txt files are allowed.');
      e.target.value = null;
      return;
    }

    fetch('http://localhost:5000/api/books')
      .then(res => res.json())
      .then(existingFiles => {
        const normalized = existingFiles.map(f => f.trim().toLowerCase());
        if (normalized.includes(file.name.trim().toLowerCase())) {
          setPendingFile(file);
          setShowOverwritePopup(true);
        } else {
          uploadFile(file);
        }
      })
      .catch(() => {
        toast.error('Error checking existing books.');
      })
      .finally(() => {
        e.target.value = null;
      });
  };

  const confirmOverwrite = () => {
    if (pendingFile) {
      uploadFile(pendingFile);
    }
    setPendingFile(null);
    setShowOverwritePopup(false);
  };

  const cancelOverwrite = () => {
    setPendingFile(null);
    setShowOverwritePopup(false);
    toast.info('Upload cancelled.');
  };

  const handleViewBooks = () => {
    navigate('/books');
  };

  return (
    <div className="home-page">
      <img src={Logo} alt="SuffixSearch Logo" className="logo-image" />
      <h1 className="title">Search the documents</h1>

      <div className="search-toggle-wrapper">
        <button
          className={`toggle-button ${searchType === 'word' ? 'active' : ''}`}
          onClick={() => {
            setSearchType('word');
            setSelectedEmoji("📄");
          }}
        >
          search word
        </button>
        <button
          className={`toggle-button ${searchType === 'sentence' ? 'active' : ''}`}
          onClick={() => {
            setSearchType('sentence');
            setSelectedEmoji("📝");
          }}
        >
          search sentence
        </button>
      </div>

      <div className="search-wrapper">
        <div className="dropdown-icon" onClick={() => setShowDropdown(!showDropdown)}>
          <span>{selectedEmoji}</span>
          <span className="caret">▼</span>
          {showDropdown && (
            <div className="emoji-menu">
              {getEmojiOptions().map((emoji) => (
                <div
                  key={emoji}
                  className="emoji-option"
                  onClick={() => handleEmojiSelect(emoji)}
                >
                  {emoji}
                </div>
              ))}
            </div>
          )}
        </div>
        <input
          type="text"
          placeholder={searchType === 'word' ? 'Search for a word...' : 'Search for a sentence...'}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
          className="search-input"
        />
        <button className="search-button" onClick={handleSearch}>
          <span role="img" aria-label="search">🔍</span>
        </button>
      </div>

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

      {showSuccessPopup && (
        <div className="popup-overlay">
          <div className="popup-content">
            <h2>✅ Book Uploaded Successfully!</h2>
            <div className="popup-buttons">
              <button className="popup-button" onClick={() => setShowSuccessPopup(false)}>
                Close
              </button>
              <button className="popup-button" onClick={handleViewBooks}>
                📚 View All Books
              </button>
            </div>
          </div>
        </div>
      )}

      {showOverwritePopup && (
        <div className="popup-overlay">
          <div className="popup-content">
            <h2>⚠️ A file with the same name already exists.</h2>
            <p>Do you want to overwrite it?</p>
            <button className="confirm-button" onClick={confirmOverwrite}>
              Yes, Overwrite
            </button>
            <button className="cancel-button" onClick={cancelOverwrite}>
              No, Cancel
            </button>
          </div>
        </div>
      )}

      <CheatSheet />
    </div>
  );
};

export default Home;
