"""
Product Automation API
AI-powered product analysis, price research, and listing generation
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import uuid

from app.services.openai_service import OpenAIService
from app.services.price_research_service import PriceResearchService
from app.services.marketplace_recommender import MarketplaceRecommender
from app.core.supabase import supabase_admin

logger = logging.getLogger(__name__)

router = APIRouter()

# Mock user ID for development
MOCK_USER_ID = "dev_user_123"


# Request/Response Models
class AnalyzeRequest(BaseModel):
    images: List[str]  # List of image URLs
    user_id: Optional[str] = MOCK_USER_ID


class AnalyzeResponse(BaseModel):
    analysis_id: str
    product_info: Dict[str, Any]
    missing_info: List[str]
    confidence: float


class ResearchPricesRequest(BaseModel):
    analysis_id: str
    product_info: Dict[str, Any]
    user_id: Optional[str] = MOCK_USER_ID


class ResearchPricesResponse(BaseModel):
    research_id: str
    marketplace_prices: Dict[str, Any]
    recommended_price: float
    confidence: str
    marketplace_recommendations: Dict[str, Any]


class GenerateListingsRequest(BaseModel):
    analysis_id: str
    product_info: Dict[str, Any]
    price_data: Dict[str, Any]
    selected_marketplaces: List[str]
    user_id: Optional[str] = MOCK_USER_ID


class GenerateListingsResponse(BaseModel):
    listings: Dict[str, Any]  # marketplace_id -> listing_data


class PublishListingsRequest(BaseModel):
    analysis_id: str
    listings: Dict[str, Any]  # marketplace_id -> listing_data
    user_id: Optional[str] = MOCK_USER_ID


class PublishListingsResponse(BaseModel):
    published: List[str]  # marketplace_ids
    failed: List[Dict[str, str]]  # {marketplace_id, error}
    product_id: Optional[str]


# Initialize services
openai_service = OpenAIService()
price_research_service = PriceResearchService()
marketplace_recommender = MarketplaceRecommender()


@router.post("/products/analyze", response_model=AnalyzeResponse)
async def analyze_product(request: AnalyzeRequest):
    """
    Step 1: Analyze product images with GPT-4 Vision
    
    Analyzes uploaded images to identify:
    - Product name and brand
    - Category and condition
    - Details (color, size, model, etc.)
    - Missing information
    
    Returns analysis with confidence score.
    """
    try:
        logger.info(f"Starting product analysis for user {request.user_id}")
        
        if not request.images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one image is required"
            )
        
        # Analyze images with GPT-4 Vision
        product_info = await openai_service.analyze_product_images(request.images)
        
        # Create analysis record in Supabase
        analysis_id = str(uuid.uuid4())
        analysis_record = {
            "id": analysis_id,
            "user_id": request.user_id,
            "images": request.images,
            "analysis_result": product_info,
            "status": "completed",
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp())
        }
        
        result = supabase_admin.table("product_analyses").insert(analysis_record).execute()
        
        if not result.data:
            logger.error("Failed to store analysis in database")
        
        return AnalyzeResponse(
            analysis_id=analysis_id,
            product_info=product_info,
            missing_info=product_info.get("missing_info", []),
            confidence=product_info.get("confidence", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/products/research-prices", response_model=ResearchPricesResponse)
async def research_prices(request: ResearchPricesRequest):
    """
    Step 2: Research product prices across all marketplaces
    
    Searches for product prices using:
    1. Marketplace APIs (user's connected + all others)
    2. Web search via GPT
    3. AI estimation if no results
    
    Also provides marketplace recommendations.
    """
    try:
        logger.info(f"Starting price research for analysis {request.analysis_id}")
        
        # Get user's connected marketplaces
        connections = supabase_admin.table("marketplace_connections").select(
            "marketplace_id"
        ).eq("user_id", request.user_id).eq("status", "active").execute()
        
        user_marketplaces = [c["marketplace_id"] for c in connections.data] if connections.data else []
        
        # Research prices across all marketplaces
        price_data = await price_research_service.search_all_marketplaces(
            request.product_info,
            user_marketplaces
        )
        
        # Get marketplace recommendations
        recommendations = await marketplace_recommender.recommend_marketplaces(
            request.product_info,
            user_marketplaces
        )
        
        # Store price research in Supabase
        research_id = str(uuid.uuid4())
        research_record = {
            "id": research_id,
            "product_analysis_id": request.analysis_id,
            "marketplace_prices": price_data.get("marketplace_prices", {}),
            "recommended_price": price_data.get("recommended_price", 0.0),
            "confidence": price_data.get("confidence", "unknown"),
            "created_at": int(datetime.now().timestamp())
        }
        
        result = supabase_admin.table("price_researches").insert(research_record).execute()
        
        if not result.data:
            logger.error("Failed to store price research in database")
        
        return ResearchPricesResponse(
            research_id=research_id,
            marketplace_prices=price_data.get("marketplace_prices", {}),
            recommended_price=price_data.get("recommended_price", 0.0),
            confidence=price_data.get("confidence", "unknown"),
            marketplace_recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error researching prices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Price research failed: {str(e)}"
        )


@router.post("/products/generate-listings", response_model=GenerateListingsResponse)
async def generate_listings(request: GenerateListingsRequest):
    """
    Step 3: Generate optimized listings for selected marketplaces
    
    Creates marketplace-specific content:
    - SEO-optimized titles
    - Compelling descriptions
    - Relevant tags and keywords
    - Structured specifications
    
    All customized for each marketplace's format and audience.
    """
    try:
        logger.info(f"Generating listings for {len(request.selected_marketplaces)} marketplaces")
        
        if not request.selected_marketplaces:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one marketplace must be selected"
            )
        
        listings = {}
        
        # Generate content for each selected marketplace
        for marketplace in request.selected_marketplaces:
            try:
                # Get marketplace-specific price if available
                marketplace_price = request.price_data.get("marketplace_prices", {}).get(marketplace, {})
                
                # Generate content
                content = await openai_service.generate_product_content(
                    request.product_info,
                    marketplace,
                    request.price_data
                )
                
                # Add price to listing
                price = marketplace_price.get("avg", request.price_data.get("recommended_price", 0.0))
                
                listing_data = {
                    **content,
                    "marketplace": marketplace,
                    "price": price,
                    "currency": "USD",
                    "quantity": 1,
                    "condition": request.product_info.get("condition", "used"),
                    "brand": request.product_info.get("brand", ""),
                    "category": request.product_info.get("category", ""),
                }
                
                listings[marketplace] = listing_data
                
                # Store in database
                listing_record = {
                    "id": str(uuid.uuid4()),
                    "product_analysis_id": request.analysis_id,
                    "marketplace_id": marketplace,
                    "listing_data": listing_data,
                    "status": "draft",
                    "created_at": int(datetime.now().timestamp()),
                    "updated_at": int(datetime.now().timestamp())
                }
                
                supabase_admin.table("generated_listings").insert(listing_record).execute()
                
            except Exception as e:
                logger.error(f"Error generating listing for {marketplace}: {str(e)}")
                listings[marketplace] = {
                    "error": str(e),
                    "marketplace": marketplace
                }
        
        return GenerateListingsResponse(listings=listings)
        
    except Exception as e:
        logger.error(f"Error generating listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Listing generation failed: {str(e)}"
        )


@router.post("/products/publish-listings", response_model=PublishListingsResponse)
async def publish_listings(request: PublishListingsRequest):
    """
    Step 4: Publish approved listings to marketplaces
    
    Creates actual product listings on selected marketplaces
    and stores product information in database.
    """
    try:
        logger.info(f"Publishing listings for user {request.user_id}")
        
        if not request.listings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No listings provided"
            )
        
        published = []
        failed = []
        
        # Get analysis data to retrieve images
        analysis = supabase_admin.table("product_analyses").select(
            "*"
        ).eq("id", request.analysis_id).execute()
        
        if not analysis.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        analysis_data = analysis.data[0]
        images = analysis_data.get("images", [])
        product_info = analysis_data.get("analysis_result", {})
        
        # Create main product record first
        first_listing = list(request.listings.values())[0]
        
        product_id = str(uuid.uuid4())
        product_record = {
            "id": product_id,
            "user_id": request.user_id,
            "title": first_listing.get("title", product_info.get("product_name", "Untitled")),
            "description": first_listing.get("short_description", ""),
            "price": first_listing.get("price", 0.0),
            "currency": "USD",
            "category": first_listing.get("category", ""),
            "brand": first_listing.get("brand", ""),
            "condition": first_listing.get("condition", "used"),
            "quantity": 1,
            "images": images,
            "status": "active",
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp())
        }
        
        product_result = supabase_admin.table("products").insert(product_record).execute()
        
        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create product"
            )
        
        # TODO: Actually publish to marketplace APIs
        # For now, we'll create listing records and mark them as published
        
        for marketplace_id, listing_data in request.listings.items():
            try:
                # Create listing record
                listing_record = {
                    "id": str(uuid.uuid4()),
                    "product_id": product_id,
                    "marketplace_id": marketplace_id,
                    "user_id": request.user_id,
                    "external_listing_id": None,  # Would be set after API call
                    "title": listing_data.get("title", ""),
                    "price": listing_data.get("price", 0.0),
                    "currency": "USD",
                    "quantity": 1,
                    "status": "draft",  # Would be 'active' after successful API call
                    "created_at": int(datetime.now().timestamp()),
                    "updated_at": int(datetime.now().timestamp())
                }
                
                listing_result = supabase_admin.table("listings").insert(listing_record).execute()
                
                if listing_result.data:
                    published.append(marketplace_id)
                    logger.info(f"Created listing for {marketplace_id}")
                else:
                    failed.append({
                        "marketplace_id": marketplace_id,
                        "error": "Failed to create listing record"
                    })
                    
            except Exception as e:
                logger.error(f"Error publishing to {marketplace_id}: {str(e)}")
                failed.append({
                    "marketplace_id": marketplace_id,
                    "error": str(e)
                })
        
        # Update generated_listings status
        for marketplace_id in published:
            supabase_admin.table("generated_listings").update({
                "status": "published",
                "updated_at": int(datetime.now().timestamp())
            }).eq("product_analysis_id", request.analysis_id).eq(
                "marketplace_id", marketplace_id
            ).execute()
        
        return PublishListingsResponse(
            published=published,
            failed=failed,
            product_id=product_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Publishing failed: {str(e)}"
        )


@router.get("/products/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get product analysis by ID"""
    try:
        result = supabase_admin.table("product_analyses").select("*").eq("id", analysis_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/products/analysis/{analysis_id}/listings")
async def get_generated_listings(analysis_id: str):
    """Get generated listings for an analysis"""
    try:
        result = supabase_admin.table("generated_listings").select(
            "*"
        ).eq("product_analysis_id", analysis_id).execute()
        
        return {"listings": result.data or []}
        
    except Exception as e:
        logger.error(f"Error fetching generated listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

