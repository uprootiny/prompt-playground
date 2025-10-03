# 🎯 Prompt Playground

**Side-by-side LLM comparison tool** for testing prompts across multiple providers.

Compare GPT-4, Claude, and other models instantly with:
- ⚡ **Performance metrics** (latency, cost, quality)
- 📝 **Prompt templates** for common tasks
- 💰 **Real-time cost tracking**
- 🔄 **A/B testing** capabilities

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Anthropic API key (optional)

### Installation

```bash
# Clone repository
git clone <your-repo>
cd prompt-playground

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run Locally

```bash
# Start backend
cd backend
python main.py

# Open browser
open http://localhost:8001
```

### Docker

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8001
```

---

## ✨ Features

### 1. Prompt Templates
Pre-built templates for common tasks:
- **Coding**: Code generation, debugging, refactoring
- **Creative**: Story writing, brainstorming, content creation
- **Analysis**: Data analysis, summarization, research
- **Business**: Email drafts, reports, proposals
- **Education**: Explanations, tutoring, lesson plans
- **Research**: Literature review, hypothesis generation

### 2. Provider Comparison
Compare responses side-by-side:
- **GPT-4** - Most capable, higher cost
- **GPT-3.5 Turbo** - Fast and affordable
- **Claude 3.5 Sonnet** - Long context, nuanced responses

### 3. Cost Tracking
Real-time cost calculation:
- Per-provider cost breakdown
- Input vs output token costs
- Total comparison cost
- Cheapest option highlighting

### 4. Performance Metrics
Track what matters:
- **Latency**: Response time per provider
- **Cost**: Accurate pricing per 1K tokens
- **Quality**: Side-by-side comparison
- **Efficiency**: Cost per second

---

## 🎨 Usage Examples

### Using Templates

1. **Select a template** from the library
2. **Fill in variables** (language, task, etc.)
3. **Choose providers** to compare
4. **Click "Compare Providers"**
5. **Review results** side-by-side

### Custom Prompts

1. Enter your prompt in the **Custom Prompt** field
2. Optionally add a **System Prompt**
3. Select providers and parameters
4. Compare responses

### Template Example

```
Template: Code Generation
Variables:
  - language: Python
  - task: calculate fibonacci numbers

Generated Prompt:
"Write a Python function that calculates fibonacci numbers.
Include docstrings and type hints."

System Prompt:
"You are an expert programmer who writes clean,
efficient, well-documented code."
```

---

## 📊 API Documentation

### Endpoints

#### `GET /api/templates`
Get all available templates
```json
[
  {
    "id": "code_generation",
    "name": "Code Generation",
    "category": "coding",
    "variables": ["language", "task"],
    "example_values": {"language": "Python", "task": "..."}
  }
]
```

#### `POST /api/compare`
Compare prompt across providers
```json
{
  "prompt": "Write a haiku about coding",
  "providers": ["openai", "anthropic"],
  "temperature": 0.7,
  "max_tokens": 1000,
  "system_prompt": "You are a creative poet"
}
```

Response:
```json
{
  "prompt": "...",
  "results": [
    {
      "provider": "openai",
      "model": "gpt-4",
      "response": "Lines of code cascade...",
      "latency": 1.23,
      "cost": 0.0045,
      "input_tokens": 15,
      "output_tokens": 25
    }
  ],
  "fastest": "anthropic",
  "cheapest": "openai",
  "total_cost": 0.0072
}
```

#### `GET /api/pricing`
Get current pricing for all models
```json
{
  "gpt-4": {
    "input_per_1k": 0.03,
    "output_per_1k": 0.06,
    "context_window": 8192
  }
}
```

#### `POST /api/render`
Render a template with values
```json
{
  "template_id": "code_generation",
  "values": {
    "language": "Python",
    "task": "sort a list"
  }
}
```

Full API documentation: http://localhost:8001/api/docs

---

## 🏗️ Architecture

```
prompt-playground/
├── backend/
│   ├── prompts/
│   │   ├── templates.py      # Template library
│   │   └── cost.py           # Cost calculation
│   ├── llm/
│   │   └── providers.py      # OpenAI, Anthropic wrappers
│   ├── config.py             # Configuration
│   ├── middleware.py         # Logging, rate limiting
│   ├── metrics.py            # Application metrics
│   ├── main.py               # FastAPI app
│   └── tests/                # Comprehensive tests
├── frontend/
│   ├── index.html            # Main UI
│   ├── css/styles.css        # Styling
│   └── js/app.js             # Frontend logic
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Tech Stack
- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Vanilla JavaScript (no build step)
- **LLM APIs**: OpenAI, Anthropic
- **Deployment**: Docker, Railway
- **Testing**: pytest

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_templates.py -v
```

---

## 🚢 Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect to Railway
3. Add environment variables:
   ```
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-...
   ```
4. Deploy automatically

### Docker

```bash
docker build -t prompt-playground .
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=sk-... \
  -e ANTHROPIC_API_KEY=sk-... \
  prompt-playground
```

### VPS

```bash
# Clone and setup
git clone <repo>
cd prompt-playground/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env

# Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## 💰 Cost Estimates

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Typical Query |
|-------|----------------------|------------------------|---------------|
| GPT-4 | $30 | $60 | $0.004-0.008 |
| GPT-3.5 Turbo | $0.50 | $1.50 | $0.0002-0.0005 |
| Claude 3.5 Sonnet | $3 | $15 | $0.001-0.003 |

**Typical comparison cost**: $0.01-0.02 (testing 2-3 providers)

---

## 🔒 Security

- API keys stored in environment variables
- Rate limiting (20 requests/minute per IP)
- CORS configured for production
- Security headers middleware
- Input validation with Pydantic

---

## 📈 Metrics

Track usage at `/metrics`:
```json
{
  "total_requests": 142,
  "template_requests": 45,
  "compare_requests": 97,
  "average_response_time": 1.23,
  "total_errors": 2
}
```

---

## 🛠️ Development

### Adding a New Template

```python
# In prompts/templates.py
TEMPLATES["my_template"] = PromptTemplate(
    id="my_template",
    name="My Template",
    template="Do {{action}} with {{subject}}",
    variables=["action", "subject"],
    system_prompt="You are helpful",
    category="custom",
    example_values={
        "action": "analyze",
        "subject": "data"
    },
    description="Custom template description"
)
```

### Adding a New Provider

```python
# In llm/providers.py
class NewProvider(LLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        # Implement API call
        return response_text
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure tests pass: `pytest`
5. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file

---

## 🎯 Use Cases

### Prompt Engineering
- Test prompt variations quickly
- Find optimal temperature settings
- Compare model performance

### Cost Optimization
- Identify cheapest provider for your use case
- Estimate production costs
- A/B test model selection

### Model Selection
- Compare quality across providers
- Test edge cases
- Evaluate reasoning capabilities

### Development
- Prototype LLM features
- Test before production deployment
- Debug prompt issues

---

## 📞 Support

- **Issues**: GitHub Issues
- **API Docs**: http://localhost:8001/api/docs
- **Health**: http://localhost:8001/health

---

**Built with FastAPI + Vanilla JS | Production-ready | Docker-enabled**
