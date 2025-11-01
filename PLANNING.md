# UDC Polaris - Planning & Architecture

**Document Version:** 1.0  
**Last Updated:** October 31, 2025  
**Project:** UDC Polaris Multi-Agent Strategic Intelligence System

---

## Project Vision

Build an AI-powered strategic intelligence platform where 7 specialized agents debate strategic questions in real-time, producing quantified trade-offs and board-ready decision sheets for UDC's CEO in under 20 minutes.

## Architecture Overview

### Multi-Agent System

**7 Specialized Agents:**

1. **Dr. Omar Al-Thani** - Orchestrator & Debate Facilitator
2. **Dr. James Chen** - CFO & Financial Risk Strategist
3. **Dr. Noor Al-Mansouri** - Market & Competitive Intelligence
4. **Dr. Khalid Al-Attiyah** - Energy Economics & District Cooling Specialist
5. **Dr. Fatima Al-Sulaiti** - Regulatory & Qatar National Vision 2030 Alignment
6. **Dr. Marcus Weber** - Sustainability & ESG Performance
7. **Dr. Sarah Mitchell** - Contrarian & Risk Challenger
8. **Dr. Hassan Al-Kuwari** - Chief Strategy Synthesizer

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15+ (structured data)
- ChromaDB (vector embeddings)
- CrewAI (multi-agent coordination)
- Anthropic Claude (Opus 4.1 for Synthesizer, Sonnet 4.5 for specialists)
- WeasyPrint (PDF generation)
- Celery + Redis (async processing)

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- Recharts (visualizations)
- Socket.IO (real-time updates)

**Infrastructure:**
- Azure App Service (Qatar Central)
- Azure Database for PostgreSQL
- Azure Redis Cache
- Azure Blob Storage

## Core Principles

### 1. File & Code Structure

- **Maximum 500 lines per file** - No exceptions, refactor immediately
- **Modular architecture** - Group by feature/responsibility
- **Relative imports** within packages
- **Consistent naming** conventions (snake_case for Python, camelCase for TypeScript)

### 2. Testing Requirements

- **Pytest tests for ALL new features** (functions, classes, routes)
- Tests in `/tests` folder mirroring app structure
- Required test cases:
  - Expected use case
  - Edge case
  - Failure case
- Update existing tests when logic changes
- Tests must pass before marking task complete

### 3. Code Standards

**Python:**
```python
# Required: Type hints, PEP8, black formatting, pydantic validation
def example_function(param1: str, param2: int) -> dict:
    """
    Brief summary.
    
    Args:
        param1 (str): Description.
        param2 (int): Description.
        
    Returns:
        dict: Description.
    """
    # Reason: Explain complex logic with why, not what
    return {"result": "value"}
```

**TypeScript/React:**
```typescript
// Required: Type safety, functional components, proper hooks
interface ExampleProps {
  param1: string;
  param2: number;
}

export const ExampleComponent: React.FC<ExampleProps> = ({ param1, param2 }) => {
  // Component implementation
  return <div>{param1}</div>;
};
```

### 4. Documentation

- **Google-style docstrings** for every function
- **README.md updates** when features/dependencies change
- **Inline comments** for complex logic with `# Reason:` prefix
- **API documentation** auto-generated via FastAPI

## Development Workflow

### Before Every Session

1. Read Multi-Agent System Specification document
2. Review task-specific documentation
3. Check current task in TASK.md
4. Understand existing code structure

### During Development

1. Write code following all standards
2. Create comprehensive tests
3. Run `pytest tests/ -v` to verify
4. Update documentation if needed
5. Commit with descriptive message

### Task Completion

1. Ensure all tests pass
2. Mark task complete in TASK.md
3. Update README.md if needed
4. Commit changes

## Agent Design Framework

Each agent must include:

1. **Persona Definition**
   - Background and expertise
   - Decision-making framework
   - Typical concerns and priorities

2. **Data Requirements**
   - Primary data sources
   - Data access patterns
   - Citation requirements

3. **Reasoning Logic**
   - Domain-specific analysis approach
   - Key metrics and thresholds
   - Interaction protocols with other agents

4. **Output Format**
   - Structured response template
   - Required elements (analysis, risks, questions)
   - Token limits (2,000 for specialists, 4,000 for synthesizer)

