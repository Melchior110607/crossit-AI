from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, users, products, listings, marketplaces, webhooks, upload

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="E-commerce Cross-Listing Platform API"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(marketplaces.router, prefix="/api/marketplaces", tags=["marketplaces"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

@app.get("/")
def root():
    return {"message": "Cross-Listing Platform API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

