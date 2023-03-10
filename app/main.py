import asyncio

from .amqp import start_amqp_listener
from .config.app import WEBHOOKS_DB, SERVICES_DB
from .db import Database
from .app import app

@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialices databases and RabbitMQ listener when service starts
    """
    webhook_db = Database(**WEBHOOKS_DB)
    service_db = Database(**SERVICES_DB)
    await service_db.connect()
    app.state.service_db = service_db
    await webhook_db.connect()
    app.state.webhook_db = webhook_db
    asyncio.create_task(start_amqp_listener())

@app.on_event("shutdown")
async def shutdown() -> None:
    """
    Closes databases connections when services shuts down
    """
    await app.state.webhooks_db.disconnect()
    await app.state.services_db.disconnect()
    await app.state.rabbit.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items")
async def read_items():
    from app.repositories.services.services import get_service_by_id
    data = await get_service_by_id(3191045)
    return data

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup_event())
    loop.run_forever()
