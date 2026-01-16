# DebugAI - AI-Powered Error Analysis Tool

An intelligent debugging assistant that analyzes error logs and provides AI-generated solutions using RAG (Retrieval-Augmented Generation) with Stack Overflow knowledge base.

## 🚀 Live Demo

- **Frontend**: [https://debugai.vercel.app/](https://debugai.vercel.app/)
- **Backend API**: [https://debugai-production.up.railway.app/](https://debugai-production.up.railway.app/)
- **API Docs**: [https://debugai-production.up.railway.app/docs](https://debugai-production.up.railway.app/docs)

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js 14 (TypeScript, React)
- **Database**: Supabase (PostgreSQL with pgvector)
- **Vector Store**: Supabase pgvector for embeddings
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

## Project Structure

```
debugAi/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app & endpoints
│   │   ├── db/
│   │   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── crud/                    # Database operations
│   │   │   └── session.py               # DB session management
│   │   ├── services/
│   │   │   ├── parser.py                # Error log parsing
│   │   │   ├── supabase_vector_store.py # Vector store operations
│   │   │   └── llm_analyzer.py          # LLM error analysis
│   │   ├── schemas/                     # Pydantic models
│   │   └── scripts/
│   │       ├── scrape_stackoverflow.py  # SO scraper
│   │       ├── batch_scrape.py          # Batch scraping
│   │       └── create_embeddings.py     # Generate embeddings
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Main UI
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

### Core Endpoints

- **POST /api/analyze** - Analyze error log and get AI-generated solutions
  ```json
  {
    "query": "Traceback (most recent call last):\n  File \"app.py\"...",
    "limit": 5
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

## How It Works

1. **User Input**: Paste error log into the frontend
2. **Error Parsing**: Backend extracts error type, message, stack trace, file path, and line number
3. **Vector Search**: Searches Stack Overflow knowledge base using semantic similarity
4. **RAG Context**: Top 3-5 most relevant posts are retrieved (distance threshold: 0.6)
5. **LLM Analysis**: GPT-4o-mini analyzes error with context and generates:
   - Root cause explanation
   - Step-by-step reasoning
   - 2-3 ranked solutions with code examples
   - Confidence scores (0-1)
   - Source URLs from Stack Overflow
6. **Database Storage**: Error and analysis are stored in Supabase
7. **Response**: Frontend displays solutions with syntax-highlighted code

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

### Tables

**parsed_errors**
- Stores parsed error information
- Fields: id, raw_error_log, error_type, error_message, language, framework, file_name, line_number, function_name, stack_trace (JSONB), confidence_score, created_at

**analyses**
- Stores LLM-generated analysis results
- Fields: id, parsed_error_id (FK), root_cause, reasoning, solutions (JSONB), sources_used, created_at

**stackoverflow_posts**
- Stores scraped Stack Overflow posts
- Fields: id, question_id, title, question_body, answer_body, tags (array), votes, url, created_at, scraped_at

**embeddings** (Supabase pgvector)
- Stores vector embeddings for semantic search
- Fields: id, content, embedding (vector), metadata (JSONB), created_at

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
| Parse Error | 10-50ms | Regex-based, very fast |
| Vector Search | 50-200ms | Depends on collection size |
| DB Insert (Error) | 20-100ms | Async operation |
| LLM Analysis | 2-5 seconds | Main bottleneck |
| DB Insert (Analysis) | 20-100ms | Async operation |
| **Total** | **2.5-6 seconds** | End-to-end |

## Architecture Highlights

- **RAG (Retrieval-Augmented Generation)**: Combines semantic search with LLM generation for context-aware solutions
- **Vector Search**: Uses pgvector for fast semantic similarity search
- **Async Operations**: FastAPI async endpoints with SQLAlchemy async for better performance
- **Structured Output**: Uses OpenAI function calling for reliable JSON responses
- **Multi-stage Pipeline**: Parse → Search → Analyze → Store

## Technologies Used

- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **Next.js 14**: React framework with server-side rendering
- **SQLAlchemy**: Python ORM with async support
- **Supabase**: PostgreSQL with pgvector extension
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

**Last Updated**: 2026-01-16
**Version**: 1.0
