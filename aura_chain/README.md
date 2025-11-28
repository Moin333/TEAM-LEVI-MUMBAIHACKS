# MSME Multi-Agent Intelligence Platform

Production-grade backend for an AI-powered business intelligence platform built with multi-agent architecture, inspired by Google/Kaggle's 5-Day AI Agents Intensive.

## 🎯 Overview

This platform implements a sophisticated multi-agent system that analyzes business data, generates insights, creates visualizations, and provides predictive analytics for MSMEs (Micro, Small, and Medium Enterprises).

### Key Features

✅ **Multi-Agent Architecture** - 8 specialized agents working in harmony  
✅ **Model-Agnostic** - Uses Anthropic Claude, Google Gemini, and OpenAI GPT  
✅ **Dataset Flexibility** - Works with any tabular data (CSV, Excel, JSON)  
✅ **Full Observability** - Logs, traces, and metrics (Prometheus-ready)  
✅ **Memory Management** - Session and long-term memory for context  
✅ **MCP Integration** - Model Context Protocol for tool interoperability  
✅ **Production-Ready** - FastAPI, Docker, Redis, PostgreSQL  

## 🏗️ Architecture

### Agent Ecosystem

| Agent | Model | Purpose | Cost | Speed |
|-------|-------|---------|------|-------|
| **Orchestrator** | Claude Sonnet 4.5 | Central controller, query interpretation | High | Medium |
| **Data Harvester** | Gemini 1.5 Flash | Data ingestion & preprocessing | Very Low | Fast |
| **Visualizer** | Claude Sonnet 4 | Chart generation | Medium | Medium |
| **Trend Analyst** | Gemini 2.0 Flash | Pattern detection | Low | Very Fast |
| **Forecaster** | Claude Sonnet 4 | Predictive analytics | Medium | Medium |
| **MCTS Optimizer** | Claude Sonnet 4 | Complex decision optimization | High | Slow |
| **Order Manager** | GPT-4o | Order processing workflows | Medium | Fast |
| **Notifier** | GPT-4o-mini | Notifications | Very Low | Very Fast |

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Gateway                      │
│              /query  /data  /analytics  /health         │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │   Orchestrator Agent      │
         │  (Claude Sonnet 4.5)      │
         └─────────────┬─────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐      ┌─────▼──────┐    ┌─────▼──────┐
│ Data   │      │ Visualizer │    │  Trend     │
│Harvester│      │  Agent     │    │ Analyst    │
└────────┘      └────────────┘    └────────────┘
                                         
┌────────────────────────────────────────────────────┐
│           Core Infrastructure                       │
│  • Memory (Redis) • Database (PostgreSQL)          │
│  • Observability (Logs/Traces/Metrics)             │
│  • MCP Tools • API Clients                         │
└────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- API Keys:
  - Anthropic API key
  - Google AI API key
  - OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd msme_agent_platform
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Verify deployment**
```bash
curl http://localhost:8000/api/v1/health
```

### Alternative: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py

# Run application
uvicorn app.main:app --reload
```

## 📡 API Usage

### 1. Upload Dataset

```bash
curl -X POST http://localhost:8000/api/v1/data/upload \
  -F "file=@sales_data.csv"
```

**Response:**
```json
{
  "dataset_id": "uuid-here",
  "filename": "sales_data.csv",
  "shape": [1000, 12],
  "columns": ["date", "revenue", "product", "region"],
  "preview": [...]
}
```

### 2. Query with Natural Language

```bash
curl -X POST http://localhost:8000/api/v1/orchestrator/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me revenue trends by region and predict next quarter",
    "user_id": "user_123",
    "context": {
      "dataset_id": "uuid-from-upload"
    }
  }'
```

**Response:**
```json
{
  "request_id": "req_uuid",
  "orchestration_plan": {
    "reasoning": "Need trend analysis followed by forecasting",
    "agents": ["data_harvester", "trend_analyst", "forecaster"],
    "execution_plan": [
      {
        "agent": "data_harvester",
        "task": "Load and preprocess data",
        "parameters": {"dataset_id": "..."}
      },
      {
        "agent": "trend_analyst",
        "task": "Analyze revenue trends by region",
        "depends_on": ["data_harvester"]
      },
      {
        "agent": "forecaster",
        "task": "Forecast next quarter revenue",
        "depends_on": ["trend_analyst"]
      }
    ]
  },
  "agent_responses": [
    {
      "agent": "trend_analyst",
      "success": true,
      "data": {
        "insights": {
          "key_findings": ["Revenue growing 15% YoY", "Regional disparities detected"],
          "trends_detected": ["upward_trend", "seasonal_pattern"]
        }
      }
    },
    {
      "agent": "forecaster",
      "success": true,
      "data": {
        "forecasts": {
          "Q1_2025": {"revenue": 1500000, "confidence": 0.87}
        }
      }
    }
  ],
  "success": true
}
```

### 3. Direct Analytics

```bash
curl -X POST http://localhost:8000/api/v1/analytics/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "uuid-here",
    "analysis_type": "trends",
    "parameters": {"focus_columns": ["revenue", "profit"]}
  }'
