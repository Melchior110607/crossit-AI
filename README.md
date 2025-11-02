# CrossIt - E-commerce Cross-Listing Platform

A powerful multi-tenant platform for cross-listing products across 20+ e-commerce marketplaces.

## 🚀 Features

- **Multi-Marketplace Support**: Connect to 20 major marketplaces (Amazon, eBay, Etsy, and more)
- **Automated Cross-Listing**: Publish products to multiple marketplaces simultaneously
- **Unified Dashboard**: Manage all your listings from one central location
- **OAuth Integration**: Secure authentication with each marketplace
- **Webhook Support**: Real-time notifications for sales and updates
- **Image Management**: S3-based storage for product images
- **Async Task Processing**: Celery-based background jobs for marketplace operations

## 📋 Tech Stack

### Backend
- **FastAPI** (Python 3.11+) - Modern, fast web framework
- **PostgreSQL** - Relational database
- **Redis** - Cache and message broker
- **Celery** - Async task queue
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Boto3** - AWS S3 integration

### Frontend
- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components
- **Axios** - HTTP client

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **AWS S3** - Image storage

## 🏁 Getting Started

### Prerequisites

- Docker & Docker Compose installed
- (Optional) Node.js 20+ for local frontend development
- (Optional) Python 3.11+ for local backend development

### Quick Start with Docker

1. **Clone the repository**:
```bash
git clone <repo-url>
cd "crossit AI"
```

2. **Copy environment files**:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

3. **Update configuration**:
Edit `backend/.env` and add your credentials:
- Database credentials (default works for Docker)
- Secret key for JWT
- AWS S3 credentials
- Marketplace API credentials (as you obtain them)

4. **Start all services**:
```bash
docker-compose up -d
```

This will start:
- Frontend on http://localhost:3000
- Backend API on http://localhost:8000
- PostgreSQL database
- Redis
- Celery worker
- Celery beat (scheduler)

5. **Initialize database**:
```bash
docker-compose exec backend alembic upgrade head
```

6. **Access the application**:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Alternative: Local Development Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL and Redis separately or use Docker:
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📦 Supported Marketplaces

