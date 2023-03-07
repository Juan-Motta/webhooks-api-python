from typing import List, Dict

from app.main import app

async def get_all_webhooks() -> List[Dict]:
    query: str = f"""
    SELECT
        w.id,
        w.user_id,
        w.event_pattern,
        w.webhook_url,
        w.headers,
        w.payload,
        w.method,
        w.active,
        w.created_at,
        w.updated_at,
        w.attempts
    FROM webhooks w  
    """
    data = await app.state.service_db.execute(query)
    return data

async def get_webhook(user_id: int, event_pattern: str) -> List[Dict]:
    query: str = f"""
    SELECT
        w.id,
        w.user_id,
        w.event_pattern,
        w.webhook_url,
        w.headers,
        w.payload,
        w.method,
        w.active,
        w.created_at,
        w.updated_at,
        w.attempts
    FROM webhooks w
    WHERE w.user_id = {user_id}
    AND w.event_pattern = '{event_pattern}'
    """
    data = await app.state.service_db.execute(query)
    return data