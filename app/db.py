import asyncio
import asyncpg
from .config.app import (
    DB_SERVICES_HOST,
    DB_SERVICES_NAME,
    DB_SERVICES_PASSWORD,
    DB_SERVICES_USER,
    DB_WEBHOOKS_HOST,
    DB_WEBHOOKS_NAME,
    DB_WEBHOOKS_PASSWORD,
    DB_WEBHOOKS_USER
)

async def start_webhooks_db_connection(app):
    """
    Creates a connection to webhooks database
    Args:
        app: fastapi instance
    """
    app.state.webhooks_db = await asyncpg.create_pool(
        dsn=("postgresql://{user}:{password}@{host}/{name}"
            .format(
                user=DB_WEBHOOKS_USER,
                password=DB_WEBHOOKS_PASSWORD,
                host=DB_WEBHOOKS_HOST,
                name=DB_WEBHOOKS_NAME
            )
        )
    )
    print("[x] Webhooks database connected ... OK")
    
async def start_services_db_connection(app):
    """
    Creates a connection to services database
    Args:
        app: fastapi instance
    """
    app.state.services_db = await asyncpg.create_pool(
        dsn=("postgresql://{user}:{password}@{host}/{name}"
            .format(
                user=DB_SERVICES_USER,
                password=DB_SERVICES_PASSWORD,
                host=DB_SERVICES_HOST,
                name=DB_SERVICES_NAME
            )
        )
    )
    print("[x] Services database connected ... OK")
    
async def check_webhooks_connection(app):
    """
    Validates if database connection exists, if so, it makes a query to database to ensure the
    connection is working correctly, if not, it calls to the connection logic to restablish
    the db connection
    Args:
        app: fastapi instance
    """
    while True:
        try:
            async with app.state.webhooks_db.acquire() as connection:
                await connection.fetch("SELECT 1")
        except (
            asyncpg.exceptions.ConnectionDoesNotExistError, 
            asyncpg.exceptions.ConnectionFailureError
        ):
            print("[x] Failed to connect to webhooks database, retrying...")
            await start_webhooks_db_connection()
        await asyncio.sleep(60)
        
async def check_services_connection(app):
    """
    Validates if database connection exists, if so, it makes a query to database to ensure the
    connection is working correctly, if not, it calls to the connection logic to restablish
    the db connection
    Args:
        app: fastapi instance
    """
    while True:
        try:
            async with app.state.services_db.acquire() as connection:
                await connection.fetch("SELECT 1")
        except (
            asyncpg.exceptions.ConnectionDoesNotExistError, 
            asyncpg.exceptions.ConnectionFailureError
        ):
            print("[x] Failed to connect to services database, retrying...")
            await start_services_db_connection()
        await asyncio.sleep(60)