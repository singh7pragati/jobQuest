import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AtsScore() {
  const [file, setFile] = useState(null);
  const [jobRole, setJobRole] = useState("Java Developer");
  const [jobRolesList, setJobRolesList] = useState([]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axios.get("http://localhost:8000/jobs/");
        setJobRolesList(response.data);
        if (response.data.length > 0) {
          setJobRole(response.data[0]);
        }
      } catch (err) {
        console.error("Error fetching job roles:", err);
      }
    };
    fetchJobs();
  }, []);

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
    formData.append("job_role", jobRole);

    try {
      const response = await axios.post(
        "http://localhost:8000/upload-resume/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setResult(response.data);
    } catch (err) {
      console.error("Error uploading resume:", err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("Failed to analyze resume. Check file type (PDF/DOCX).");
      }
    } finally {
      setLoading(false);
    }
  };

  // --- NEW: Download PDF Handler ---
  const handleDownload = async () => {
    if (!result) return;
    
    setLoading(true); // Show spinner while PDF is generated
    setError(null);
    
    try {
      const response = await axios.post(
        "http://localhost:8000/generate-report/",
        {
          role: result.role,
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
      link.remove(); // Clean up
      
    } catch (err) {
      console.error("Error downloading report:", err);
      setError("Failed to download PDF report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ats-score-container">
      {loading && (
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      )}

      <h2>Get ATS Score by Role</h2>
      <p>Upload your resume and select a job role to see how well you match.</p>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Select Job Role:</label>
          <select
            value={jobRole}
            onChange={(e) => setJobRole(e.target.value)}
          >
            {jobRolesList.map((role) => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Upload Resume (PDF/DOCX):</label>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Get Score"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="results">
          
          {/* --- NEW: Download Button --- */}
          <button onClick={handleDownload} className="download-button" disabled={loading}>
            Download PDF Report
          </button>
          
          <h3>Analysis for {result.filename}</h3>
          
          <div className="score-circle">
            <strong>{result.ats_score_percent}%</strong>
            <span>{result.role}</span>
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

        </div>
      )}
    </div>
  );
}

export default AtsScore;