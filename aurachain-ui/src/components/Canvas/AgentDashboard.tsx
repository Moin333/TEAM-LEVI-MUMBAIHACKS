import React from 'react';
import AgentCard, { type Agent } from './AgentCard';
import DetailedReport from './DetailedReport'; // Import the new report
import { useUIStore } from '../../store/uiStore'; // Import store
import { X } from 'lucide-react'; // Import X icon

// Mock Data
const MOCK_AGENTS: Agent[] = [
  { 
    id: '1', 
    name: 'Data Harvester', 
    type: 'harvester', 
    status: 'completed', 
    progress: 100, 
    summary: 'Collected 730 days of historical sales data from Mumbai branch.' 
  },
  { 
    id: '2', 
    name: 'Trend Analyst', 
    type: 'analyst', 
    status: 'processing', 
    progress: 45 
  },
  { 
    id: '3', 
    name: 'Demand Forecaster', 
    type: 'forecaster', 
    status: 'queued', 
    progress: 0 
  }
];

const AgentDashboard: React.FC = () => {
  const { selectedAgentId, setSelectedAgent, setRightPanelOpen } = useUIStore();

  // 1. If an agent is selected, show the Detailed Report
  if (selectedAgentId) {
    return <DetailedReport agentId={selectedAgentId} />;
  }

  // 2. Otherwise, show the main List Dashboard
  return (
    <div className="h-full flex flex-col bg-light-surface dark:bg-dark-surface">
      {/* Header */}
      <div className="h-16 px-6 border-b border-light-border dark:border-dark-border flex items-center justify-between flex-shrink-0 bg-white dark:bg-dark-elevated">
        <div>
          <h2 className="font-heading font-semibold text-slate-800 dark:text-white">Agent Workflow</h2>
          <p className="text-xs text-slate-500">3 Agents Active • 1 Processing</p>
        </div>
        
        {/* Close Button */}
        <button 
          onClick={() => setRightPanelOpen(false)}
          className="p-2 -mr-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          aria-label="Close Panel"
        >
          <X size={20} />
        </button>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        
        {/* Execution Flow Visualizer */}
        <div className="mb-6 px-2">
           <div className="flex items-center space-x-2 text-xs text-slate-400 mb-2 uppercase tracking-wider font-bold">
             <span>Execution Pipeline</span>
           </div>
           <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-accent-teal"></div>
              <div className="h-[2px] w-8 bg-accent-teal"></div>
              <div className="w-2 h-2 rounded-full bg-accent-amber animate-pulse"></div>
              <div className="h-[2px] w-8 bg-slate-200 dark:bg-slate-700"></div>
              <div className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-700"></div>
           </div>
        </div>

        {/* Grid of Cards */}
        <div className="grid grid-cols-1 gap-4">
          {MOCK_AGENTS.map(agent => (
            <div key={agent.id} onClick={() => setSelectedAgent(agent.id)} className="cursor-pointer">
              <AgentCard agent={agent} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AgentDashboard;