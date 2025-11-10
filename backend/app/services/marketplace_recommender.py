"""
Marketplace Recommender Service
Recommends the best marketplaces for a product based on category and compatibility
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MarketplaceRecommender:
    # Matrice de compatibilité produit-marketplace
    # Categories that each marketplace specializes in or accepts
    MARKETPLACE_CATEGORIES = {
        "stockx": {
            "primary": ["sneakers", "streetwear", "collectibles", "watches", "trading cards", "handbags"],
            "secondary": ["accessories", "electronics"],
            "excluded": ["handmade", "vintage", "food", "plants", "services"]
        },
        "ebay": {
            "primary": ["all"],  # eBay accepts almost everything
            "secondary": [],
            "excluded": ["illegal", "prohibited"]
        },
        "shopify": {
            "primary": ["all"],  # Shopify is a store platform, accepts everything
            "secondary": [],
            "excluded": []
        },
        "etsy": {
            "primary": ["handmade", "vintage", "crafts", "art", "jewelry", "home_decor"],
            "secondary": ["collectibles", "clothing", "accessories"],
            "excluded": ["mass_produced", "dropshipping", "resale"]
        },
        "amazon": {
            "primary": ["electronics", "books", "home", "toys", "sports", "clothing"],
            "secondary": ["collectibles", "jewelry"],
            "excluded": ["handmade", "vintage", "used"]  # Unless specific programs
        },
        "kaufland": {
            "primary": ["electronics", "home", "toys", "sports", "clothing", "food"],
            "secondary": ["books", "health"],
            "excluded": []
        },
        "bol": {
            "primary": ["electronics", "books", "media", "toys", "home"],
            "secondary": ["clothing", "sports"],
            "excluded": []
        }
    }
    
    # Category keywords mapping for better matching
    CATEGORY_KEYWORDS = {
        "sneakers": ["shoe", "sneaker", "trainer", "footwear", "kicks"],
        "streetwear": ["hoodie", "tee", "shirt", "jacket", "pants", "supreme", "bape"],
        "collectibles": ["collectible", "limited", "edition", "rare", "vintage", "antique"],
        "watches": ["watch", "timepiece", "rolex", "omega", "seiko"],
        "electronics": ["phone", "computer", "laptop", "tablet", "camera", "audio", "gaming"],
        "handmade": ["handmade", "craft", "artisan", "custom", "diy"],
        "vintage": ["vintage", "retro", "antique", "old", "classic"],
        "jewelry": ["jewelry", "necklace", "ring", "bracelet", "earring", "gold", "silver"],
        "art": ["art", "painting", "print", "sculpture", "drawing"],
        "clothing": ["clothing", "apparel", "wear", "fashion", "dress", "pants", "shirt"],
        "accessories": ["bag", "wallet", "belt", "hat", "scarf", "sunglasses"],
        "books": ["book", "novel", "textbook", "manga", "comic"],
        "toys": ["toy", "game", "puzzle", "action figure", "doll", "lego"],
        "home_decor": ["decor", "furniture", "lamp", "vase", "pillow", "decoration"]
    }
    
    async def recommend_marketplaces(
        self,
        product_info: Dict[str, Any],
        user_connected_marketplaces: List[str]
    ) -> Dict[str, Any]:
        """
        Recommend the best marketplaces for a product
        
        Args:
            product_info: Product information from analysis
            user_connected_marketplaces: List of marketplace IDs user is connected to
            
        Returns:
            {
                "recommended": [
                    {
                        "marketplace": "ebay",
                        "score": 0.95,
                        "reason": "Large audience for electronics",
                        "connected": True,
                        "priority": "high"  # high, medium, low
                    },
                    ...
                ],
                "incompatible": [
                    {
                        "marketplace": "stockx",
                        "reason": "Not a sneaker or streetwear item",
                        "connected": False
                    }
                ],
                "suggestions": [
                    "Consider connecting to eBay for broader reach",
                    ...
                ]
            }
        """
        logger.info(f"Recommending marketplaces for: {product_info.get('product_name')}")
        
        category = product_info.get('category', '').lower()
        subcategory = product_info.get('subcategory', '').lower()
        product_name = product_info.get('product_name', '').lower()
        brand = product_info.get('brand', '').lower()
        condition = product_info.get('condition', 'used').lower()
        
        # Detect product categories from text
        detected_categories = self._detect_categories(
            f"{category} {subcategory} {product_name} {brand}"
        )
        
        recommended = []
        incompatible = []
        suggestions = []
        
        # Evaluate each marketplace
        for marketplace, rules in self.MARKETPLACE_CATEGORIES.items():
            score, reason, is_compatible = self._evaluate_marketplace(
                marketplace,
                rules,
                detected_categories,
                condition,
                product_info
            )
            
            is_connected = marketplace in user_connected_marketplaces
            
            if is_compatible:
                priority = "high" if score >= 0.8 else "medium" if score >= 0.5 else "low"
                
                recommended.append({
                    "marketplace": marketplace,
                    "score": score,
                    "reason": reason,
                    "connected": is_connected,
                    "priority": priority
                })
                
                # Generate suggestions for non-connected high-priority marketplaces
                if not is_connected and score >= 0.7:
                    suggestions.append(
                        f"Consider connecting to {marketplace.title()} - {reason}"
                    )
            else:
                incompatible.append({
                    "marketplace": marketplace,
                    "reason": reason,
                    "connected": is_connected
                })
        
        # Sort recommended by score (highest first)
        recommended.sort(key=lambda x: x['score'], reverse=True)
        
        # Add general suggestions
        if not any(r['connected'] for r in recommended):
            suggestions.append("No marketplaces connected. Connect to at least one marketplace to start selling.")
        elif len([r for r in recommended if r['connected']]) < 2:
            suggestions.append("Connect to more marketplaces to increase your reach and sales potential.")
        
        result = {
            "recommended": recommended,
            "incompatible": incompatible,
            "suggestions": suggestions
        }
        
        logger.info(f"Recommended {len(recommended)} marketplaces, {len(incompatible)} incompatible")
        
        return result
    
    def _detect_categories(self, text: str) -> List[str]:
        """Detect product categories from text using keywords"""
        detected = []
        text_lower = text.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(category)
        
        # If nothing detected, assume general
        if not detected:
            detected.append("general")
        
        return detected
    
    def _evaluate_marketplace(
        self,
        marketplace: str,
        rules: Dict[str, List[str]],
        detected_categories: List[str],
        condition: str,
        product_info: Dict[str, Any]
    ) -> tuple[float, str, bool]:
        """
        Evaluate if a marketplace is suitable for a product
        
        Returns:
            (score, reason, is_compatible)
        """
        primary = rules.get("primary", [])
        secondary = rules.get("secondary", [])
        excluded = rules.get("excluded", [])
        
        # Check exclusions first
        for cat in detected_categories:
            if cat in excluded:
                return (
                    0.0,
                    f"{marketplace.title()} does not accept {cat} items",
                    False
                )
        
        # Special rules for specific marketplaces
        if marketplace == "etsy":
            # Etsy doesn't accept mass-produced or resale unless vintage
            if condition != "new" and "vintage" not in detected_categories and "handmade" not in detected_categories:
                if "collectibles" not in detected_categories:
                    return (
                        0.0,
                        "Etsy primarily accepts handmade, vintage (20+ years), or craft supplies",
                        False
                    )
        
        if marketplace == "stockx":
            # StockX is very category-specific
            has_stockx_category = any(cat in primary for cat in detected_categories)
            if not has_stockx_category:
                return (
                    0.0,
                    "StockX specializes in sneakers, streetwear, collectibles, and watches only",
                    False
                )
        
        if marketplace == "amazon":
            # Amazon typically doesn't accept used items in regular listings
            if condition in ["used", "fair", "poor"]:
                return (
                    0.3,
                    "Amazon primarily for new items (used items require special programs)",
                    True  # Still compatible but low score
                )
        
        # Calculate compatibility score
        score = 0.0
        reason_parts = []
        
        # Check if "all" is in primary (eBay, Shopify)
        if "all" in primary:
            score = 0.9
            reason_parts.append(f"accepts all product types")
        else:
            # Check primary categories
            primary_matches = [cat for cat in detected_categories if cat in primary]
            if primary_matches:
                score = 0.9
                reason_parts.append(f"specializes in {', '.join(primary_matches)}")
            
            # Check secondary categories
            secondary_matches = [cat for cat in detected_categories if cat in secondary]
            if secondary_matches and not primary_matches:
                score = 0.6
                reason_parts.append(f"accepts {', '.join(secondary_matches)}")
            
            # If no matches, low score but still compatible
            if not primary_matches and not secondary_matches:
                score = 0.3
                reason_parts.append("accepts this category but not specialized")
        
        # Boost score for condition-appropriate marketplaces
        if condition == "new":
            if marketplace in ["amazon", "shopify"]:
                score = min(score + 0.1, 1.0)
                reason_parts.append("great for new items")
        elif condition in ["like_new", "good"]:
            if marketplace in ["ebay", "stockx"]:
                score = min(score + 0.1, 1.0)
                reason_parts.append("handles used items well")
        
        # Brand boost for luxury/streetwear brands on StockX
        brand = product_info.get('brand', '').lower()
        if marketplace == "stockx" and brand in ["nike", "adidas", "supreme", "jordan", "yeezy", "rolex", "omega"]:
            score = min(score + 0.15, 1.0)
            reason_parts.append("popular brand on platform")
        
        reason = f"{marketplace.title()} {', '.join(reason_parts)}"
        
        # Compatible if score > 0
        is_compatible = score > 0
        
        return (round(score, 2), reason, is_compatible)

