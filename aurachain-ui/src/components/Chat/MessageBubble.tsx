import React from 'react';
import { clsx } from 'clsx';
import { BrainCircuit, Clock, ArrowRight } from 'lucide-react';
import { useUIStore } from '../../store/uiStore';

export interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  type?: 'text' | 'analysis';
  status?: 'processing' | 'completed' | 'failed';
  metadata?: {
    agents?: string[];
    progress?: number;
  };
}

interface MessageBubbleProps {
  message: Message;
  isLast: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const { setRightPanelOpen } = useUIStore();

  // Render Analysis Card (Interactive Artifact)
  if (message.type === 'analysis') {
    return (
      <div className="mb-8 max-w-[85%]"> {/* Increased margin for visual separation */}
        <div className="flex items-center text-xs font-bold text-slate-500 mb-2 ml-1 uppercase tracking-wider">
          <BrainCircuit size={14} className="mr-2" />
          AI Orchestrator
        </div>
        
        {/* Interactive Card */}
        <div 
          onClick={() => setRightPanelOpen(true)}
          className="group relative bg-white dark:bg-[#212121] border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm hover:shadow-md hover:border-primary-300 dark:hover:border-primary-700 transition-all cursor-pointer overflow-hidden"
        >
          {/* Left Accent Bar */}
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-accent-amber group-hover:bg-primary-500 transition-colors" />

          <div className="p-5 pl-6">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h4 className="font-heading font-semibold text-lg text-slate-800 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                  {message.text}
                </h4>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Click to view agent execution pipeline
                </p>
              </div>
              <div className="p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-400 group-hover:text-primary-500 group-hover:bg-primary-50 dark:group-hover:bg-primary-900/20 transition-colors">
                <ArrowRight size={18} />
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="flex items-center text-accent-amber">
                  <Clock size={14} className="mr-1.5 animate-pulse" />
                  Processing...
                </span>
                <span className="text-slate-600 dark:text-slate-400">{message.metadata?.progress}%</span>
              </div>
              
              <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="bg-accent-amber h-full rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
                  style={{ width: `${message.metadata?.progress}%` }}
                >
                  <div className="absolute inset-0 bg-white/30 w-full h-full animate-[shimmer_1.5s_infinite]"></div>
                </div>
              </div>

              <div className="pt-3 mt-1 border-t border-slate-100 dark:border-slate-700 text-xs text-slate-500 flex items-center gap-2">
                <span>Agents active:</span>
                <span className="text-slate-700 dark:text-slate-300 font-medium bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                  {message.metadata?.agents?.join(', ')}
                </span>
              </div>
            </div>
          </div>
        </div>
        <span className="text-[10px] text-slate-400 ml-1 mt-2 block">{message.timestamp}</span>
      </div>
    );
  }

  // Render Standard Text Message
  return (
    <div className={clsx("flex w-full mb-6", isUser ? "justify-end" : "justify-start")}>
      <div className={clsx("max-w-[75%] flex flex-col", isUser ? "items-end" : "items-start")}>
        
        {!isUser && (
          <span className="flex items-center text-xs font-bold text-slate-500 mb-1.5 ml-1 uppercase tracking-wider">
            <BrainCircuit size={12} className="mr-1.5" />
            AI Orchestrator
          </span>
        )}

        <div className={clsx(
          "px-5 py-3.5 text-[15px] leading-relaxed shadow-sm",
          isUser 
            ? "bg-primary-600 text-white rounded-2xl rounded-tr-sm" 
            : "bg-white dark:bg-[#212121] border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-2xl rounded-tl-sm"
        )}>
          {message.text}
        </div>
        
        <span className={clsx("text-[10px] text-slate-400 mt-1.5", isUser ? "mr-1" : "ml-1")}>
          {message.timestamp}
        </span>
      </div>
    </div>
  );
};

export default MessageBubble;