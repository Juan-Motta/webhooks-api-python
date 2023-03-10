import asyncio
import json
from aio_pika import connect_robust, RobustConnection
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractRobustConnection
from aiormq.connection import parse_bool, parse_timeout

from .app import app
from .config.app import RABBIT
from .workers.webhooks import process_message

class CustomRobustConnection(RobustConnection):
    """
    Override RobustConnection class from aio-pika
    """
    KWARGS_TYPES = (
        ("reconnect_interval", parse_timeout, RABBIT["reconnection_time"]),
        ("fail_fast", parse_bool, "1"),
    )
    
    async def _on_connection_close(self, closing: asyncio.Future) -> None:
        """
        Override methods that is called when the connection with RabbitMQ is closed or lost
        Args:
            closing: internal object of RobustConnection
        """
        await super()._on_connection_close(closing)
        # self.transport is a way to identify is the connection with broker has lost because
        # when connection start this method is evaluated and it generates a false-positive alert
        if self.transport is None:
            print(f"""[x] RabbitMQ connection list, retry in {RABBIT["reconnection_time"]}""")


async def start_amqp_listener() -> None:
    """
    Starts AQMP connection for the listener logic that is goin to be running in background, it
    also defines a message handler that is goind to execute the logic for each message the listener
    receives
    Args:
        app: fastapi instance
    """
    try:             
        connection: AbstractRobustConnection = await connect_robust(
            f"""amqp://{RABBIT["user"]}:{RABBIT["password"]}@{RABBIT["host"]}:{RABBIT["port"]}/""",
            client_properties={"connection_name": "webhooks"},
            connection_class=CustomRobustConnection,
        )
        app.state.rabbit = connection
        channel: AbstractChannel = await connection.channel()
        queue: AbstractQueue = await channel.declare_queue(
            RABBIT["notification_queue"],
            durable=True
        )
        print("[x] RabbitMQ connected ... OK")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body)
                    process_message(data)
    except Exception as e:
        print(e)