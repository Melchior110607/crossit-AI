"""
OpenAI Service for product analysis and content generation
Uses GPT-4 Vision for image analysis and GPT-4 for content generation
"""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY environment variable not set. AI features will not work.")
            self.client = None
            self.vision_model = None
            self.text_model = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            self.vision_model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
            self.text_model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o")
    
    async def analyze_product_images(self, image_urls: List[str]) -> Dict[str, Any]:
        """
        Analyze product images using GPT-4 Vision with Chain of Thought
        
        Args:
            image_urls: List of image URLs to analyze
            
        Returns:
            {
                "product_name": str,
                "brand": str,
                "category": str,
                "condition": str,  # "new", "like_new", "good", "fair", "poor"
                "has_box": bool,
                "has_accessories": bool,
                "details": dict,  # Additional details like color, size, model, etc.
                "missing_info": List[str],  # List of missing information
                "confidence": float,  # 0.0 to 1.0
                "reasoning": str  # AI's reasoning process
            }
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
        
        try:
            # Prepare image content for Vision API
            image_content = [
                {
                    "type": "image_url",
                    "image_url": {"url": url, "detail": "high"}
                }
                for url in image_urls
            ]
            
            # Chain of Thought prompt
            system_prompt = """You are an expert product analyst. Analyze the provided images carefully and identify the product.

Use Chain of Thought reasoning:
1. First, identify what type of product this is
2. Look for brand names, logos, or identifying marks
3. Assess the condition based on visible wear, scratches, or damage
4. Check if original packaging/box is visible
5. Look for accessories or additional items
6. Note any missing information that would be helpful

Return your analysis as a JSON object with the following structure:
{
    "product_name": "Specific product name",
    "brand": "Brand name or 'Unknown'",
    "category": "Product category (electronics, clothing, shoes, accessories, collectibles, etc.)",
    "subcategory": "More specific category",
    "condition": "new|like_new|good|fair|poor",
    "has_box": true/false,
    "has_accessories": true/false,
    "details": {
        "color": "...",
        "size": "...",
        "model": "...",
        "year": "...",
        "material": "...",
        "other_details": "..."
    },
    "missing_info": ["list of information that cannot be determined from images"],
    "confidence": 0.0-1.0,
    "reasoning": "Your step-by-step reasoning process"
}

