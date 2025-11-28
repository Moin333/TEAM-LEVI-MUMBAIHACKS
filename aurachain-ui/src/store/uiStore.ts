import { create } from 'zustand';
import { api, type OrchestrationPlan } from '../services/api';
import { type Message } from '../components/Chat/MessageBubble';

interface DatasetContext {
  dataset_id: string;
  filename: string;
  shape: [number, number];
  columns: string[];
}

interface UIState {
  // --- Layout State ---
  isSidebarOpen: boolean;
  isRightPanelOpen: boolean;
  rightPanelWidth: number;
  isDarkMode: boolean;
  
  // --- Session Data ---
  sessionId: string | null;
  userId: string;
  messages: Message[];
  
  // --- Agentic State (The "Live" feel) ---
  isThinking: boolean; // Triggers the "Brain" animation
  processingStep: string | null; // e.g. "Data Harvester is working..."
  
  // --- Context ---
  activeDataset: DatasetContext | null;
  selectedAgentId: string | null; // Controls what opens in Right Panel
  
  // --- Orchestration Data ---
  currentPlan: OrchestrationPlan | null;
  agentStatuses: Map<string, 'queued' | 'processing' | 'completed' | 'failed'>;
  
  // --- Actions ---
  toggleSidebar: () => void;
  toggleRightPanel: () => void;
  setRightPanelOpen: (isOpen: boolean) => void;
  setRightPanelWidth: (width: number) => void;
  setSelectedAgent: (id: string | null) => void;
  toggleTheme: () => void;
  
  // --- Core Functional Actions ---
  initializeSession: () => Promise<void>;
  uploadDataset: (file: File) => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  resetSession: () => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  // --- Initial State ---
  isSidebarOpen: true,
  isRightPanelOpen: false,
  rightPanelWidth: 450,
  isDarkMode: false,
  
  sessionId: null,
  userId: 'demo_user_01', // Hardcoded for now
  messages: [],
  
  isThinking: false,
  processingStep: null,
  
  activeDataset: null,
  selectedAgentId: null,
  currentPlan: null,
  agentStatuses: new Map(),

  // --- Layout Actions ---
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  toggleRightPanel: () => set((state) => ({ isRightPanelOpen: !state.isRightPanelOpen })),
  setRightPanelOpen: (isOpen) => set({ isRightPanelOpen: isOpen }),
  setRightPanelWidth: (width) => set({ rightPanelWidth: width }),
  
  // When a user clicks an agent card, open the panel and show details
  setSelectedAgent: (id) => set({ selectedAgentId: id, isRightPanelOpen: !!id }),
  
  toggleTheme: () => set((state) => {
    const newMode = !state.isDarkMode;
    if (newMode) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
    return { isDarkMode: newMode };
  }),

  // --- Functional Actions ---

  // 1. Initialize Session on App Load
  initializeSession: async () => {
    const { userId } = get();
    try {
      const res = await api.createSession(userId);
      // Backend returns request_id, we generate a session ID if backend doesn't provide one explicitly yet
      const newSessionId = res.session_id || `sess_${Date.now()}`;
      set({ sessionId: newSessionId });
      console.log("Session Initialized:", newSessionId);
    } catch (e) {
      console.error("Session Init Failed", e);
      set({ sessionId: `offline_sess_${Date.now()}` }); // Fallback
    }
  },

  // 2. Upload Data
  uploadDataset: async (file: File) => {
    try {
      const res = await api.uploadDataset(file);
      
      set({ 
        activeDataset: {
          dataset_id: res.dataset_id,
          filename: res.filename,
          shape: res.shape,
          columns: res.columns
        }
      });

      // Add a system message confirming upload
      const sysMsg: Message = {
        id: Date.now().toString(),
        sender: 'ai',
        text: `dataset_uploaded`, // Special flag we can catch in MessageBubble if we want custom UI
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'text', // Standard text for now
        metadata: {
            // We use the text field for the UI, but store data here
            displayText: `✅ Ingested **${res.filename}** (${res.shape[0]} rows). Ready for analysis.` 
        }
      };
      
      set(state => ({ messages: [...state.messages, { ...sysMsg, text: sysMsg.metadata?.displayText || "" }] }));

    } catch (e) {
      console.error("Upload failed", e);
      // Error handling UI could go here
    }
  },

  // 3. THE MAIN AGENT LOOP
  sendMessage: async (text: string) => {
    const { sessionId, userId, activeDataset } = get();
    
    // Ensure session
    if (!sessionId) await get().initializeSession();

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // A. Add User Message
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text,
      timestamp,
      type: 'text'
    };

