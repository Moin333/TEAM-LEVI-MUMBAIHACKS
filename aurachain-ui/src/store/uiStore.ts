import { create } from 'zustand';
import { type Message } from '../components/Chat/MessageBubble';

interface UIState {
  // Layout State
  isSidebarOpen: boolean;
  isRightPanelOpen: boolean;
  rightPanelWidth: number; // New: For resizing
  isDarkMode: boolean;
  
  // Data State
  messages: Message[];
  selectedAgentId: string | null;
  
  // Actions
  toggleSidebar: () => void;
  toggleRightPanel: () => void;
  setRightPanelOpen: (isOpen: boolean) => void;
  setRightPanelWidth: (width: number) => void; // New
  setSelectedAgent: (id: string | null) => void;
  toggleTheme: () => void;
  addMessage: (msg: Message) => void;
  resetSession: () => void; // New Action
  
  // The "Simulation" Action
  runSimulation: (userText: string) => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  isSidebarOpen: true,
  isRightPanelOpen: false, // Start closed (Zero State behavior)
  rightPanelWidth: 450, // Default width
  isDarkMode: false,
  messages: [], // Start empty for Zero State
  selectedAgentId: null,

  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  toggleRightPanel: () => set((state) => ({ isRightPanelOpen: !state.isRightPanelOpen })),
  setRightPanelOpen: (isOpen) => set({ isRightPanelOpen: isOpen }),
  setRightPanelWidth: (width) => set({ rightPanelWidth: width }),
  setSelectedAgent: (id) => set({ selectedAgentId: id, isRightPanelOpen: true }),
  
  toggleTheme: () => set((state) => {
    const newMode = !state.isDarkMode;
    if (newMode) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
    return { isDarkMode: newMode };
  }),

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),

  // Clear messages to reset to Zero State
  resetSession: () => set({ 
    messages: [], 
    isRightPanelOpen: false, 
    selectedAgentId: null 
  }),

  // This creates the "Magic" flow
  runSimulation: (userText) => {
    const { addMessage, setRightPanelOpen } = get();

    // 1. Add User Message immediately
    addMessage({
      id: Date.now().toString(),
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      type: 'text'
    });

    // 2. Simulate AI Thinking (Short delay)
    setTimeout(() => {
      addMessage({
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: "I'll analyze the current supply chain parameters and activate the agent swarm.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'text'
      });
    }, 600);

    // 3. Trigger the "Artifact" and Open Right Panel
    setTimeout(() => {
      // Add the "Artifact Created" card to chat
      addMessage({
        id: (Date.now() + 2).toString(),
        sender: 'ai',
        text: "Agent Workflow Strategy", // Title of the card
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'analysis',
        status: 'processing',
        metadata: { progress: 15, agents: ['Data Harvester', 'Trend Analyst'] }
      });

      // AUTO-OPEN THE CANVAS (The behavior you wanted)
      setRightPanelOpen(true);
      
    }, 1400);
  }
}));