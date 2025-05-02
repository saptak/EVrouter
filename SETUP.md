# EVrouter Local Development Setup

This guide provides step-by-step instructions for setting up the EVrouter application locally for development and testing.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (v14 or higher)
- [Python](https://www.python.org/downloads/) (v3.8 or higher)
- [Git](https://git-scm.com/downloads)

## Setup Steps

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/EVrouter.git
cd EVrouter
```

### 2. Run with Docker Compose (Recommended)

The easiest way to run the full application stack is using Docker Compose:

```bash
# Start all services
docker-compose up -d

# Initialize the database with sample data
docker-compose exec backend python initialize.py
```

This will start:
- Neo4j database on port 7474 (browser UI) and 7687 (Bolt protocol)
- Backend API on port 8000
- Frontend app on port 3000

You can access:
- Frontend application: http://localhost:3000
- API documentation: http://localhost:8000/docs
- Neo4j browser: http://localhost:7474 (credentials: neo4j/evrouter)

### 3. Manual Setup (Alternative)

If you prefer to run components individually:

#### Backend Setup

```bash
# Create and activate a virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend (ensure Neo4j is running)
uvicorn main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

#### Neo4j Setup

If you want to run Neo4j separately:

```bash
docker run \
    --name evrouter-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/evrouter \
    -e NEO4J_dbms_memory_heap_max__size=2G \
    -v neo4j_data:/data \
    neo4j:4.4
```

## Development Workflow

### Backend Development

The backend uses FastAPI with auto-reload enabled, so your changes will be reflected immediately. Key files:

- `backend/main.py`: Application entry point
- `backend/app/api/`: API endpoints
- `backend/app/services/`: Business logic
- `backend/app/models/`: Data models
- `backend/app/db/`: Database interactions

### Frontend Development

The React frontend also has hot-reloading enabled. Key files:

- `frontend/src/App.tsx`: Main component
- `frontend/src/components/`: React components
- `frontend/src/services/`: API services
- `frontend/src/contexts/`: React contexts
- `frontend/src/hooks/`: Custom React hooks

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Troubleshooting

### Database Connection Issues

If the backend cannot connect to Neo4j:

1. Check Neo4j is running: `docker ps | grep neo4j`
2. Verify credentials in `.env` file
3. Try accessing Neo4j browser directly: http://localhost:7474

### API Connection Issues

If the frontend cannot connect to the backend:

1. Check backend is running: `curl http://localhost:8000/docs`
2. Verify API URL in `frontend/.env` file
3. Check for CORS issues in browser console

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Neo4j Documentation](https://neo4j.com/docs/)
