import React from 'react';

// We receive activeTab and setActiveTab from App.jsx as props
function Sidebar({ activeTab, setActiveTab }) {
  
  // Helper function to check if a button is active
  const getButtonClass = (tabName) => {
    return `sidebar-button ${activeTab === tabName ? 'active' : ''}`;
  };

  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h2>JobQuest</h2>
      </div>
      
      <ul className="sidebar-menu">
        <li>
          <button 
            className={getButtonClass('atsScore')}
            onClick={() => setActiveTab('atsScore')}
          >
            ATS Score
          </button>
        </li>
        <li>
          <button 
            className={getButtonClass('autoMatch')}
            onClick={() => setActiveTab('autoMatch')}
          >
            Auto-Match Role
          </button>
        </li>
        <li>
          <button 
            className={getButtonClass('dashboard')}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
        </li>
        <li>
          <button 
            className={getButtonClass('jobRoles')}
            onClick={() => setActiveTab('jobRoles')}
          >
            Job Roles
          </button>
        </li>
      </ul>
    </nav>
  );
}

export default Sidebar;