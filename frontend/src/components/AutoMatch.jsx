import React, { useState } from 'react';
import axios from 'axios';

function AutoMatch() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("Please select a resume file.");
      return;
    }

    setLoading(true);
    setResult(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "https://jobquest-backend-iz7j.onrender.com/auto-match-role/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setResult(response.data);
    } catch (err) {
      console.error("Error auto-matching resume:", err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("Failed to analyze resume. Check file type (PDF/DOCX).");
      }
    } finally {
      setLoading(false);
    }
  };
  
  // --- Download PDF Handler ---
  const handleDownload = async () => {
    if (!result) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        "https://jobquest-backend-iz7j.onrender.com/generate-report/",
        {
          // Send data for the *best matched* role
          role: result.best_matched_role, 
          ats_score: result.ats_score_percent,
          missing_keywords: result.missing_keywords,
          improvement_advice: result.improvement_advice
        },
        {
          responseType: 'blob', // This is crucial to handle the file download
        }
      );
      
      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'JobQuest_Report.pdf'); // This is the file name
      document.body.appendChild(link);
      link.click();
      link.remove(); // Clean up the temporary link
      
    } catch (err) {
      console.error("Error downloading report:", err);
      setError("Failed to download PDF report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auto-match-container">
      {loading && (
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      )}

      <h2>Auto-Match Best Role</h2>
      <p>Upload your resume and we'll find the best job role for you.</p>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Upload Resume (PDF/DOCX):</label>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files[0])} 
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Find Best Role"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="results">
          
          {/* --- Download Button --- */}
          <button onClick={handleDownload} className="download-button" disabled={loading}>
            Download PDF Report
          </button>
          
          <h3>Best Match for {result.filename}</h3>

          <div className="score-circle">
            <strong>{result.ats_score_percent}%</strong>
            <span>{result.best_matched_role}</span>
          </div>

          <div className="results-advice">
            <h4>Improvement Advice:</h4>
            <ul>
              {result.improvement_advice.map((advice, i) => (
                <li key={i}>{advice}</li>
              ))}
            </ul>
          </div>
          
          {result.missing_keywords && result.missing_keywords.length > 0 && (
            <div className="results-missing">
              <h4>Missing Keywords:</h4>
              <ul>
                {result.missing_keywords.map((kw, i) => (
                  <li key={i}>{kw}</li>
                ))}
              </ul>
            </div>
          )}

          {result.suggested_courses && (
            <div className="results-advice">
              <h4>Suggested Courses:</h4>
              <p>
                <a href={result.suggested_courses.udemy} target="_blank" rel="noopener noreferrer">Udemy</a> | 
                <a href={result.suggested_courses.coursera} target="_blank" rel="noopener noreferrer">Coursera</a>
              </p>
            </div>
          )}

        </div>
      )}
    </div>
  );
}

export default AutoMatch;