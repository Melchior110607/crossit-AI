Crossit AI
An experimental full-stack platform for managing and cross-listing e-commerce products across marketplaces.
Crossit AI was a personal software project I built before founding Revealy AI. I wanted to explore how a single application could manage product data, connect to different marketplaces, and automate repetitive listing workflows.
I used the project to learn how the pieces of a production-style web application fit together: frontend interfaces, backend APIs, relational data models, authentication, integrations, background jobs, and deployment. I developed it using AI-assisted coding while working through the architecture, integrations, and application logic.
Project status: Learning project / prototype. This repository is not a production-ready cross-listing service. Marketplace connector code and integration scaffolding do not imply that every marketplace has been authenticated, end-to-end tested, or approved for live publishing.
What I built
Product and listing management: Data models and API routes for products, listings, and marketplace connections.
Full-stack application structure: A Next.js/TypeScript frontend connected to a Python/FastAPI backend.
Marketplace integration framework: Connector modules designed to accommodate different marketplace APIs and authentication requirements.
Asynchronous processing: Redis and Celery components for background marketplace operations.
Development environment: Docker Compose setup for the application and supporting services.
Some features require external API credentials and additional marketplace-specific setup or testing. See the source code for the current implementation; do not assume all connectors operate end to end.
Tech stack
Layer
Technologies
Frontend
Next.js 14, React, TypeScript, Tailwind CSS, shadcn/ui
Backend
Python, FastAPI, SQLAlchemy, Pydantic, Alembic
Data
PostgreSQL, Redis
Background jobs
Celery
Infrastructure
Docker, Docker Compose, S3 integration code
Repository structure
backend/              FastAPI application, models, routes, services, connectors, tasks
frontend/             Next.js application and UI components
docker-compose.yml    Local multi-service development setup
supabase_schema.sql   Database schema reference
​
Running locally
Requirements: Docker and Docker Compose, plus the relevant environment configuration.
git clone <https://github.com/Melchior110607/crossit-AI.git>
cd crossit-AI
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# Add the required local configuration; never commit real credentials.
docker compose up --build
​
Depending on your configuration, the frontend runs at http://localhost:3000 and the backend API documentation at http://localhost:8000/docs. Database initialization, marketplace API credentials, and connector-specific setup may be required.
What I learned
Crossit helped me develop a practical understanding of how frontend, backend, databases, third-party APIs, and asynchronous workers interact. More importantly, it taught me how to break down a complex software product into components, evaluate AI-generated implementations, and iterate across the full stack. I subsequently applied those lessons when building Revealy AI.
Scope and limitations
This repository is a prototype and a record of my technical learning, not a claim of commercial traction. In particular, the presence of marketplace integrations in the codebase should not be interpreted as proof that all listed services are live or fully verified.
