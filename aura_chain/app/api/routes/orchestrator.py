from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from app.agents.orchestrator import orchestrator
from app.agents.base_agent import AgentRequest
from app.core.memory import session_manager, context_engineer
import uuid

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])

class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None
    user_id: str
    context: Dict[str, Any] = {}
    parameters: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    request_id: str
    orchestration_plan: Dict[str, Any]
    agent_responses: list[Dict[str, Any]]
    success: bool
    error: str | None = None

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main endpoint: User submits query, orchestrator coordinates agents
    """
    try:
        request_id = str(uuid.uuid4())
        
        # Create or get session
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
            await session_manager.create_session(request.user_id, request.session_id)
        
        # Build context using memory
        context = await context_engineer.build_context(
            session_id=request.session_id,
            user_id=request.user_id,
            current_query=request.query
        )
        
        # Merge with provided context
        context.update(request.context)
        
        # Create agent request
        agent_request = AgentRequest(
            query=request.query,
            context=context,
            session_id=request.session_id,
            user_id=request.user_id,
            parameters=request.parameters
        )
        
        # Get orchestration plan
        orchestrator_response = await orchestrator.execute_with_observability(
            agent_request
        )
        
        if not orchestrator_response.success:
            return QueryResponse(
                request_id=request_id,
                orchestration_plan={},
                agent_responses=[],
                success=False,
                error=orchestrator_response.error
            )
        
        plan = orchestrator_response.data["plan"]
        
        # Execute agents according to plan
        agent_responses = await orchestrator.route_to_agents(plan, agent_request)
        
        # Save conversation to session
        await session_manager.add_message(
            request.session_id,
            "user",
            request.query
        )
        
        # Format response
        response_content = "\n\n".join([
            f"{r.agent_name}: {r.data if r.success else r.error}"
            for r in agent_responses
        ])
        
        await session_manager.add_message(
            request.session_id,
            "assistant",
            response_content
        )
        
        return QueryResponse(
            request_id=request_id,
            orchestration_plan=plan,
            agent_responses=[
                {
                    "agent": r.agent_name,
                    "success": r.success,
                    "data": r.data,
                    "error": r.error
                }
                for r in agent_responses
            ],
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))