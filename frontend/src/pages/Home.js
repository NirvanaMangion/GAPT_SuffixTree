import React from 'react';
import SearchBar from '../components/SearchBar';
import './PageStyles.css';

const Home = () => (
  <div className="home-page">
    <h2 className="title">Search the documents</h2>
    <SearchBar onSearch={() => {}} />
    <button className="upload-btn">Upload .rtf File</button>
    <textarea placeholder="Paste your text here..." />
  </div>
);

export default Home;
