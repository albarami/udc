# UDC Polaris Multi-Agent Strategic Intelligence System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## Overview

UDC Polaris is an AI-powered strategic intelligence platform that enables United Development Company's CEO to make billion-riyal decisions through real-time multi-agent debates. Seven specialized AI agents analyze strategic questions from different perspectives, producing board-ready recommendations in 12-18 minutes.

**Repository:** https://github.com/albarami/udc

## Key Features

- **7 Specialized AI Agents** - CFO, Market Intelligence, Energy Economics, Regulatory, Sustainability, Contrarian, Orchestrator, Synthesizer
- **Real-Time Debate System** - Round 1 → Tension Identification → Round 2 → Synthesis
- **Interactive Data Gathering** - Agents ask CEO for missing critical data
- **Board-Ready Output** - CEO Decision Sheet with Options A/B/C and quantified trade-offs
- **Qatar Open Data Integration** - 80-100 government datasets from data.gov.qa

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+
- **Vector DB:** ChromaDB
- **Agent Framework:** CrewAI
- **LLM:** Anthropic Claude (Opus 4.1 + Sonnet 4.5)
- **PDF Generation:** WeasyPrint
- **Task Queue:** Celery + Redis

### Frontend
- **Framework:** React 18 + Vite
- **UI Library:** Tailwind CSS
- **Charts:** Recharts
- **WebSocket:** Socket.IO

### Infrastructure
- **Hosting:** Azure App Service (Qatar Central)
- **Monitoring:** Sentry + PostHog
- **CI/CD:** GitHub Actions

## Project Structure

```
udc/
├── backend/
│   ├── app/
│   │   ├── agents/          # CrewAI agent implementations
│   │   │   ├── orchestrator.py
│   │   │   ├── cfo.py
│   │   │   ├── market.py
│   │   │   ├── energy.py
│   │   │   ├── regulatory.py
│   │   │   ├── sustainability.py
│   │   │   ├── contrarian.py
│   │   │   └── synthesizer.py
│   │   ├── core/            # Configuration and utilities
│   │   ├── db/              # Database models
│   │   ├── data/            # Data ingestion pipelines
│   │   ├── api/             # API endpoints
│   │   └── main.py
│   ├── tests/               # Comprehensive test suite
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── pages/           # Page components
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── data/                    # UDC internal data
├── qatar_data/              # Qatar Open Data Portal downloads
│   ├── raw/                 # Raw downloaded data
│   ├── processed/           # Cleaned data
│   └── metadata/            # Catalogs and reports
│
├── docs/                    # Documentation
│   ├── UDC_Polaris_Multi_Agent_System_Specification.md
│   ├── qatar_open_data_scraping_strategy.md
│   ├── qatar_data_scraper.py
│   └── QUICK_START.md
│
├── .github/
│   └── workflows/           # CI/CD pipelines
│
├── PLANNING.md              # Architecture and goals
├── TASK.md                  # Task tracking
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/albarami/udc.git
   cd udc
   ```

2. **Run Qatar Open Data Scraper**
   ```bash
   cd docs
   pip install -r requirements.txt
   python qatar_data_scraper.py
   # Select option 2: Download top 50 priority datasets
   ```

3. **Set up Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your credentials
   
   # Run migrations
   alembic upgrade head
   
   # Start server
   uvicorn app.main:app --reload
   ```

4. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Python formatting and linting
black app/
ruff check app/

# TypeScript/React linting
npm run lint
```

## MVP Timeline

- **Weeks 1-2:** Foundation & Architecture
- **Weeks 3-4:** Single Agent POC (Dr. Omar + Dr. James)
- **Weeks 5-6:** Basic Debate (3 agents)
- **Weeks 7-8:** Complete Agent Council (7 agents) + PDF generation
- **Weeks 9-10:** Frontend UI
- **Week 11:** Demo scenarios & testing
- **Week 12:** Deployment & CEO training

## Success Criteria

- ✅ Analysis completion time: <20 minutes
- ✅ CEO usage: 3-5 times in first month
- ✅ Decision quality rating: >7/10
- ✅ Board acceptance: 1+ Decision Sheet used in actual Board meeting
- ✅ Data gathering efficiency: <10 CEO questions per analysis

## Documentation

- [System Specification](docs/UDC_Polaris_Multi_Agent_System_Specification.md)
- [Qatar Data Scraping Strategy](docs/qatar_open_data_scraping_strategy.md)
- [Quick Start Guide](docs/QUICK_START.md)
- [API Documentation](http://localhost:8000/docs) (when running)

## Contributing

This is a proprietary project for United Development Company Q.P.S.C. Internal team members should follow the development standards outlined in PLANNING.md.

## License

Proprietary - United Development Company Q.P.S.C. © 2025

## Support

For technical support, contact the development team or refer to the documentation in the `docs/` directory.

---

**Built with ❤️ for UDC's Strategic Intelligence**

