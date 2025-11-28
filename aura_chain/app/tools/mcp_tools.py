from typing import Dict, Any, List, Callable
from pydantic import BaseModel
from enum import Enum
from loguru import logger
import asyncio

class ToolStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"

class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    requires_approval: bool = False
    timeout: int = 60

class MCPToolCall(BaseModel):
    """MCP Tool call instance"""
    tool_name: str
    call_id: str
    parameters: Dict[str, Any]
    status: ToolStatus = ToolStatus.PENDING
    result: Any = None
    error: str | None = None

class MCPServer:
    """
    MCP Server for tool management and execution
    Implements long-running operations with human-in-the-loop
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.tool_functions: Dict[str, Callable] = {}
        self.active_calls: Dict[str, MCPToolCall] = {}
    
    def register_tool(
        self,
        tool: MCPTool,
        function: Callable
    ):
        """Register a tool with its implementation"""
        self.tools[tool.name] = tool
        self.tool_functions[tool.name] = function
        logger.info(f"Registered MCP tool: {tool.name}")
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        call_id: str
    ) -> MCPToolCall:
        """Execute a tool call"""
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not registered")
        
        tool = self.tools[tool_name]
        tool_call = MCPToolCall(
            tool_name=tool_name,
            call_id=call_id,
            parameters=parameters
        )
        
        self.active_calls[call_id] = tool_call
        
        try:
            # Check if approval required
            if tool.requires_approval:
                tool_call.status = ToolStatus.AWAITING_APPROVAL
                logger.info(f"Tool {tool_name} awaiting approval: {call_id}")
                # Wait for approval (in production, this would notify user)
                # For now, auto-approve after 1 second
                await asyncio.sleep(1)
            
            tool_call.status = ToolStatus.RUNNING
            
            # Execute tool function
            function = self.tool_functions[tool_name]
            result = await function(**parameters)
            
            tool_call.status = ToolStatus.COMPLETED
            tool_call.result = result
            
            logger.info(f"Tool {tool_name} completed: {call_id}")
            
        except Exception as e:
            tool_call.status = ToolStatus.FAILED
            tool_call.error = str(e)
            logger.error(f"Tool {tool_name} failed: {str(e)}")
        
        return tool_call
    
    def get_tool_call_status(self, call_id: str) -> MCPToolCall:
        """Check status of tool call"""
        return self.active_calls.get(call_id)
    
    async def approve_tool_call(self, call_id: str):
        """Approve a pending tool call"""
        if call_id in self.active_calls:
            tool_call = self.active_calls[call_id]
            if tool_call.status == ToolStatus.AWAITING_APPROVAL:
                # Continue execution
                logger.info(f"Tool call approved: {call_id}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "requires_approval": tool.requires_approval
            }
            for tool in self.tools.values()
        ]


# Global MCP server instance
mcp_server = MCPServer()

# Register data tools
from app.tools.data_tools import DataTools
from app.tools.analysis_tools import AnalysisTools

# Register tools on startup
def register_default_tools():
    """Register all default tools with MCP server"""
    
    # Data filtering tool
    mcp_server.register_tool(
        MCPTool(
            name="filter_data",
            description="Filter dataset based on conditions",
            parameters={
                "df": "DataFrame",
                "conditions": "Dict[str, Any]"
            }
        ),
        DataTools.filter_data
    )
    
    # Aggregation tool
    mcp_server.register_tool(
        MCPTool(
            name="aggregate_data",
            description="Group and aggregate data",
            parameters={
                "df": "DataFrame",
                "group_by": "List[str]",
                "aggregations": "Dict[str, str]"
            }
        ),
        DataTools.aggregate_data
    )
    
    # Outlier detection tool
    mcp_server.register_tool(
        MCPTool(
            name="detect_outliers",
            description="Detect outliers in data",
            parameters={
                "df": "DataFrame",
                "column": "str",
                "method": "str"
            }
        ),
        AnalysisTools.detect_outliers
    )
    
    # Customer segmentation (requires approval)
    mcp_server.register_tool(
        MCPTool(
            name="segment_customers",
            description="Perform customer segmentation",
            parameters={
                "df": "DataFrame",
                "features": "List[str]",
                "n_clusters": "int"
            },
            requires_approval=True  # Sensitive operation
        ),
        AnalysisTools.segment_customers
    )
    
    logger.info("Default MCP tools registered")