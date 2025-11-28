const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface QueryResponse {
  request_id: string;
  orchestration_plan: OrchestrationPlan;
  agent_responses: AgentResponse[];
  success: boolean;
  error?: string;
}

interface OrchestrationPlan {
  reasoning: string;
  agents: string[];
  execution_plan: ExecutionStep[];
  requires_data: boolean;
}

interface ExecutionStep {
  agent: string;
  task: string;
  parameters: Record<string, any>;
  depends_on: string[];
}

interface AgentResponse {
  agent: string;
  success: boolean;
  data: any;
  error?: string;
}

export const api = {
  // Session Management
  createSession: async (userId: string) => {
    const response = await fetch(`${API_URL}/orchestrator/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: "initialize",
        user_id: userId,
        context: {}
      })
    });
    return response.json();
  },

  // Main query loop
  sendQuery: async (
    query: string, 
    sessionId: string, 
    userId: string,
    context: Record<string, any> = {}
  ): Promise<QueryResponse> => {
    const response = await fetch(`${API_URL}/orchestrator/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        user_id: userId,
        context,
        parameters: {}
      })
    });
    
    if (!response.ok) throw new Error('Query failed');
    return response.json();
  },

  // Data upload
  uploadDataset: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_URL}/data/upload`, {
      method: 'POST',
      body: formData
    });
    
    return response.json();
  },

  // Get dataset
  getDataset: async (datasetId: string) => {
    const response = await fetch(`${API_URL}/data/dataset/${datasetId}`);
    return response.json();
  },

  // Human-in-the-loop approval
  approveOrder: async (orderId: string, sessionId: string) => {
    // You'll need to add this endpoint to your backend
    const response = await fetch(`${API_URL}/orders/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, session_id: sessionId })
    });
    return response.json();
  }
};