| # | Marketplace | Status | API Documentation |
|---|-------------|--------|-------------------|
| 1 | Amazon (SP-API) | ✅ Implemented | [Link](https://developer-docs.amazon.com) |
| 2 | eBay | ✅ Implemented | [Link](https://developer.ebay.com) |
| 3 | Etsy | ✅ Implemented | [Link](https://developer.etsy.com) |
| 4 | bol.com | ✅ Implemented | [Link](https://api.bol.com) |
| 5 | Allegro | ✅ Implemented | [Link](https://developer.allegro.pl) |
| 6 | Kaufland | ✅ Implemented | [Link](https://sellerapi.kaufland.com) |
| 7 | OnBuy | ✅ Implemented | [Link](https://onbuy.github.io) |
| 8 | Wish | ✅ Implemented | [Link](https://merchant.wish.com) |
| 9 | Joom | ✅ Implemented | [Link](https://merchant.joom.com) |
| 10 | Zalando | ✅ Implemented | [Link](https://helpcenter.channable.com) |
| 11 | ABOUT YOU | ✅ Implemented | [Link](https://aboutyou.de) |
| 12 | OTTO Market | ✅ Implemented | [Link](https://api.otto.market) |
| 13 | Cdiscount | ✅ Implemented | [Link](https://marketplace.cdiscount.com) |
| 14 | Fnac Darty | ✅ Implemented | [Link](https://fnacdartymarketplace.com) |
| 15 | Vinted Pro | ✅ Implemented | [Link](https://pro-docs.svc.vinted.com) |
| 16 | StockX | ✅ Implemented | [Link](https://stockx.com/developer) |
| 17 | Shopify | ✅ Implemented | [Link](https://shopify.dev) |
| 18 | La Redoute | ✅ Implemented | Mirakl-based |
| 19 | Galeries Lafayette | ✅ Implemented | Mirakl-based |
| 20 | ASOS | ✅ Implemented | Mirakl-based |

## 🔑 Obtaining API Credentials

Each marketplace requires you to register as a developer and obtain API credentials:

### Priority Marketplaces

**Amazon SP-API**:
1. Visit [Amazon Seller Central](https://developer-docs.amazon.com)
2. Register as a developer
3. Create a new app and obtain:
   - Client ID
   - Client Secret
   - Refresh Token (after OAuth flow)

**eBay**:
1. Visit [eBay Developers Program](https://developer.ebay.com)
2. Create an application
3. Obtain:
   - Client ID (App ID)
   - Client Secret (Cert ID)
   - Configure OAuth redirect URI

**Etsy**:
1. Visit [Etsy Developers](https://developer.etsy.com)
2. Register your app
3. Obtain:
   - API Key (Keystring)
   - Shared Secret

### Other Marketplaces

Follow similar registration processes for other marketplaces. Each requires:
- Developer account registration
- Application creation
- OAuth credentials (Client ID & Secret)
- API key configuration

Add all credentials to `backend/.env`:

```env
# Amazon
AMAZON_CLIENT_ID=your_client_id
AMAZON_CLIENT_SECRET=your_client_secret
AMAZON_REFRESH_TOKEN=your_refresh_token

# eBay
EBAY_CLIENT_ID=your_client_id
EBAY_CLIENT_SECRET=your_client_secret

# ... and so on for each marketplace
```

## 📖 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication**:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/users/me` - Get current user

**Products**:
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get product details
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

**Listings**:
- `GET /api/listings` - List all listings
- `POST /api/listings` - Create listing
- `DELETE /api/listings/{id}` - Delete listing

**Marketplaces**:
- `GET /api/marketplaces` - List available marketplaces
- `GET /api/marketplaces/connected` - Get connected marketplaces
- `POST /api/marketplaces/{name}/connect` - Initiate OAuth connection
- `DELETE /api/marketplaces/{name}/disconnect` - Disconnect marketplace

**Upload**:
- `POST /api/upload/images` - Upload product images

## 🏗️ Project Structure

```
crossit-ai/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   ├── listings.py
│   │   │   ├── marketplaces.py
│   │   │   ├── webhooks.py
│   │   │   └── upload.py
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── listing.py
│   │   │   ├── marketplace_connection.py
│   │   │   └── webhook_event.py
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── integrations/     # Marketplace connectors
│   │   │   ├── base_connector.py
│   │   │   ├── amazon_connector.py
│   │   │   ├── ebay_connector.py
│   │   │   ├── etsy_connector.py
│   │   │   ├── shopify_connector.py
│   │   │   ├── ... (17 more)
│   │   │   └── connector_factory.py
│   │   └── tasks/            # Celery tasks
│   │       ├── celery_app.py
│   │       └── marketplace_tasks.py
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── products/
│   │   │   │   └── marketplaces/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/       # Reusable components
│   │   ├── contexts/         # React contexts
│   │   │   └── AuthContext.tsx
│   │   └── lib/              # Utilities
│   │       ├── api-client.ts
│   │       └── utils.ts
│   ├── package.json
│   ├── Dockerfile
│   └── .env.local.example
├── docker-compose.yml
├── Makefile
└── README.md
```

## 🔧 Makefile Commands

Convenient commands for development:

```bash
make build       # Build all containers
make up          # Start all services
make down        # Stop all services
make logs        # View logs
make restart     # Restart services
make clean       # Remove containers and volumes
make migrate     # Run database migrations
make shell       # Open backend shell
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🚀 Deployment

The platform is designed to run in Docker containers and can be deployed to:
- AWS (ECS, EKS)
- Google Cloud (GKE)
- Azure (AKS)
- Any Kubernetes cluster

Production considerations:
- Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- Use managed Redis (ElastiCache, etc.)
- Configure proper secrets management
- Set up SSL/TLS certificates
- Configure CDN for frontend
- Set up monitoring and logging

## 🤝 Contributing

This is a proprietary project. For contribution guidelines, contact the maintainer.

## 📝 License

Proprietary - All rights reserved

## 💬 Support

For support and questions, contact the development team.

---

**Note**: This platform is in active development. Marketplace integrations require actual API credentials to function. Some marketplace connectors may need additional configuration based on their specific requirements.