Be thorough and honest. If you're unsure about something, add it to missing_info and lower the confidence score."""

            user_prompt = f"""Analyze these {len(image_urls)} product image(s) and provide a detailed analysis.

IMPORTANT: 
- Look at ALL images carefully
- Note the condition accurately (visible wear, scratches, damage)
- Check for packaging, boxes, tags
- Identify all visible details (brand, model, color, size, etc.)
- If critical information is missing, list it in missing_info
- Provide your confidence score honestly

Please analyze now and return ONLY the JSON object, no additional text."""

            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            *image_content
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent analysis
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response (in case there's extra text)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            
            logger.info(f"Product analysis completed: {analysis.get('product_name')} (confidence: {analysis.get('confidence')})")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.error(f"Response content: {content}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Error analyzing product images: {str(e)}")
            raise
    
    async def search_product_online(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for product information online using GPT-4 with web browsing
        
        Args:
            product_info: Product information from image analysis
            
        Returns:
            {
                "found": bool,
                "product_details": dict,
                "market_info": {
                    "typical_price_range": {"min": float, "max": float},
                    "availability": str,
                    "popular_marketplaces": List[str]
                },
                "sources": List[str]  # URLs of sources
            }
        """
        try:
            product_name = product_info.get('product_name', 'Unknown')
            brand = product_info.get('brand', '')
            category = product_info.get('category', '')
            
            search_query = f"{brand} {product_name} {category}".strip()
            
            prompt = f"""Search online for information about this product:

Product: {product_name}
Brand: {brand}
Category: {category}
Condition: {product_info.get('condition', 'unknown')}

Find:
1. Exact product identification (model number, SKU if available)
2. Typical market prices (current retail and resale)
3. Where this product is commonly sold
4. Any relevant market information

Return as JSON:
{{
    "found": true/false,
    "product_details": {{
        "full_name": "...",
        "model_number": "...",
        "release_year": "...",
        "original_price": float,
        "other_info": "..."
    }},
    "market_info": {{
        "typical_price_range": {{"min": float, "max": float}},
        "availability": "widely available|limited|rare|discontinued",
        "popular_marketplaces": ["ebay", "amazon", "stockx", etc.]
    }},
    "sources": ["url1", "url2"]
}}"""
           
            # Use responses.create with web_search tool (OpenAI Responses API)
            response = await self.client.responses.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product research assistant. Search the web for accurate product information and market data. Return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3,
                tools=[{"type": "web_search"}]
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            logger.info(f"Online search completed for: {search_query} (found: {result.get('found')})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching product online: {str(e)}")
            # Return empty result on error
            return {
                "found": False,
                "product_details": {},
                "market_info": {
                    "typical_price_range": {"min": 0, "max": 0},
                    "availability": "unknown",
                    "popular_marketplaces": []
                },
                "sources": []
            }
    
    async def generate_product_content(
        self,
        product_info: Dict[str, Any],
        marketplace: str,
        price_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate optimized product listing content for specific marketplace
        
        Args:
            product_info: Product information from analysis
            marketplace: Target marketplace (ebay, shopify, stockx, etc.)
            price_data: Optional pricing data
            
        Returns:
            {
                "title": str,  # Optimized for marketplace
                "description": str,  # Rich HTML description
                "short_description": str,  # Plain text summary
                "tags": List[str],
                "specifications": dict,
                "seo_keywords": List[str]
            }
        """
        try:
            # Marketplace-specific guidelines
            marketplace_guidelines = {
                "ebay": {
                    "title_max": 80,
                    "style": "keyword-rich, searchable",
                    "focus": "condition, brand, model, key features"
                },
                "shopify": {
                    "title_max": 255,
                    "style": "clean, brand-focused",
                    "focus": "benefits, lifestyle, quality"
                },
                "stockx": {
                    "title_max": 100,
                    "style": "exact model name and colorway",
                    "focus": "authenticity, condition, original packaging"
                },
                "etsy": {
                    "title_max": 140,
                    "style": "descriptive, handmade-friendly",
                    "focus": "uniqueness, craftsmanship, story"
                }
            }
            
            guidelines = marketplace_guidelines.get(marketplace, marketplace_guidelines["ebay"])
            
            product_name = product_info.get('product_name', 'Product')
            brand = product_info.get('brand', '')
            condition = product_info.get('condition', 'used')
            details = product_info.get('details', {})
            
            price_context = ""
            if price_data:
                avg_price = price_data.get('marketplace_prices', {}).get(marketplace, {}).get('avg')
                if avg_price:
                    price_context = f"\nSuggested price based on market: ${avg_price:.2f}"
            
            prompt = f"""Create an optimized product listing for {marketplace.upper()}.

PRODUCT INFORMATION:
- Name: {product_name}
- Brand: {brand}
- Category: {product_info.get('category', 'General')}
- Condition: {condition}
- Has Box: {product_info.get('has_box', False)}
- Has Accessories: {product_info.get('has_accessories', False)}
- Details: {json.dumps(details, indent=2)}
{price_context}

MARKETPLACE GUIDELINES for {marketplace}:
- Title max length: {guidelines['title_max']} characters
- Style: {guidelines['style']}
- Focus on: {guidelines['focus']}

Create:
1. A compelling, SEO-optimized title (under {guidelines['title_max']} chars)
2. A detailed HTML description highlighting key features, condition, and value
3. A short plain-text summary (2-3 sentences)
4. Relevant tags/keywords for search
5. Structured specifications
6. SEO keywords

Return as JSON:
{{
    "title": "Optimized title here",
    "description": "<p>HTML formatted description...</p>",
    "short_description": "Plain text summary",
    "tags": ["tag1", "tag2", ...],
    "specifications": {{
        "Brand": "...",
        "Condition": "...",
        "Color": "...",
        ...
    }},
    "seo_keywords": ["keyword1", "keyword2", ...]
}}

Make it compelling and honest. Highlight the condition accurately."""

            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {marketplace} seller. Create compelling, honest product listings that convert. Return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7  # Slightly higher for creative content
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            listing_content = json.loads(content)
            
            # Validate title length
            if len(listing_content.get('title', '')) > guidelines['title_max']:
                listing_content['title'] = listing_content['title'][:guidelines['title_max']-3] + '...'
            
            logger.info(f"Content generated for {marketplace}: {listing_content.get('title')}")
            
            return listing_content
            
        except Exception as e:
            logger.error(f"Error generating product content: {str(e)}")
            # Return minimal content on error
            return {
                "title": f"{product_info.get('brand', '')} {product_info.get('product_name', 'Product')}".strip(),
                "description": "<p>Product for sale. Contact for details.</p>",
                "short_description": "Product for sale",
                "tags": [product_info.get('category', 'general')],
                "specifications": {},
                "seo_keywords": []
            }
    
    async def estimate_price_with_ai(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate product price using AI when no market data is available
        
        Args:
            product_info: Product information
            
        Returns:
            {
                "estimated_price": float,
                "price_range": {"min": float, "max": float},
                "confidence": str,  # "low", "medium", "high"
                "reasoning": str
            }
        """
        try:
            prompt = f"""Estimate the market value of this product:

Product: {product_info.get('product_name')}
Brand: {product_info.get('brand')}
Category: {product_info.get('category')}
Condition: {product_info.get('condition')}
Has Box: {product_info.get('has_box', False)}
Has Accessories: {product_info.get('has_accessories', False)}
Details: {json.dumps(product_info.get('details', {}), indent=2)}

Provide a realistic price estimate based on:
1. Similar products in the market
2. Brand value
3. Condition
4. Completeness (box, accessories)
5. Current market trends

Return as JSON:
{{
    "estimated_price": float,
    "price_range": {{"min": float, "max": float}},
    "confidence": "low|medium|high",
    "reasoning": "Detailed explanation of price estimate"
}}"""

            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a pricing expert. Provide realistic, conservative price estimates. Return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            estimate = json.loads(content)
            
            logger.info(f"Price estimated: ${estimate.get('estimated_price'):.2f} (confidence: {estimate.get('confidence')})")
            
            return estimate
            
        except Exception as e:
            logger.error(f"Error estimating price: {str(e)}")
            # Return conservative estimate on error
            return {
                "estimated_price": 50.0,
                "price_range": {"min": 25.0, "max": 100.0},
                "confidence": "low",
                "reasoning": "Unable to estimate accurately. Manual pricing recommended."
            }