## Data Architecture

### Qatar Open Data Integration

**Categories:**
- `real_estate/` - Property transactions, prices, occupancy
- `population/` - Demographics, migration, households
- `economy/` - GDP, inflation, CPI, trade
- `tourism/` - Hotel occupancy, visitor statistics
- `labor/` - Employment, wages, workforce
- `energy/` - Electricity, cooling, consumption
- `infrastructure/` - Development, transport

**Agent Mappings:**
- Dr. Noor (Market) → real_estate + economy + tourism
- Dr. James (CFO) → economy + real_estate
- Dr. Khalid (Energy) → energy + infrastructure
- Dr. Fatima (Regulatory) → population + infrastructure
- Dr. Marcus (Sustainability) → energy + infrastructure
- Dr. Sarah (Risk) → all categories

### Data Storage

1. **Raw Data** - `qatar_data/raw/` (organized by category)
2. **Processed Data** - PostgreSQL tables (structured queries)
3. **Embeddings** - ChromaDB (semantic search)
4. **Metadata** - Catalogs, quality reports, audit logs

## Security & Compliance

### Data Governance

- All data access logged to audit trail
- CEO context stored with encryption
- Session data temporary (within single analysis)
- No PII storage in MVP (CEO only user)

### API Security

- Azure AD authentication (if needed)
- Rate limiting on LLM API calls
- Cost controls and spending caps
- Error handling and graceful degradation

## Cost Management

### LLM API Costs

**Token Limits:**
- Specialists: 2,000 tokens max
- Synthesizer: 4,000 tokens max
- Total per analysis: ~20,000 tokens

**Estimated Costs:**
- Per analysis: ~QR 400
- 100 analyses/month: QR 40,000
- MVP development: QR 80,000

**Controls:**
- Per-session token budget alerts
- Monthly spending cap in Azure
- Usage analytics via PostHog
- Response caching for identical queries

### Qatar Data Costs

- Development: QR 0 (code provided)
- API Access: QR 0 (public)
- Operational: QR 4,800/month
- ROI: 10-20x (replaces QR 50-100K/month consulting)

## Quality Assurance

### Code Review Checklist

- [ ] Follows 500-line-per-file limit
- [ ] All functions have type hints and docstrings
- [ ] Tests written for all new code
- [ ] All tests pass
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Documentation updated

### Agent Quality Validation

- [ ] Persona is distinct and consistent
- [ ] Data citations are accurate
- [ ] Recommendations are actionable
- [ ] Token usage within limits
- [ ] Responses are coherent and relevant
- [ ] Tensions identified are genuine
- [ ] Trade-offs are quantified

## Constraints & Exclusions (MVP)

### ❌ NOT in MVP Scope

- Internal system integrations (ERP, Property Management)
- Automated data pipelines (manual Qatar data updates for MVP)
- Predictive analytics (machine learning models)
- Multi-session memory (long-term learning)
- Multi-user access (CEO only)
- Mobile app (web only)
- Voice interface
- Admin panel
- Authentication UI (if needed, Azure AD handles it)

### ✅ MVP Focus

- Question → Debate → Decision Sheet workflow
- 7-agent debate system
- Interactive CEO data gathering
- Real-time visualization
- PDF Decision Sheet generation
- Qatar Open Data integration
- 3 pre-built demo scenarios

## Success Metrics

### Quantitative

- Analysis completion time: <20 minutes
- CEO usage: 3-5 times in first month
- Decision quality rating: >7/10 average
- Board acceptance: 1+ Decision Sheet used
- Data gathering: <10 questions per analysis

### Qualitative

- "Faster than consultants"
- "Shows perspectives I hadn't considered"
- "Trade-off analysis is clear and actionable"
- "Can defend this to the Board"

## References

- [System Specification](docs/UDC_Polaris_Multi_Agent_System_Specification.md)
- [Strategic Intelligence Report](docs/udc_strategic_intelligence.md)
- [Qatar Data Strategy](docs/qatar_open_data_scraping_strategy.md)
- [Quick Start Guide](docs/QUICK_START.md)

---

**This is a real production system - treat seriously. Always seek best solution, not quickest.**

