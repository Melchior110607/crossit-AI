from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.webhook_event import WebhookEvent
import json

router = APIRouter()


@router.post("/{marketplace_name}")
async def receive_webhook(
    marketplace_name: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Receive webhook from marketplace"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # TODO: Verify webhook signature/authentication per marketplace
        
        # Store webhook event
        webhook_event = WebhookEvent(
            marketplace_name=marketplace_name,
            event_type=payload.get("type", "unknown"),
            payload=json.dumps(payload),
            processed=False
        )
        db.add(webhook_event)
        db.commit()
        
        # TODO: Trigger async processing task
        
        return {"status": "received", "event_id": webhook_event.id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/events")
def get_webhook_events(
    marketplace_name: str = None,
    processed: bool = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get webhook events (for debugging/monitoring)"""
    query = db.query(WebhookEvent)
    
    if marketplace_name:
        query = query.filter(WebhookEvent.marketplace_name == marketplace_name)
    
    if processed is not None:
        query = query.filter(WebhookEvent.processed == processed)
    
    events = query.order_by(WebhookEvent.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "events": [
            {
                "id": e.id,
                "marketplace_name": e.marketplace_name,
                "event_type": e.event_type,
                "processed": e.processed,
                "created_at": e.created_at,
                "processed_at": e.processed_at
            }
            for e in events
        ],
        "total": len(events)
    }

