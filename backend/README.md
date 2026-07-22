# CodeGraph Backend

Backend API for CodeGraph - The AI Software Architect for Every Codebase.

## Tech Stack

- **Python**: 3.12+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic v2
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Environment**: python-dotenv
- **Testing**: pytest

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Run the server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core configuration and settings
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic services
│   ├── utils/         # Utility functions
│   ├── dependencies/  # FastAPI dependencies
│   ├── middleware/    # Custom middleware
│   └── main.py        # Application entry point
├── tests/             # Test files
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## API Endpoints

### GET /
Returns application status:
```json
{
  "name": "CodeGraph",
  "status": "running"
}
```

### GET /health
Health check endpoint:
```json
{
  "status": "healthy"
}
```

## Development

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```
