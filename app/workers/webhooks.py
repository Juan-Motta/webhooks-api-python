from typing import Dict

from ..repositories.webhooks.webhooks import get_webhook_by_id
from ..repositories.services.services import get_service_by_id

def validate_message(message: Dict) -> None:
    if not isinstance(message, dict):
        raise ValueError("[x] Message must be a dictionary")
    if not "user_id" in message or not "service_id" in message or not "event_pattern" in message:
        raise ValueError("[x] user_id, service_id and event_pattern are required")
    if not str(message["user_id"]).isnumeric() or not str(message["service_id"]).isnumeric():
        raise ValueError("[x] user_id and service_id must be numeric")
    if not message["event_pattern"]:
        raise ValueError("[x] event_pattern must not be blank")

def process_message(message: Dict):
    validate_message(message)
    
    user_id = message["user_id"]
    event_pattern = message["event_pattern"]
    service_id = message["service_id"]
    
    webhooks = get_webhook_by_id(user_id=user_id, event_pattern=event_pattern)
    service = get_service_by_id(service_id=service_id)
    
    for webhook in webhooks:
        continue
    