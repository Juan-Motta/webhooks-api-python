import asyncio
import asyncpg
from asyncpg.exceptions import PostgresError


class Database:
    """
    Database connection handler, it manage the database connection and handles the errors
    """
    
    def __init__(self, host: str, name: str, user: str, password: str, port: str) -> None:
        self._name: str = name
        self.dsn=(f"postgresql://{user}:{password}@{host}:{port}/{name}")
        self.conn = None

    async def connect(self) -> None:
        """
        Creates db connection
        """
        try:
            self.conn = await asyncpg.connect(self.dsn)
            print(f"[x] {self._name.capitalize()} database connection ... OK")
        except PostgresError as e:
            print(f"[x] Could not connect to database: {e}")
            await asyncio.sleep(15)
            await self.connect()

    async def disconnect(self) -> None:
        """
        Closes db connection
        """
        await self.conn.close()

    async def execute(self, query: str, *args):
        """
        Executes queries
        Args:
            query
        """
        if not self.conn:
            await self.connect()
        try:
            return await self.conn.execute(query, *args)
        except PostgresError as e:
            print(f"[x] Error executing query: {e}")
            await self.disconnect()
            await asyncio.sleep(5)
            return await self.execute(query, *args)