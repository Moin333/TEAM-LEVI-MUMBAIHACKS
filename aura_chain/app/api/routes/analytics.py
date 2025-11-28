from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["analytics"])

class AnalyticsRequest(BaseModel):
    dataset_id: str
    analysis_type: str  # 'summary', 'trends', 'forecast', 'optimize'
    parameters: Dict[str, Any] = {}

@router.post("/analyze")
async def run_analysis(request: AnalyticsRequest):
    """
    Run specific analytics on dataset
    Directly invokes appropriate agent
    """
    try:
        # Get dataset
        import redis.asyncio as redis
        from app.config import get_settings
        import pandas as pd
        
        settings = get_settings()
        redis_client = await redis.from_url(settings.REDIS_URL)
        data = await redis_client.get(f"dataset:{request.dataset_id}")
        await redis_client.close()
        
        if not data:
            raise HTTPException(404, "Dataset not found")
        
        df = pd.read_json(data)
        
        # Route to appropriate agent
        from app.agents.trend_analyst import TrendAnalystAgent
        from app.agents.forecaster import ForecasterAgent
        from app.agents.base_agent import AgentRequest
        
        context = {"dataset": df.to_dict('records')}
        
        if request.analysis_type == "trends":
            agent = TrendAnalystAgent()
            query = "Analyze trends in this dataset"
        elif request.analysis_type == "forecast":
            agent = ForecasterAgent()
            query = "Generate forecasts for this dataset"
        else:
            raise HTTPException(400, "Invalid analysis type")
        
        agent_request = AgentRequest(
            query=query,
            context=context,
            parameters=request.parameters
        )
        
        response = await agent.execute_with_observability(agent_request)
        
        return {
            "analysis_type": request.analysis_type,
            "success": response.success,
            "results": response.data,
            "error": response.error
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
