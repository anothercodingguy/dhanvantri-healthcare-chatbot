import React, { useState, useEffect } from 'react';
import './NewsModal.css';

const NewsModal = ({ isOpen, onClose }) => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fast fetch with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
      
      const response = await fetch('/api/news/health/latest', {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setNews(data.results || []);
      } else {
        setError(data.message || 'Failed to fetch news');
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. Please try again.');
      } else {
        console.error('Error fetching news:', err);
        setError('Could not load news. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchNews();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="news-modal-overlay" onClick={onClose}>
      <div className="news-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="news-modal-header">
          <h2>Latest Health News</h2>
          <button className="news-modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="news-modal-body">
          {loading && (
            <div className="news-loading">
              <div className="loading-spinner"></div>
              <p>Loading news...</p>
            </div>
          )}
          
          {error && (
            <div className="news-error">
              <p>{error}</p>
              <button onClick={fetchNews} className="retry-button">
                Try Again
              </button>
            </div>
          )}
          
          {!loading && !error && news.length === 0 && (
            <div className="news-empty">
              <p>No health news found.</p>
            </div>
          )}
          
          {!loading && !error && news.length > 0 && (
            <div className="news-articles">
              {news.map((article, index) => (
                <div key={index} className="news-article">
                  <h3>
                    <a 
                      href={article.link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="news-article-link"
                    >
                      {article.title}
                    </a>
                  </h3>
                  
                  {article.description && (
                    <p className="news-description">
                      {article.description.length > 150 
                        ? `${article.description.substring(0, 150)}...` 
                        : article.description
                      }
                    </p>
                  )}
                  
                  <div className="news-meta">
                    <span className="news-source">Source: {article.source_id}</span>
                    {article.pubDate && (
                      <span className="news-date">
                        {new Date(article.pubDate).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="news-modal-footer">
          <button onClick={onClose} className="close-button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewsModal;