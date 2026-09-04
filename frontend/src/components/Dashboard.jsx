import React, { useState, useEffect } from 'react';

import axios from 'axios';
import { Line, Bar, Pie } from 'react-chartjs-2'; 
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  LineElement,
  PointElement
} from 'chart.js';

// Register all the chart components we are using
ChartJS.register(
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  LineElement,
  PointElement
);

function Dashboard() {
  const [data, setData] = useState(null);
  const [keywordData, setKeywordData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [dashResponse, keywordResponse] = await Promise.all([
          axios.get("http://localhost:8000/dashboard-data/"),
          axios.get("http://localhost:8000/keyword-data/")
        ]);

        setData(dashResponse.data);
        setKeywordData(keywordResponse.data);
        setError(null);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError(err.message || "Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // --- Chart Options for Dark Mode ---
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: { color: '#f9fafb' }
      },
      title: { display: false }
    }
  };
  
  const barOptions = {
    ...chartOptions,
    indexAxis: 'y', // Horizontal bar chart
    scales: {
      x: {
        beginAtZero: true,
        ticks: { color: '#f9fafb', stepSize: 1 }
      },
      y: {
        ticks: { color: '#f9fafb' }
      }
    },
    plugins: {
      legend: { display: false }
    }
  };

  const lineOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: { color: '#f9fafb' }
      },
      x: {
        ticks: { color: '#f9fafb' }
      }
    },
    plugins: {
      legend: { display: false }
    },
    elements: {
      line: {
        borderColor: '#3b82f6',
        tension: 0.1
      },
      point: {
        backgroundColor: '#3b82f6',
      }
    }
  };
  // --- End of Chart Options ---

  if (loading) {
    return (<div style={{ textAlign: 'center', padding: '40px' }}><h2>Loading Dashboard...</h2></div>);
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h2 style={{ color: '#ff6b6b' }}>Error Loading Dashboard</h2>
        <p>{error}</p>
        <p>Please check if your backend server is running.</p>
      </div>
    );
  }

  if (!data || !keywordData) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h2>No Data Available</h2>
        <p>Upload some resumes to see analytics!</p>
      </div>
    );
  }

  // Helper variables
  const hasRoleCounts = data.role_counts && Object.keys(data.role_counts).length > 0;
  const hasTrend = data.score_trend && data.score_trend.length > 0;
  const hasMissedKeywords = keywordData.top_missed_keywords && Object.keys(keywordData.top_missed_keywords).length > 0;
  const hasFoundKeywords = keywordData.top_found_keywords && Object.keys(keywordData.top_found_keywords).length > 0;

  // --- Prepare Chart Data ---
  const pieData = {
    labels: hasRoleCounts ? Object.keys(data.role_counts) : [],
    datasets: [{
      data: hasRoleCounts ? Object.values(data.role_counts) : [],
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
      borderColor: '#374151',
    }],
  };
  
  const lineData = {
    labels: hasTrend ? data.score_trend.map(d => new Date(d.time).toLocaleTimeString()) : [],
    datasets: [{
      label: 'ATS Score',
      data: hasTrend ? data.score_trend.map(d => d.score) : [],
      fill: false,
    }],
  };
  
  const missedBarData = {
    labels: hasMissedKeywords ? Object.keys(keywordData.top_missed_keywords) : [],
    datasets: [{
      label: 'Times Missed',
      data: hasMissedKeywords ? Object.values(keywordData.top_missed_keywords) : [],
      backgroundColor: 'rgba(239, 68, 68, 0.5)',
      borderColor: '#ef4444',
      borderWidth: 1,
    }],
  };
  
  const foundBarData = {
    labels: hasFoundKeywords ? Object.keys(keywordData.top_found_keywords) : [],
    datasets: [{
      label: 'Times Found',
      data: hasFoundKeywords ? Object.values(keywordData.top_found_keywords) : [],
      backgroundColor: 'rgba(16, 185, 129, 0.5)',
      borderColor: '#10b981',
      borderWidth: 1,
    }],
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ 
        fontSize: '2.5rem',
        background: 'linear-gradient(to right, #a78bfa, #ec4899)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        marginBottom: '40px',
        textAlign: 'center'
      }}>
        🚀 JobQuest Dashboard
      </h1>
      
      {/* Stats Grid */}
      <div className="stats-grid">
         <div className="stat-box">
          <div style={{ fontSize: '1.5rem', marginBottom: '10px' }}>📄</div>
          <h4>Total Analyses</h4>
          <strong>{data.total_analyses || 0}</strong>
        </div>
        <div className="stat-box">
          <div style={{ fontSize: '1.5rem', marginBottom: '10px' }}>⭐</div>
          <h4>Average Score</h4>
          <strong>{data.average_score ? data.average_score.toFixed(1) : 0}%</strong>
        </div>
        <div className="stat-box">
          <div style={{ fontSize: '1.5rem', marginBottom: '10px' }}>💼</div>
          <h4>Roles Analyzed</h4>
          <strong>{hasRoleCounts ? Object.keys(data.role_counts).length : 0}</strong>
        </div>
      </div>

      {/* --- NEW 2x2 CHART GRID --- */}
      <div className="charts-grid">
        
        {/* Chart 1: ATS Score Trend (Line Chart) */}
        <div className="chart-container">
          <h3>ATS Score Trend (Last 15)</h3>
          <div className="chart-wrapper">
            {hasTrend ? <Line data={lineData} options={lineOptions} /> : <p>Run more analyses to see a trend.</p>}
          </div>
        </div>

        {/* Chart 2: Role Popularity (Pie Chart) */}
        <div className="chart-container">
          <h3>Role Popularity</h3>
          <div className="chart-wrapper">
            {hasRoleCounts ? <Pie data={pieData} options={chartOptions} /> : <p>No role data yet.</p>}
          </div>
        </div>
        
        {/* Chart 3: Most Missed Keywords (Bar Chart) */}
        <div className="chart-container">
          <h3>Top 10 Most Missed Keywords</h3>
          <div className="chart-wrapper" style={{height: '300px'}}>
            {hasMissedKeywords ? <Bar data={missedBarData} options={barOptions} /> : <p>No keyword data yet.</p>}
          </div>
        </div>

        {/* Chart 4: Most Found Keywords (Bar Chart) */}
        <div className="chart-container">
          <h3>Top 10 Most Found Keywords</h3>
          <div className="chart-wrapper" style={{height: '300px'}}>
            {hasFoundKeywords ? <Bar data={foundBarData} options={barOptions} /> : <p>No keyword data yet.</p>}
          </div>
        </div>
        
      </div>

      {/* Footer */}
      <div style={{ 
        textAlign: 'center',
        marginTop: '50px',
        opacity: 0.6,
        fontSize: '0.9rem',
        color: '#d1d5db'
      }}>
        <p>Powered by AI • Real-time Analytics • JobQuest 2025</p>
      </div>
    </div>
  );
}

export default Dashboard;