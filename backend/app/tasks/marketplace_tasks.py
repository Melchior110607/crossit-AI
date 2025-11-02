from celery import shared_task
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.listing import Listing
from app.models.product import Product
from app.models.marketplace_connection import MarketplaceConnection
from app.models.webhook_event import WebhookEvent
from app.integrations.connector_factory import ConnectorFactory
from datetime import datetime, timedelta
import json


@celery_app.task(name="sync_marketplace_listings")
def sync_marketplace_listings(user_id: int, marketplace_name: str):
    """Synchronize listings from a marketplace"""
    db = SessionLocal()
    try:
        # Get user's marketplace connection
        connection = db.query(MarketplaceConnection).filter(
            MarketplaceConnection.user_id == user_id,
            MarketplaceConnection.marketplace_name == marketplace_name,
            MarketplaceConnection.is_active == True
        ).first()
        
        if not connection:
            return {"error": "No active connection found"}
        
        # Create connector
        config = {"access_token": connection.access_token}
        connector = ConnectorFactory.create_connector(marketplace_name, config)
        
        # Fetch listings from marketplace
        marketplace_listings = connector.get_listings(connection.access_token)
        
        # Update local database
        synced_count = 0
        for mp_listing in marketplace_listings:
            listing = db.query(Listing).filter(
                Listing.marketplace_listing_id == mp_listing.get("id")
            ).first()
            
            if listing:
                # Update existing listing
                listing.status = mp_listing.get("status", "active")
                listing.synced_at = datetime.utcnow()
                synced_count += 1
        
        # Update connection sync time
        connection.last_synced_at = datetime.utcnow()
        db.commit()
        
        return {"synced": synced_count, "marketplace": marketplace_name}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="publish_listing_task")
def publish_listing_task(product_id: int, marketplace_name: str, user_id: int, custom_price: float = None):
    """Asynchronously publish a product listing to a marketplace"""
    db = SessionLocal()
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "Product not found"}
        
        # Get marketplace connection
        connection = db.query(MarketplaceConnection).filter(
            MarketplaceConnection.user_id == user_id,
            MarketplaceConnection.marketplace_name == marketplace_name,
            MarketplaceConnection.is_active == True
        ).first()
        
        if not connection:
            return {"error": "No active marketplace connection"}
        
        # Prepare product data
        product_data = {
            "title": product.title,
            "description": product.description,
            "price": custom_price or product.price,
            "images": product.images,
            "sku": product.sku,
            "quantity": product.quantity,
            "brand": product.brand,
            "condition": product.condition,
            "category": product.category,
            "weight": product.weight,
            "dimensions": product.dimensions
        }
        
        # Create connector and publish
        config = {"access_token": connection.access_token}
        connector = ConnectorFactory.create_connector(marketplace_name, config)
        
        result = connector.create_listing(product_data, connection.access_token)
        
        # Create listing record
        listing = Listing(
            product_id=product_id,
            marketplace_name=marketplace_name,
            marketplace_listing_id=result.get("marketplace_listing_id"),
            status=result.get("status", "active"),
            price=custom_price or product.price,
            url=result.get("url"),
            last_sync_status="success"
        )
        db.add(listing)
        db.commit()
        
        return {
            "success": True,
            "listing_id": listing.id,
            "marketplace_listing_id": result.get("marketplace_listing_id")
        }
        
    except Exception as e:
        db.rollback()
        # Update listing with error
        if 'listing' in locals():
            listing.last_sync_status = "failed"
            listing.last_error = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="delete_listing_task")
def delete_listing_task(listing_id: int):
    """Asynchronously delete a listing from marketplace"""
    db = SessionLocal()
    try:
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            return {"error": "Listing not found"}
        
        # Get marketplace connection
        connection = db.query(MarketplaceConnection).filter(
            MarketplaceConnection.marketplace_name == listing.marketplace_name
        ).first()
        
        if connection:
            # Delete from marketplace
            config = {"access_token": connection.access_token}
            connector = ConnectorFactory.create_connector(listing.marketplace_name, config)
            connector.delete_listing(listing.marketplace_listing_id, connection.access_token)
        
        # Update local listing
        listing.status = "deleted"
        db.commit()
        
        return {"success": True, "listing_id": listing_id}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="process_webhook_event")
def process_webhook_event(event_id: int):
    """Process a webhook event"""
    db = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if not event or event.processed:
            return {"error": "Event not found or already processed"}
        
        payload = json.loads(event.payload)
        
        # Process based on event type
        if event.event_type in ["order.created", "sale", "ORDER_STATUS_CHANGE"]:
            # Handle sale event
            # TODO: Update listing status, notify user, etc.
            pass
        
        # Mark as processed
        event.processed = True
        event.processed_at = datetime.utcnow()
        db.commit()
        
        return {"success": True, "event_id": event_id}
        
    except Exception as e:
        event.processing_error = str(e)
        db.commit()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="refresh_marketplace_tokens")
def refresh_marketplace_tokens():
    """Periodic task to refresh expiring marketplace tokens"""
    db = SessionLocal()
    try:
        # Find connections with tokens expiring in next hour
        expiring_soon = datetime.utcnow() + timedelta(hours=1)
        
        connections = db.query(MarketplaceConnection).filter(
            MarketplaceConnection.is_active == True,
            MarketplaceConnection.expires_at != None,
            MarketplaceConnection.expires_at < expiring_soon
        ).all()
        
        refreshed_count = 0
        for connection in connections:
            try:
                config = {}
                connector = ConnectorFactory.create_connector(connection.marketplace_name, config)
                
                # Refresh token
                new_tokens = connector.refresh_token(connection.refresh_token)
                
                # Update connection
                connection.access_token = new_tokens.get("access_token")
                if new_tokens.get("refresh_token"):
                    connection.refresh_token = new_tokens.get("refresh_token")
                if new_tokens.get("expires_at"):
                    connection.expires_at = datetime.utcnow() + timedelta(seconds=new_tokens["expires_at"])
                
                refreshed_count += 1
                
            except Exception as e:
                connection.is_active = False
                print(f"Failed to refresh token for {connection.marketplace_name}: {e}")
        
        db.commit()
        return {"refreshed": refreshed_count}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


# Periodic task configuration
celery_app.conf.beat_schedule = {
    'refresh-tokens-every-30-minutes': {
        'task': 'refresh_marketplace_tokens',
        'schedule': 1800.0,  # 30 minutes
    },
}

