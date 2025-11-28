# app/core/observability.py
from loguru import logger
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import sys
from functools import wraps
import time
from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from app.config import get_settings

settings = get_settings()

# ==================== LOGS ====================
# The diary - structured logging for all events

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AgentLogger:
    """Structured logger for agent activities"""
    
    def __init__(self):
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure loguru with structured format"""
        logger.remove()  # Remove default handler
        
        # Console handler with pretty formatting
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
            level=settings.LOG_LEVEL
        )
        
        # File handler with JSON formatting
        logger.add(
            "logs/agent_platform_{time}.log",
            rotation="500 MB",
            retention="10 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function} | {message}",
            level=settings.LOG_LEVEL,
            serialize=True  # JSON format
        )
    
    def log_agent_activity(
        self,
        agent_name: str,
        activity: str,
        details: Dict[str, Any],
        level: LogLevel = LogLevel.INFO
    ):
        """Log structured agent activity"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "activity": activity,
            "details": details
        }
        
        log_message = f"[{agent_name}] {activity}: {json.dumps(details)}"
        
        if level == LogLevel.DEBUG:
            logger.debug(log_message)
        elif level == LogLevel.INFO:
            logger.info(log_message)
        elif level == LogLevel.WARNING:
            logger.warning(log_message)
        elif level == LogLevel.ERROR:
            logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            logger.critical(log_message)
    
    def log_tool_use(
        self,
        agent_name: str,
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        success: bool = True,
        duration_ms: Optional[float] = None
    ):
        """Log tool usage"""
        details = {
            "tool": tool_name,
            "inputs": inputs,
            "outputs": outputs,
            "success": success,
            "duration_ms": duration_ms
        }
        
        level = LogLevel.INFO if success else LogLevel.ERROR
        self.log_agent_activity(agent_name, "tool_use", details, level)
    
    def log_error(
        self,
        agent_name: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ):
        """Log errors with context"""
        details = {
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace
        }
        self.log_agent_activity(agent_name, "error", details, LogLevel.ERROR)


# ==================== TRACES ====================
# The narrative - end-to-end request flows

# Configure OpenTelemetry
trace.set_tracer_provider(TracerProvider())
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

class AgentTracer:
    """Distributed tracing for agent workflows"""
    
    @staticmethod
    def trace_agent_execution(agent_name: str):
        """Decorator to trace agent execution"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with tracer.start_as_current_span(
                    f"{agent_name}.{func.__name__}"
                ) as span:
                    span.set_attribute("agent.name", agent_name)
                    span.set_attribute("function.name", func.__name__)
                    
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("status", "success")
                        return result
                    except Exception as e:
                        span.set_attribute("status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        raise
                    finally:
                        duration = (time.time() - start_time) * 1000
                        span.set_attribute("duration_ms", duration)
            return wrapper
        return decorator
    
    @staticmethod
    def trace_tool_call(tool_name: str):
        """Decorator to trace tool calls"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with tracer.start_as_current_span(f"tool.{tool_name}") as span:
                    span.set_attribute("tool.name", tool_name)
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("status", "success")
                        return result
                    except Exception as e:
                        span.set_attribute("status", "error")
                        span.set_attribute("error.message", str(e))
                        raise
            return wrapper
        return decorator


# ==================== METRICS ====================
# The health report - quantitative performance data

# Define Prometheus metrics
agent_requests_total = Counter(
    'agent_requests_total',
    'Total number of agent requests',
    ['agent_name', 'status']
)

agent_request_duration = Histogram(
    'agent_request_duration_seconds',
    'Agent request duration in seconds',
    ['agent_name']
)

tool_calls_total = Counter(
    'tool_calls_total',
    'Total number of tool calls',
    ['agent_name', 'tool_name', 'status']
)

tool_call_duration = Histogram(
    'tool_call_duration_seconds',
    'Tool call duration in seconds',
    ['tool_name']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

api_tokens_used = Counter(
    'api_tokens_used_total',
    'Total API tokens used',
    ['provider', 'model']
)

class AgentMetrics:
    """Metrics collection for agents"""
    
    @staticmethod
    def record_agent_request(agent_name: str, duration: float, success: bool):
        """Record agent request metrics"""
        status = "success" if success else "error"
        agent_requests_total.labels(agent_name=agent_name, status=status).inc()
        agent_request_duration.labels(agent_name=agent_name).observe(duration)
    
    @staticmethod
    def record_tool_call(
        agent_name: str,
        tool_name: str,
        duration: float,
        success: bool
    ):
        """Record tool call metrics"""
        status = "success" if success else "error"
        tool_calls_total.labels(
            agent_name=agent_name,
            tool_name=tool_name,
            status=status
        ).inc()
        tool_call_duration.labels(tool_name=tool_name).observe(duration)
    
    @staticmethod
    def record_token_usage(provider: str, model: str, tokens: int):
        """Record API token usage"""
        api_tokens_used.labels(provider=provider, model=model).inc(tokens)
    
    @staticmethod
    def update_active_sessions(count: int):
        """Update active session count"""
        active_sessions.set(count)


# ==================== UNIFIED OBSERVABILITY ====================

class ObservabilityManager:
    """Unified interface for logs, traces, and metrics"""
    
    def __init__(self):
        self.logger = AgentLogger()
        self.tracer = AgentTracer()
        self.metrics = AgentMetrics()
    
    async def observe_agent_execution(
        self,
        agent_name: str,
        func,
        *args,
        **kwargs
    ) -> Any:
        """Observe complete agent execution with logs, traces, and metrics"""
        start_time = time.time()
        success = False
        result = None
        
        try:
            self.logger.log_agent_activity(
                agent_name,
                "execution_started",
                {"args": str(args)[:100], "kwargs": str(kwargs)[:100]}
            )
            
            result = await func(*args, **kwargs)
            success = True
            
            self.logger.log_agent_activity(
                agent_name,
                "execution_completed",
                {"success": True}
            )
            
            return result
            
        except Exception as e:
            self.logger.log_error(
                agent_name,
                type(e).__name__,
                str(e)
            )
            raise
            
        finally:
            duration = time.time() - start_time
            self.metrics.record_agent_request(agent_name, duration, success)


# Global observability manager instance
observability = ObservabilityManager()