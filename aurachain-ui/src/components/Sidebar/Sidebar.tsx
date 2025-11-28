import React from 'react';
import { clsx } from 'clsx';
import { Infinity as InfinityIcon, Database, PanelLeft, Plus } from 'lucide-react'; // Added Plus icon
import SessionList from './SessionList';
import UserProfile from './UserProfile';
import { useUIStore } from '../../store/uiStore'; // Import store for resetSession

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const { resetSession } = useUIStore(); // Get reset action

  return (
    <aside 
      className={clsx(
        "flex-shrink-0 flex flex-col border-r border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] relative z-20",
        isOpen ? "w-[280px]" : "w-[72px]"
      )}
    >
      {/* 1. Top Section: Brand */}
      <div className={clsx(
        "h-16 flex items-center transition-all duration-300",
        isOpen ? "justify-start px-3 gap-3" : "justify-center px-2"
      )}>
        
        {/* Interactive Logo/Toggle Area - Fixed Width 48px (w-12) */}
        <button 
          onClick={onToggle}
          className="group relative flex items-center justify-center focus:outline-none w-12 h-12 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex-shrink-0"
          title={isOpen ? "Close sidebar" : "Open sidebar"}
        >
          <div className="relative w-8 h-8 flex items-center justify-center">
            <div className="absolute inset-0 flex items-center justify-center transition-all duration-200 opacity-100 scale-100 group-hover:opacity-0 group-hover:scale-90">
               <InfinityIcon size={32} strokeWidth={2.5} className="text-primary-500" />
            </div>
            <div className="absolute inset-0 flex items-center justify-center transition-all duration-200 opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100">
               <PanelLeft size={24} className="text-slate-500 dark:text-slate-400" />
            </div>
          </div>
        </button>
        
        {/* Name */}
        <div className={clsx(
          "fade-in whitespace-nowrap overflow-hidden transition-all duration-300",
          isOpen ? "w-auto opacity-100 translate-x-0" : "w-0 opacity-0 -translate-x-4"
        )}>
          <h1 className="font-heading font-bold text-2xl tracking-tight text-primary-500">
            AURAChain
          </h1>
        </div>
      </div>

      {/* 2. Data Connectivity Status */}
      <div className={clsx(
        "flex items-center transition-all duration-300 py-3",
        isOpen ? "px-3 gap-3" : "justify-center px-3"
      )}>
        {/* Icon - Fixed Width */}
        <div className="flex-shrink-0 flex items-center justify-center w-12 h-12 text-slate-500 dark:text-slate-400">
           <Database size={24} strokeWidth={1.5} />
        </div>

        {/* Content */}
        <div className={clsx(
          "flex-1 flex items-center justify-between overflow-hidden transition-all duration-300",
          isOpen ? "w-auto opacity-100" : "w-0 opacity-0"
        )}>
           <span className="text-sm font-medium text-slate-700 dark:text-slate-300 whitespace-nowrap">
             Data Sources
           </span>
           <span className="flex items-center text-[10px] font-bold text-accent-teal bg-accent-teal/10 px-2 py-0.5 rounded-full">
             <span className="w-1.5 h-1.5 rounded-full bg-accent-teal mr-1.5 animate-pulse"></span>
             3 Active
           </span>
        </div>
      </div>

      {/* 3. NEW SESSION BUTTON (Added here) */}
      <div className={clsx(
        "py-2 transition-all duration-300",
        isOpen ? "px-3" : "px-2 flex justify-center"
      )}>
        <button
          onClick={resetSession}
          className={clsx(
            "flex items-center justify-center transition-all duration-200 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 group",
            // Size logic: w-full when open, w-12 (48px) when collapsed to match other icons
            isOpen ? "w-full py-2.5" : "w-12 h-12" 
          )}
          title="Start New Session"
        >
          <Plus size={20} className="text-slate-500 dark:text-slate-400 group-hover:text-primary-500 transition-colors" />
          {isOpen && (
            <span className="ml-2 text-sm font-medium text-slate-600 dark:text-slate-300 group-hover:text-primary-600 dark:group-hover:text-primary-400 whitespace-nowrap transition-colors">
              New Session
            </span>
          )}
        </button>
      </div>

      {/* 4. Scrollable Session List */}
      <SessionList isOpen={isOpen} />

      {/* 5. Bottom: User Profile */}
      <UserProfile isOpen={isOpen} />
    </aside>
  );
};

export default Sidebar;