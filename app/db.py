import json
import asyncio
from asyncpg import connect, Connection
from asyncpg.exceptions import PostgresError
from typing import Optional, List

class Database:
    """
    Database connection handler, it manage the database connection and handles the errors
    """
    
    _name: str
    _dsn: str
    _conn: Optional[Connection]
    
    def __init__(self, host: str, name: str, user: str, password: str, port: str) -> None:
        self._name: str = name
        self._dsn = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        self._conn = None

    async def connect(self) -> None:
        """
        Creates db connection
        """
        try:
            self._conn = await connect(self._dsn)
            await self._conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )
            print(f"[x] {self._name.capitalize()} database connection ... OK")
        except PostgresError as e:
            print(f"[x] Could not connect to database: {e}")
            await asyncio.sleep(15)
            await self.connect()

    async def disconnect(self) -> None:
        """
        Closes db connection
        """
        await self._conn.close()

    async def execute(self, query: str, *args: Optional[List]):
        """
        Executes queries
        Args:
            query
        """
        if not self._conn:
            await self.connect()
        try:
            return await self._conn.fetch(query, *args)
        except PostgresError as e:
            print(f"[x] Error executing query: {e}")
            await self.disconnect()
            await asyncio.sleep(5)
            return await self.execute(query, *args)