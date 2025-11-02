from typing import Dict
from app.integrations.base_connector import BaseMarketplaceConnector
from app.integrations.amazon_connector import AmazonConnector
from app.integrations.ebay_connector import EbayConnector
from app.integrations.etsy_connector import EtsyConnector
from app.integrations.bol_connector import BolConnector
from app.integrations.allegro_connector import AllegroConnector
from app.integrations.shopify_connector import ShopifyConnector
from app.integrations.marketplace_templates import (
    KauflandConnector,
    OnBuyConnector,
    WishConnector,
    JoomConnector,
    ZalandoConnector,
    AboutYouConnector,
    OttoConnector,
    CdiscountConnector,
    FnacDartyConnector,
    VintedConnector,
    StockXConnector,
    LaRedouteConnector,
    GaleriesLafayetteConnector,
    AsosConnector
)


class ConnectorFactory:
    """Factory class to create marketplace connectors"""
    
    _connectors = {
        "amazon": AmazonConnector,
        "ebay": EbayConnector,
        "etsy": EtsyConnector,
        "bol": BolConnector,
        "allegro": AllegroConnector,
        "kaufland": KauflandConnector,
        "onbuy": OnBuyConnector,
        "wish": WishConnector,
        "joom": JoomConnector,
        "zalando": ZalandoConnector,
        "aboutyou": AboutYouConnector,
        "otto": OttoConnector,
        "cdiscount": CdiscountConnector,
        "fnac_darty": FnacDartyConnector,
        "vinted": VintedConnector,
        "stockx": StockXConnector,
        "shopify": ShopifyConnector,
        "la_redoute": LaRedouteConnector,
        "galeries_lafayette": GaleriesLafayetteConnector,
        "asos": AsosConnector,
    }
    
    @classmethod
    def create_connector(
        cls,
        marketplace_name: str,
        config: Dict[str, str]
    ) -> BaseMarketplaceConnector:
        """
        Create and return a marketplace connector instance
        
        Args:
            marketplace_name: Name of the marketplace
            config: Configuration dictionary with API credentials
            
        Returns:
            Marketplace connector instance
            
        Raises:
            ValueError: If marketplace is not supported
        """
        connector_class = cls._connectors.get(marketplace_name.lower())
        
        if not connector_class:
            raise ValueError(f"Marketplace '{marketplace_name}' is not supported")
        
        return connector_class(config)
    
    @classmethod
    def register_connector(cls, marketplace_name: str, connector_class):
        """Register a new marketplace connector"""
        cls._connectors[marketplace_name.lower()] = connector_class
    
    @classmethod
    def get_supported_marketplaces(cls) -> list:
        """Get list of supported marketplace names"""
        return list(cls._connectors.keys())

