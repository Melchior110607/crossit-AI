"""
Webhooks API (SUPABASE VERSION)
Receive and manage webhook events from marketplaces
"""
from fastapi import APIRouter, Request, HTTPException, status
from app.core.supabase import supabase_admin
from datetime import datetime
from typing import Optional
import json

router = APIRouter()


@router.post("/{marketplace_name}")
async def receive_webhook(
    marketplace_name: str,
    request: Request
):
    """Receive webhook from marketplace"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # TODO: Verify webhook signature/authentication per marketplace
        
        # Store webhook event in Supabase
        webhook_data = {
            "marketplace_name": marketplace_name,
            "event_type": payload.get("type", "unknown"),
            "payload": json.dumps(payload),
            "processed": False,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase_admin.table("webhook_events").insert(webhook_data).execute()
        
        if not response.data:
            raise Exception("Failed to store webhook event")
        
        # TODO: Trigger async processing task (Celery)
        
        return {"status": "received", "event_id": response.data[0]["id"]}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/events")
async def get_webhook_events(
    marketplace_name: Optional[str] = None,
    processed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get webhook events (for debugging/monitoring)"""
    query = supabase_admin.table("webhook_events").select("*")
    
    if marketplace_name:
        query = query.eq("marketplace_name", marketplace_name)
    
    if processed is not None:
        query = query.eq("processed", processed)
    
    query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
    
    response = query.execute()
    
    return {
        "events": [
            {
                "id": e["id"],
                "marketplace_name": e["marketplace_name"],
                "event_type": e["event_type"],
                "processed": e["processed"],
                "created_at": e["created_at"],
                "processed_at": e.get("processed_at")
            }
            for e in response.data
        ],
        "total": len(response.data)
    }
