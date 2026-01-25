# DebugAI - AI-Powered Error Analysis Tool

An intelligent debugging assistant that analyzes error logs and provides AI-generated solutions using RAG (Retrieval-Augmented Generation) with Stack Overflow knowledge base.

## 🚀 Live Demo

- **Frontend**: [https://debugai.vercel.app/](https://debugai.vercel.app/)
- **Backend API**: [https://debugai-production.up.railway.app/](https://debugai-production.up.railway.app/)
- **API Docs**: [https://debugai-production.up.railway.app/docs](https://debugai-production.up.railway.app/docs)

## Architecture Overview

```mermaid
graph TB
    subgraph Frontend["Frontend (Next.js)"]
        UI[Web UI]
        API_CLIENT[API Service]
    end

    subgraph Backend["Backend (FastAPI)"]
        ROUTER[API Router]
        PARSER[Error Parser]
        VECTOR[Vector Store]
        LLM[LLM Analyzer]
        CACHE[Redis Cache]
        COST[Cost Tracker]
    end

    subgraph Database["Database (Supabase)"]
        PG[(PostgreSQL)]
        PGVECTOR[(pgvector)]
    end

    subgraph External["External Services"]
        OPENAI[GitHub Models API]
        SO[Stack Overflow Data]
    end

    UI --> API_CLIENT
    API_CLIENT --> ROUTER
    ROUTER --> CACHE
    CACHE --> PARSER
    PARSER --> VECTOR
    VECTOR --> PGVECTOR
    VECTOR --> LLM
    LLM --> OPENAI
    LLM --> COST
    COST --> PG
    PARSER --> PG
    SO --> PG
```

## Analysis Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Cache
    participant Parser
    participant VectorStore
    participant LLM
    participant Database

    User->>Frontend: Paste Error Log
    Frontend->>Cache: Check Cache

    alt Cache Hit
        Cache-->>Frontend: Return Cached Analysis
    else Cache Miss
        Cache->>Parser: Parse Error
        Parser->>Database: Store Parsed Error
        Parser->>VectorStore: Search Similar Errors
        VectorStore->>Database: Query pgvector
        Database-->>VectorStore: Return Top K Results
        VectorStore->>LLM: Analyze with Context
        LLM->>Database: Track API Cost
        LLM-->>Parser: Return Analysis
        Parser->>Database: Store Analysis
        Parser->>Cache: Cache Result (24h TTL)
        Cache-->>Frontend: Return Analysis
    end

    Frontend-->>User: Display Solutions
```

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js 14 (TypeScript, React)
- **Database**: Supabase (PostgreSQL with pgvector)
- **Vector Store**: Supabase pgvector for embeddings
- **Caching**: Redis (24h TTL for analyses)
- **AI/LLM**: GitHub Models (Azure OpenAI)
  - GPT-4o-mini for error analysis
  - text-embedding-3-small for vector embeddings
- **Deployment**: Railway (Backend), Vercel (Frontend)

## Features

- **Intelligent Error Parsing**: Automatically extracts error type, message, stack trace, and context from logs
- **RAG-Powered Analysis**: Searches Stack Overflow knowledge base using semantic similarity
- **AI-Generated Solutions**: GPT-4o-mini provides ranked solutions with code examples and confidence scores
- **Multi-Language Support**: Currently supports Python, JavaScript, TypeScript, React, Node.js, Django, FastAPI
- **Batch Scraping**: Automated Stack Overflow scraping across multiple tags
- **Vector Search**: Fast semantic search using Supabase pgvector
- **Persistent Storage**: All errors and analyses stored in Supabase PostgreSQL
- **Redis Caching**: Two-level cache for analyses and search results (24h TTL)
- **Cost Tracking**: Real-time API cost monitoring with daily/operation breakdown
- **Analytics Dashboard**: Comprehensive metrics including success rates, language breakdown, cache performance
- **Feedback System**: User feedback collection to improve solution quality

## Project Structure

```
debugAi/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app & endpoints
│   │   ├── api/
│   │   │   ├── analyze.py               # Analysis endpoints
│   │   │   ├── analytics.py             # Analytics & metrics endpoints
│   │   │   ├── feedback.py              # Feedback endpoints
│   │   │   ├── cost_routes.py           # Cost tracking endpoints
│   │   │   ├── embeddings_routes.py     # Embeddings endpoints
│   │   │   └── scrape_routes.py         # Scraping endpoints
│   │   ├── core/                        # Core configuration
│   │   ├── db/
│   │   │   ├── models/                  # SQLAlchemy models
│   │   │   │   ├── error.py             # ParsedError, Analysis models
│   │   │   │   ├── feedback.py          # Feedback model
│   │   │   │   └── cost.py              # CostTracking model
│   │   │   ├── crud/                    # Database operations
│   │   │   │   ├── error_crud.py        # Error CRUD operations
│   │   │   │   ├── feedback_crud.py     # Feedback CRUD operations
│   │   │   │   ├── cost_crud.py         # Cost tracking CRUD
│   │   │   │   └── analytics_crud.py    # Analytics CRUD operations
│   │   │   └── session.py               # DB session management
│   │   ├── services/
│   │   │   ├── parser.py                # Error log parsing
│   │   │   ├── supabase_vector_store.py # Vector store operations
│   │   │   ├── llm_analyzer.py          # LLM error analysis
│   │   │   ├── cache.py                 # Redis caching service
│   │   │   └── cost_tracker.py          # API cost tracking
│   │   ├── schemas/                     # Pydantic models
│   │   ├── scripts/
│   │   │   ├── scrape_stackoverflow.py  # SO scraper
│   │   │   ├── batch_scrape.py          # Batch scraping
│   │   │   └── create_embeddings.py     # Generate embeddings
│   │   └── utils/                       # Utility functions
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Main UI
│   │   ├── analytics/page.tsx           # Analytics dashboard
│   │   └── layout.tsx
│   ├── components/
│   │   ├── InputSection.tsx             # Error input
│   │   └── ResultsSection.tsx           # Results display
│   ├── services/
│   │   └── api.ts                       # API client
│   ├── Dockerfile
│   └── .env.local.example
├── docker-compose.yml
├── APPLICATION_FLOW.md                   # Detailed flow documentation
└── README.md
```

## Quick Start

### Prerequisites
- Docker installed on your machine
- Docker Compose installed
- GitHub Personal Access Token (for GitHub Models API)
- Supabase project with pgvector enabled
- Stack Exchange API key (optional, for scraping)

### Setup Steps

1. **Clone and navigate to the project**
   ```bash
   git clone <repository-url>
   cd debugAi
   ```

2. **Create environment files**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

3. **Configure Backend Environment** (`backend/.env`)
   ```bash
   # Database (Supabase PostgreSQL)
   DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

   # GitHub Models API (for LLM and embeddings)
   GITHUB_TOKEN=github_pat_xxxxxxxxxxxxx

   # Redis (optional - for caching)
   REDIS_URL=redis://localhost:6379

   # CORS (comma-separated origins)
   ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

   # Stack Exchange API (optional)
   STACKEXCHANGE_API_KEY=your_key_here
   ```

4. **Configure Frontend Environment** (`frontend/.env.local`)
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. **Start all services with Docker**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - FastAPI backend on port `8000`
   - Next.js frontend on port `3000`

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Initial Setup (First Time)

1. **Initialize Database Tables**
   The database tables are automatically created on first startup via SQLAlchemy.

2. **Scrape Stack Overflow Posts** (Optional but recommended)
   ```bash
   # Scrape posts for multiple tags at once
   curl -X POST http://localhost:8000/api/scrape/batch

   # Or scrape specific tag
   curl -X POST http://localhost:8000/api/scrape \
     -H "Content-Type: application/json" \
     -d '{"tag": "python", "limit": 500}'
   ```

3. **Create Embeddings**
   ```bash
   curl -X POST http://localhost:8000/api/embeddings/create
   ```

### Production Deployment

**Live Application:**
- **Frontend**: https://debugai.vercel.app/
- **Backend API**: https://debugai-production.up.railway.app/
- **API Documentation**: https://debugai-production.up.railway.app/docs

**Deployment Platforms:**
- **Backend**: Railway
- **Frontend**: Vercel

**Deployment Checklist:**
1. Set all environment variables in Railway/Vercel dashboards
2. Ensure `GITHUB_TOKEN` has no trailing whitespace/newlines
3. Configure CORS origins to include your production domain:
   ```
   ALLOWED_ORIGINS=https://debugai.vercel.app
   ```
4. Use Supabase connection pooler for better performance
5. Verify pgvector extension is enabled in Supabase

## Docker Commands

### Start services in background
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop services and remove volumes (clean database)
```bash
docker-compose down -v
```

### View logs
```bash
docker-compose logs -f
```

### View logs for specific service
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Rebuild containers
```bash
docker-compose up --build
```

### Access backend container shell
```bash
docker exec -it debugai-backend sh
```

### Access frontend container shell
```bash
docker exec -it debugai-frontend sh
```

### Access PostgreSQL database
```bash
docker exec -it debugai-db psql -U debugai -d debugai_db
```

## API Endpoints

```mermaid
graph LR
    subgraph Analysis
        A1[POST /api/analyze]
        A2[POST /api/feedback]
    end

    subgraph Analytics
        B1[GET /api/analytics/overview]
        B2[GET /api/analytics/language-breakdown]
        B3[GET /api/analytics/feedback-stats]
        B4[GET /api/analytics/cache-stats]
        B5[GET /api/analytics/costs]
    end

    subgraph Data
        C1[POST /api/scrape]
        C2[POST /api/scrape/batch]
        C3[POST /api/embeddings/create]
    end
```

### Core Endpoints

- **POST /api/analyze** - Analyze error log and get AI-generated solutions
  ```json
  {
    "query": "Traceback (most recent call last):\n  File \"app.py\"...",
    "limit": 5
  }
  ```

- **POST /api/feedback** - Submit feedback on a solution
  ```json
  {
    "analysis_id": 1,
    "solution_index": 0,
    "worked": true,
    "notes": "Fixed my issue!"
  }
  ```

- **POST /api/scrape** - Scrape Stack Overflow posts for a specific tag
  ```json
  {
    "tag": "python",
    "limit": 500
  }
  ```

- **POST /api/scrape/batch** - Batch scrape multiple tags
  - Python: 500 posts
  - JavaScript: 500 posts
  - React: 300 posts
  - TypeScript: 300 posts
  - Node.js: 200 posts
  - Django: 150 posts
  - FastAPI: 100 posts

- **POST /api/embeddings/create** - Generate embeddings for scraped posts

- **GET /health** - Health check endpoint

### Analytics Endpoints

- **GET /api/analytics/overview** - System-wide analytics (total analyses, errors, avg time, success rate)
- **GET /api/analytics/language-breakdown** - Error distribution by programming language
- **GET /api/analytics/feedback-stats** - Feedback statistics with solution breakdown
- **GET /api/analytics/cache-stats** - Redis cache performance metrics
- **GET /api/analytics/costs?days=30** - API cost tracking with daily breakdown

## How It Works

```mermaid
flowchart TD
    A[User Pastes Error Log] --> B{Check Redis Cache}
    B -->|Cache Hit| C[Return Cached Analysis]
    B -->|Cache Miss| D[Parse Error Log]
    D --> E[Extract Error Type, Message, Stack Trace]
    E --> F[Store Parsed Error in DB]
    F --> G[Vector Search in pgvector]
    G --> H[Retrieve Top K Similar Posts]
    H --> I[Build RAG Context]
    I --> J[Send to GPT-4o-mini]
    J --> K[Track API Cost]
    K --> L[Generate Analysis]
    L --> M[Store Analysis in DB]
    M --> N[Cache Result - 24h TTL]
    N --> O[Return to Frontend]
    C --> O
    O --> P[Display Solutions with Syntax Highlighting]
    P --> Q{User Feedback}
    Q -->|Worked/Didn't Work| R[Store Feedback]
```

1. **User Input**: Paste error log into the frontend
2. **Cache Check**: Check Redis for cached analysis (24h TTL)
3. **Error Parsing**: Backend extracts error type, message, stack trace, file path, and line number
4. **Vector Search**: Searches Stack Overflow knowledge base using semantic similarity
5. **RAG Context**: Top 3-5 most relevant posts are retrieved (distance threshold: 0.6)
6. **LLM Analysis**: GPT-4o-mini analyzes error with context and generates:
   - Root cause explanation
   - Step-by-step reasoning
   - 2-3 ranked solutions with code examples
   - Confidence scores (0-1)
   - Source URLs from Stack Overflow
7. **Cost Tracking**: API usage and costs are logged for monitoring
8. **Database Storage**: Error and analysis are stored in Supabase
9. **Caching**: Result is cached in Redis for 24 hours
10. **Response**: Frontend displays solutions with syntax-highlighted code
11. **Feedback**: Users can provide feedback on solution effectiveness

See [APPLICATION_FLOW.md](APPLICATION_FLOW.md) for detailed flow documentation.

## Development

### Hot Reload
Both frontend and backend support hot reload:
- Backend: Changes to Python files will automatically reload the FastAPI server
- Frontend: Changes to TypeScript/React files will trigger Next.js hot reload

### Adding Python Dependencies
1. Add the package to `backend/requirements.txt`
2. Rebuild the backend container:
   ```bash
   docker-compose up --build backend
   ```

### Adding Node Dependencies
1. Add the package to `frontend/package.json` or run:
   ```bash
   docker-compose exec frontend npm install <package-name>
   ```
2. Restart the frontend service:
   ```bash
   docker-compose restart frontend
   ```

### Running Without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Database Schema

```mermaid
erDiagram
    PARSED_ERRORS ||--o{ ANALYSES : has
    ANALYSES ||--o{ FEEDBACK : receives
    STACKOVERFLOW_POSTS ||--o{ EMBEDDINGS : generates
    COST_TRACKING

    PARSED_ERRORS {
        int id PK
        text raw_error_log
        string error_type
        string error_message
        string language
        string framework
        string file_name
        int line_number
        string function_name
        jsonb stack_trace
        float confidence_score
        timestamp created_at
    }

    ANALYSES {
        int id PK
        int parsed_error_id FK
        text root_cause
        text reasoning
        jsonb solutions
        int sources_used
        int analysis_time
        timestamp created_at
    }

    FEEDBACK {
        int id PK
        int analysis_id FK
        int solution_index
        boolean worked
        text notes
        timestamp created_at
    }

    STACKOVERFLOW_POSTS {
        int id PK
        int question_id
        string title
        text question_body
        text answer_body
        array tags
        int votes
        string url
        timestamp created_at
        timestamp scraped_at
    }

    EMBEDDINGS {
        int id PK
        text content
        vector embedding
        jsonb metadata
        timestamp created_at
    }

    COST_TRACKING {
        int id PK
        string operation
        string model
        float cost
        int prompt_tokens
        int completion_tokens
        int total_tokens
        timestamp created_at
    }
```

### Tables

**parsed_errors**
- Stores parsed error information
- Fields: id, raw_error_log, error_type, error_message, language, framework, file_name, line_number, function_name, stack_trace (JSONB), confidence_score, created_at

**analyses**
- Stores LLM-generated analysis results
- Fields: id, parsed_error_id (FK), root_cause, reasoning, solutions (JSONB), sources_used, analysis_time, created_at

**feedback**
- Stores user feedback on solutions
- Fields: id, analysis_id (FK), solution_index, worked, notes, created_at

**stackoverflow_posts**
- Stores scraped Stack Overflow posts
- Fields: id, question_id, title, question_body, answer_body, tags (array), votes, url, created_at, scraped_at

**embeddings** (Supabase pgvector)
- Stores vector embeddings for semantic search
- Fields: id, content, embedding (vector), metadata (JSONB), created_at

**cost_tracking**
- Stores API cost records for monitoring
- Fields: id, operation, model, cost, prompt_tokens, completion_tokens, total_tokens, created_at

### Database Management

Connect to Supabase dashboard or use direct connection:
```bash
psql "postgresql://user:pass@host:port/dbname"
```

## Troubleshooting

### "Illegal header value" Error
**Symptom**: `httpcore.LocalProtocolError: Illegal header value`

**Cause**: API keys in environment variables have trailing newlines/whitespace

**Solution**: Ensure `GITHUB_TOKEN` and other API keys are stripped of whitespace. This is now handled automatically in the code with `.strip()`.

### Port Already in Use
If you get port conflict errors, either:
- Stop the conflicting service on your machine
- Change ports in `docker-compose.yml`

### Container Won't Start
Check logs:
```bash
docker-compose logs <service-name>
```

### Clean Start
Remove all containers and volumes:
```bash
docker-compose down -v
docker-compose up --build
```

### Frontend Can't Reach Backend
Make sure `NEXT_PUBLIC_API_URL` in frontend environment points to `http://localhost:8000` for local development or your production backend URL for production.

### CORS Errors
Ensure your frontend origin is included in `ALLOWED_ORIGINS` environment variable on the backend:
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Vector Search Returns No Results
1. Ensure embeddings are created: `POST /api/embeddings/create`
2. Check that Stack Overflow posts are scraped: `POST /api/scrape/batch`
3. Verify Supabase pgvector extension is enabled

### Database Connection Issues
- Check `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/dbname`
- Use Supabase connection pooler URL for better performance
- Ensure pgvector extension is installed in your Supabase project

## Performance

| Stage | Typical Duration | Notes |
|-------|------------------|-------|
| Cache Check | 1-5ms | Redis lookup |
| Parse Error | 10-50ms | Regex-based, very fast |
| Vector Search | 50-200ms | Depends on collection size |
| DB Insert (Error) | 20-100ms | Async operation |
| LLM Analysis | 2-5 seconds | Main bottleneck |
| DB Insert (Analysis) | 20-100ms | Async operation |
| Cache Write | 1-5ms | Redis set with TTL |
| **Total (Cache Miss)** | **2.5-6 seconds** | Full pipeline |
| **Total (Cache Hit)** | **5-20ms** | Cached response |

## Architecture Highlights

```mermaid
graph TB
    subgraph Caching Layer
        REDIS[Redis Cache]
        L1[Analysis Cache<br/>24h TTL]
        L2[Search Cache<br/>24h TTL]
    end

    subgraph Cost Management
        CT[Cost Tracker]
        CM[Cost Model]
    end

    REDIS --> L1
    REDIS --> L2
    CT --> CM

    style REDIS fill:#dc382d,color:#fff
    style CT fill:#22c55e,color:#fff
```

- **RAG (Retrieval-Augmented Generation)**: Combines semantic search with LLM generation for context-aware solutions
- **Vector Search**: Uses pgvector for fast semantic similarity search
- **Two-Level Caching**: Redis cache for analyses and search results with 24-hour TTL
- **Cost Tracking**: Real-time monitoring of API costs with breakdown by operation
- **Async Operations**: FastAPI async endpoints with SQLAlchemy async for better performance
- **Structured Output**: Uses OpenAI function calling for reliable JSON responses
- **Multi-stage Pipeline**: Cache Check → Parse → Search → Analyze → Store → Cache
- **Feedback Loop**: User feedback collection for continuous improvement

## Technologies Used

- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **Next.js 14**: React framework with server-side rendering
- **SQLAlchemy**: Python ORM with async support
- **Supabase**: PostgreSQL with pgvector extension
- **Redis**: In-memory caching for analyses and search results
- **GitHub Models**: Azure OpenAI endpoints (GPT-4o-mini, text-embedding-3-small)
- **Docker**: Containerization for consistent environments
- **Railway**: Backend deployment platform
- **Vercel**: Frontend deployment platform

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature-name`
5. Open a pull request

## License

[Add your license here]

## Acknowledgments

- Stack Overflow for community knowledge
- GitHub Models for AI services
- Supabase for database and vector storage

## Contact

**Sai Krishna**
- Email: kokkulasaikrishna1288@gmail.com
- Project: [DebugAI on GitHub](https://github.com/saikrishna01301/debug.ai)

---

**Last Updated**: 2026-01-23
**Version**: 1.1
