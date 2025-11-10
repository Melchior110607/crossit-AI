"""
Price Research Service
Searches for product prices across multiple marketplaces using their APIs
"""
import os
import logging
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from datetime import datetime

from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class PriceResearchService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.ebay_app_id = os.getenv("EBAY_APP_ID")
        self.ebay_finding_app_id = os.getenv("EBAY_FINDING_APP_ID") or self.ebay_app_id
    
    async def search_all_marketplaces(
        self,
        product_info: Dict[str, Any],
        user_marketplaces: List[str]
    ) -> Dict[str, Any]:
        """
        Cascade search for product prices:
        1. User's connected marketplaces (APIs)
        2. All other marketplaces (APIs)
        3. Web search via OpenAI
        4. AI estimation if nothing found
        
        Args:
            product_info: Product information from analysis
            user_marketplaces: List of marketplace IDs user is connected to
            
        Returns:
            {
                "marketplace_prices": {
                    "ebay": {"min": 50, "max": 100, "avg": 75, "found": True, "count": 10},
                    "shopify": {"estimated": True, "price": 80},
                    ...
                },
                "recommended_price": float,
                "confidence": str,  # "high", "medium", "low", "estimated"
                "search_summary": {
                    "total_results": int,
                    "marketplaces_searched": List[str],
                    "marketplaces_with_results": List[str]
                }
            }
        """
        logger.info(f"Starting price research for: {product_info.get('product_name')}")
        
        marketplace_prices = {}
        search_summary = {
            "total_results": 0,
            "marketplaces_searched": [],
            "marketplaces_with_results": []
        }
        
        # All available marketplaces
        all_marketplaces = ["ebay", "shopify", "stockx", "etsy", "amazon"]
        
        # 1. Search user's connected marketplaces first (higher priority)
        user_search_tasks = []
        for marketplace in user_marketplaces:
            if marketplace in all_marketplaces:
                user_search_tasks.append(self._search_marketplace(marketplace, product_info))
                search_summary["marketplaces_searched"].append(marketplace)
        
        if user_search_tasks:
            user_results = await asyncio.gather(*user_search_tasks, return_exceptions=True)
            for marketplace, result in zip(user_marketplaces, user_results):
                if not isinstance(result, Exception) and result:
                    marketplace_prices[marketplace] = result
                    if result.get("found"):
                        search_summary["marketplaces_with_results"].append(marketplace)
                        search_summary["total_results"] += result.get("count", 0)
        
        # 2. Search other marketplaces
        other_marketplaces = [m for m in all_marketplaces if m not in user_marketplaces]
        other_search_tasks = []
        for marketplace in other_marketplaces:
            other_search_tasks.append(self._search_marketplace(marketplace, product_info))
            search_summary["marketplaces_searched"].append(marketplace)
        
        if other_search_tasks:
            other_results = await asyncio.gather(*other_search_tasks, return_exceptions=True)
            for marketplace, result in zip(other_marketplaces, other_results):
                if not isinstance(result, Exception) and result:
                    marketplace_prices[marketplace] = result
                    if result.get("found"):
                        search_summary["marketplaces_with_results"].append(marketplace)
                        search_summary["total_results"] += result.get("count", 0)
        
        # 3. Web search via OpenAI if limited results
        if search_summary["total_results"] < 3:
            logger.info("Limited results, performing web search...")
            try:
                web_search_result = await self.openai_service.search_product_online(product_info)
                if web_search_result.get("found"):
                    market_info = web_search_result.get("market_info", {})
                    price_range = market_info.get("typical_price_range", {})
                    
                    # Add as general market data
                    marketplace_prices["web_search"] = {
                        "found": True,
                        "min": price_range.get("min", 0),
                        "max": price_range.get("max", 0),
                        "avg": (price_range.get("min", 0) + price_range.get("max", 0)) / 2 if price_range else 0,
                        "source": "web_search",
                        "estimated": True
                    }
            except Exception as e:
                logger.error(f"Web search failed: {str(e)}")
        
        # 4. AI estimation if still no results
        if search_summary["total_results"] == 0:
            logger.info("No results found, using AI estimation...")
            try:
                ai_estimate = await self.openai_service.estimate_price_with_ai(product_info)
                marketplace_prices["ai_estimate"] = {
                    "found": False,
                    "estimated": True,
                    "price": ai_estimate.get("estimated_price", 0),
                    "min": ai_estimate.get("price_range", {}).get("min", 0),
                    "max": ai_estimate.get("price_range", {}).get("max", 0),
                    "avg": ai_estimate.get("estimated_price", 0),
                    "confidence": ai_estimate.get("confidence", "low"),
                    "reasoning": ai_estimate.get("reasoning", "")
                }
            except Exception as e:
                logger.error(f"AI estimation failed: {str(e)}")
        
        # Calculate recommended price and overall confidence
        recommended_price, confidence = self._calculate_recommended_price(marketplace_prices, search_summary)
        
        result = {
            "marketplace_prices": marketplace_prices,
            "recommended_price": recommended_price,
            "confidence": confidence,
            "search_summary": search_summary
        }
        
        logger.info(f"Price research completed: ${recommended_price:.2f} (confidence: {confidence})")
        
        return result
    
    async def _search_marketplace(self, marketplace: str, product_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route to appropriate marketplace search method"""
        search_methods = {
            "ebay": self.search_ebay_api,
            "shopify": self.search_shopify_api,
            "stockx": self.search_stockx_api,
            "etsy": self.search_etsy_api,
            "amazon": self.search_amazon_api
        }
        
        method = search_methods.get(marketplace)
        if method:
            try:
                return await method(product_info)
            except Exception as e:
                logger.error(f"Error searching {marketplace}: {str(e)}")
                return None
        return None
    
    async def search_ebay_api(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search eBay using Finding API
        Documentation: https://developer.ebay.com/devzone/finding/Concepts/FindingAPIGuide.html
        """
        if not self.ebay_finding_app_id:
            logger.warning("eBay Finding API App ID not configured")
            return {"found": False, "estimated": False}
        
        try:
            product_name = product_info.get('product_name', '')
            brand = product_info.get('brand', '')
            category = product_info.get('category', '')
            
            # Build search query
            keywords = f"{brand} {product_name}".strip()
            if not keywords:
                keywords = category
            
            # eBay Finding API endpoint
            url = "https://svcs.ebay.com/services/search/FindingService/v1"
            
            params = {
                "OPERATION-NAME": "findCompletedItems",
                "SERVICE-VERSION": "1.13.0",
                "SECURITY-APPNAME": self.ebay_finding_app_id,
                "RESPONSE-DATA-FORMAT": "JSON",
                "REST-PAYLOAD": "",
                "keywords": keywords,
                "paginationInput.entriesPerPage": "100",
                "sortOrder": "EndTimeSoonest",
                # Filter for sold items only
                "itemFilter(0).name": "SoldItemsOnly",
                "itemFilter(0).value": "true",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse results
                        search_result = data.get("findCompletedItemsResponse", [{}])[0]
                        ack = search_result.get("ack", [""])[0]
                        
                        if ack == "Success":
                            items = search_result.get("searchResult", [{}])[0].get("item", [])
                            
                            if items:
                                prices = []
                                for item in items:
                                    selling_status = item.get("sellingStatus", [{}])[0]
                                    price = selling_status.get("currentPrice", [{}])[0].get("__value__")
                                    if price:
                                        try:
                                            prices.append(float(price))
                                        except ValueError:
                                            continue
                                
                                if prices:
                                    return {
                                        "found": True,
                                        "estimated": False,
                                        "min": min(prices),
                                        "max": max(prices),
                                        "avg": sum(prices) / len(prices),
                                        "count": len(prices),
                                        "source": "ebay_finding_api"
                                    }
            
            logger.info(f"No eBay results found for: {keywords}")
            return {"found": False, "estimated": False}
            
        except Exception as e:
            logger.error(f"eBay API search error: {str(e)}")
            return {"found": False, "estimated": False}
    
    async def search_shopify_api(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search Shopify stores (Note: This requires access to specific stores)
        For now, returns not found
        """
        # Shopify doesn't have a public product search API across all stores
        # Would need to search individual connected stores
        logger.info("Shopify search not implemented (requires store-specific access)")
        return {"found": False, "estimated": False}
    
    async def search_stockx_api(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search StockX (Note: Requires authentication and specific product data)
        For now, returns not found
        """
        # StockX API requires OAuth and specific product identifiers
        # Would need proper authentication to search
        logger.info("StockX search not implemented (requires OAuth)")
        return {"found": False, "estimated": False}
    
    async def search_etsy_api(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search Etsy marketplace
        For now, returns not found
        """
        logger.info("Etsy search not implemented")
        return {"found": False, "estimated": False}
    
    async def search_amazon_api(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search Amazon (Note: Requires Product Advertising API access)
        For now, returns not found
        """
        logger.info("Amazon search not implemented (requires PA-API access)")
        return {"found": False, "estimated": False}
    
    def _calculate_recommended_price(
        self,
        marketplace_prices: Dict[str, Any],
        search_summary: Dict[str, Any]
    ) -> tuple[float, str]:
        """
        Calculate recommended price based on all marketplace data
        
        Returns:
            (recommended_price, confidence)
        """
        all_prices = []
        has_real_data = False
        
        for marketplace, data in marketplace_prices.items():
            if data.get("found") and not data.get("estimated"):
                has_real_data = True
                # Add all prices (min, avg, max) for better distribution
                if "avg" in data:
                    all_prices.append(data["avg"])
                if "min" in data:
                    all_prices.append(data["min"])
                if "max" in data:
                    all_prices.append(data["max"])
            elif data.get("estimated"):
                # Use estimated prices with lower weight
                if "avg" in data:
                    all_prices.append(data["avg"])
                elif "price" in data:
                    all_prices.append(data["price"])
        
        if not all_prices:
            return 0.0, "none"
        
        # Calculate median for recommended price (more robust than mean)
        all_prices.sort()
        n = len(all_prices)
        if n % 2 == 0:
            recommended_price = (all_prices[n//2 - 1] + all_prices[n//2]) / 2
        else:
            recommended_price = all_prices[n//2]
        
        # Determine confidence
        total_results = search_summary.get("total_results", 0)
        
        if has_real_data and total_results >= 10:
            confidence = "high"
        elif has_real_data and total_results >= 3:
            confidence = "medium"
        elif has_real_data:
            confidence = "low"
        else:
            confidence = "estimated"
        
        return round(recommended_price, 2), confidence