    set(state => ({ 
      messages: [...state.messages, userMsg],
      isThinking: true, // Start the "Brain" animation
      processingStep: "Orchestrator is analyzing request..."
    }));

    try {
      // B. Call Backend
      // We inject dataset_id into context if it exists
      const context = activeDataset ? { dataset_id: activeDataset.dataset_id } : {};
      const response = await api.sendQuery(text, sessionId!, userId, context);

      // --- STAGE 1: Reasoning & Plan ---
      
      // 1. Add "Thinking" Reasoning as a message
      const reasoningMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: response.orchestration_plan.reasoning,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'text'
      };
      set(state => ({ messages: [...state.messages, reasoningMsg] }));

      // 2. Add the "Plan Artifact" (The list of agents)
      const planMsg: Message = {
        id: (Date.now() + 2).toString(),
        sender: 'ai',
        text: 'Agent Execution Strategy', // Title
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'analysis', // This triggers the Workflow Card
        status: 'processing',
        metadata: {
          progress: 0,
          agents: response.orchestration_plan.agents
        }
      };

      set(state => ({ 
        messages: [...state.messages, planMsg],
        currentPlan: response.orchestration_plan,
        isRightPanelOpen: true, // Auto-open sidebar as requested
        selectedAgentId: null // Show the workflow view initially
      }));

      // --- STAGE 2: Simulate Agent Execution Stream ---
      
      // Since backend sends all data at once (for now), we loop with delays 
      // to create the "Live Agent" experience.
      
      const agents = response.agent_responses;
      const totalAgents = agents.length;
      let completedCount = 0;

      for (const agentRes of agents) {
        // Update Status: Agent Processing
        set(state => ({
          processingStep: `Activating ${agentRes.agent}...`,
          agentStatuses: new Map(state.agentStatuses).set(agentRes.agent, 'processing')
        }));

        // 1. Simulate "Working" time (800ms)
        await new Promise(r => setTimeout(r, 800));

        // 2. Add the Agent Result Artifact to Chat
        const resultMsg: Message = {
          id: `${Date.now()}_${agentRes.agent}`,
          sender: 'ai',
          text: agentRes.agent, // Used as title
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          type: 'analysis', // Re-using analysis type to show a card
          status: agentRes.success ? 'completed' : 'failed',
          metadata: {
            data: agentRes.data, // The raw JSON (chart, table, etc)
            summary: "Click to view detailed report"
          }
        };

        // 3. Update State:
        //    - Add message to chat (resultMsg)
        //    - Update Sidebar status to Completed
        //    - Auto-navigate Right Sidebar to this Agent's specific view
        //    - Update the main Plan Card progress
        set(state => ({
          agentStatuses: new Map(state.agentStatuses).set(agentRes.agent, agentRes.success ? 'completed' : 'failed'),
          selectedAgentId: agentRes.agent, // <--- This triggers the "Right Sidebar Loop" you asked for
          
          messages: [
            // A. Map over existing messages to update progress on the Plan Card
            ...state.messages.map(m => 
                m.id === planMsg.id 
                  ? { ...m, metadata: { ...m.metadata, progress: Math.round(((completedCount + 1) / totalAgents) * 100) } } 
                  : m
            ),
            // B. Append the new result message at the end
            resultMsg
          ]
        }));

        completedCount++;
        // Pause briefly so user can see the "Result" before next one starts
        await new Promise(r => setTimeout(r, 1200));
      }

      // --- STAGE 3: Finalize ---
      
      set(state => ({
        isThinking: false,
        processingStep: null,
        selectedAgentId: null, // Return sidebar to workflow view (optional, or keep last agent open)
        // Mark the plan card as 100% complete
        messages: state.messages.map(m => 
            m.id === planMsg.id 
              ? { ...m, status: 'completed', metadata: { ...m.metadata, progress: 100 } } 
              : m
          )
      }));

    } catch (error: any) {
      console.error("Interaction failed", error);
      set(state => ({
        isThinking: false,
        processingStep: null,
        messages: [...state.messages, {
          id: Date.now().toString(),
          sender: 'ai',
          text: `System Error: ${error.message || "Unknown error"}`,
          timestamp,
          type: 'text'
        }]
      }));
    }
  },

  resetSession: () => set({
    messages: [],
    activeDataset: null,
    currentPlan: null,
    agentStatuses: new Map(),
    isRightPanelOpen: false
  })
}));