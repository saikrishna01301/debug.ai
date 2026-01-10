# DebugAI - Docker Setup

A full-stack application with FastAPI backend, Next.js frontend, and PostgreSQL database, all containerized with Docker.

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js (TypeScript)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Project Structure

```
debugAi/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── app/
│       ├── page.tsx
│       └── layout.tsx
├── docker-compose.yml
└── .env.example
```

## Quick Start

### Prerequisites
- Docker installed on your machine
- Docker Compose installed

### Setup Steps

1. **Clone and navigate to the project**
   ```bash
   cd "/Users/saikrishna/Desktop/skool/ai engineer/GenAI/debugAi"
   ```

2. **Create environment files** (optional - defaults work for development)
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port `5432`
   - FastAPI backend on port `8000`
   - Next.js frontend on port `3000`

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

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

## Database Management

### Connect to Database
```bash
docker exec -it debugai-db psql -U debugai -d debugai_db
```

### Database Credentials (default)
- Host: `localhost` (or `db` from within containers)
- Port: `5432`
- Database: `debugai_db`
- Username: `debugai`
- Password: `debugai_password`

## Troubleshooting

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
Make sure `NEXT_PUBLIC_API_URL` in frontend environment points to `http://localhost:8000`

## Production Deployment

For production, update:
1. Change database credentials in environment variables
2. Set `ENVIRONMENT=production` in backend
3. Use build optimizations for frontend:
   ```bash
   docker-compose -f docker-compose.prod.yml up
   ```

## Next Steps

- Add database models using SQLAlchemy in the backend
- Create API endpoints in `backend/main.py`
- Build your frontend components in `frontend/app/`
- Set up database migrations with Alembic
- Add authentication and authorization
- Configure CORS properly for your domain