```

### 4. Health & Metrics

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Prometheus metrics
curl http://localhost:8000/api/v1/health/metrics
```

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

```bash
# API Keys (Required)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/msme_db

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600

# Application
DEBUG=false
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=52428800  # 50MB
```

### Model Selection

Customize models in `app/config.py`:

```python
ORCHESTRATOR_MODEL: str = "claude-sonnet-4-5-20250929"
DATA_HARVESTER_MODEL: str = "gemini-1.5-flash"
TREND_ANALYST_MODEL: str = "gemini-2.0-flash-exp"
# ... etc
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_api/test_orchestrator.py
```

## 📊 Monitoring

### Prometheus Metrics

Available at `http://localhost:9090`

Key metrics:
- `agent_requests_total` - Total agent requests by agent and status
- `agent_request_duration_seconds` - Request latency
- `tool_calls_total` - Tool usage statistics
- `api_tokens_used_total` - Token consumption by provider

### Grafana Dashboards

Access at `http://localhost:3000` (admin/admin)

Pre-configured dashboards for:
- Agent performance
- API usage
- System health
- Cost tracking

### Logs

Structured logs in `logs/` directory:
- JSON format for parsing
- Includes traces for debugging
- Agent activity tracking

## 🛠️ Development

### Adding a New Agent

1. Create agent class in `app/agents/`:

```python
from app.agents.base_agent import BaseAgent, AgentRequest, AgentResponse

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyNewAgent",
            model="model-name",
            api_client=client
        )
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Implementation
        pass
```

2. Register in orchestrator's `AGENT_CAPABILITIES`

3. Add to agent registry in `orchestrator.route_to_agents()`

### Creating MCP Tools

```python
from app.tools.mcp_tools import mcp_server, MCPTool

# Define tool
my_tool = MCPTool(
    name="my_custom_tool",
    description="What it does",
    parameters={"param": "type"}
)

# Register implementation
async def my_tool_function(param: str):
    # Tool logic
    return {"result": "..."}

mcp_server.register_tool(my_tool, my_tool_function)
```

## 🎓 Learning Resources

This project implements concepts from:
- [Google/Kaggle 5-Day AI Agents Intensive](https://www.kaggle.com/learn-guide/5-day-agents)
  - Day 1: Agent foundations & multi-agent systems
  - Day 2: Tools & MCP integration
  - Day 3: Context engineering & memory
  - Day 4: Observability & evaluation
  - Day 5: Production deployment

## 📈 Example Use Cases

### 1. Sales Analysis
```
Query: "Analyze sales performance and identify top products"
Agents: DataHarvester → TrendAnalyst → Visualizer
Output: Trend analysis + charts
```

### 2. Inventory Optimization
```
Query: "Optimize inventory levels to minimize costs"
Agents: DataHarvester → MCTSOptimizer
Output: Optimal stock levels by product
```

### 3. Customer Segmentation
```
Query: "Segment our customers and recommend strategies"
Agents: DataHarvester → TrendAnalyst (clustering)
Output: Customer segments with characteristics
```

### 4. Demand Forecasting
```
Query: "Predict demand for next 6 months"
Agents: DataHarvester → TrendAnalyst → Forecaster
Output: Time series forecast with confidence intervals
```

## 🔐 Security

- API authentication via JWT tokens
- Rate limiting on endpoints
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- Sensitive data in environment variables

## 📦 Deployment

### Docker (Recommended)

```bash
docker-compose up -d
```

### Kubernetes

```bash
# Build image
docker build -t msme-platform:latest .

# Deploy to k8s
kubectl apply -f k8s/
```

### Cloud Platforms

Compatible with:
- AWS (ECS, EKS)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Google & Kaggle for the AI Agents Intensive course
- Anthropic, Google AI, and OpenAI for model APIs
- FastAPI, Pydantic, and the Python ecosystem

## 📞 Support

- Documentation: `/docs` endpoint (Swagger UI)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**Built with ❤️ for MSMEs worldwide**