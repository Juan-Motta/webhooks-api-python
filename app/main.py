import asyncio
from fastapi import FastAPI
from .amqp import (
    start_amqp_listener,
    check_amqp_connection
)
from .db import (
    start_services_db_connection,
    start_webhooks_db_connection,
    check_services_connection,
    check_webhooks_connection,
)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await start_amqp_listener(app)
    await start_services_db_connection(app)
    await start_webhooks_db_connection(app)
    asyncio.create_task(check_services_connection(app))
    asyncio.create_task(check_webhooks_connection(app))
    asyncio.create_task(check_amqp_connection(app))

@app.on_event("shutdown")
async def shutdown():
    await app.state.webhooks_db.close()
    await app.state.services_db.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items")
async def read_items():
    async with app.state.db.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM webhooks")
        return rows

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup_event())
    loop.run_forever()
