import React, { useState } from 'react';
import './App.css'; // Main app styles

// Import your components
import AtsScore from './components/AtsScore.jsx'; 
import AutoMatch from './components/AutoMatch.jsx';
import JobRoles from './components/JobRoles.jsx'; 
import Dashboard from './components/Dashboard.jsx';

function App() {
  const [activeTab, setActiveTab] = useState('atsScore'); 

  return (
    // This is the main centered card
    <div className="App"> 
      
      {/* The navigation tabs are now back at the top */}
      <nav>
        <button 
          className={activeTab === 'atsScore' ? 'active' : ''}
          onClick={() => setActiveTab('atsScore')}
        >
          ATS Score
        </button>
        <button 
          className={activeTab === 'autoMatch' ? 'active' : ''}
          onClick={() => setActiveTab('autoMatch')}
        >
          Auto-Match Role
        </button>
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'jobRoles' ? 'active' : ''}
          onClick={() => setActiveTab('jobRoles')}
        >
          Job Roles
        </button>
      </nav>
      
      {/* The main content area */}
      <main>
        {activeTab === 'atsScore' && <AtsScore />}
        {activeTab === 'autoMatch' && <AutoMatch />}
        {activeTab === 'jobRoles' && <JobRoles />}
        {activeTab === 'dashboard' && <Dashboard />}
      </main>

    </div>
  );
}

export default App;
