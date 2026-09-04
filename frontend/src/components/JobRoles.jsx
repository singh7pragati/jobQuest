import React, { useState, useEffect } from 'react';
import axios from 'axios';

function JobRoles() {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const response = await axios.get("https://jobquest-backend-iz7j.onrender.com/jobs/");
        setRoles(response.data); 
        setError(null);
      } catch (err) {
        console.error("Error fetching job roles:", err);
        setError("Failed to load job roles.");
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []); 

  if (loading) return <p>Loading job roles...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div className="job-roles-container">
      <h2>Available Job Roles ({roles.length})</h2>
      <p>This is the full list of roles in the backend database that your resume can be scored against.</p>
      <ul className="job-roles-list">
        {roles.map((role, index) => (
          <li key={index}>{role}</li>
        ))}
      </ul>
    </div>
  );
}

export default JobRoles;