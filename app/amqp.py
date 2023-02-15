import asyncio
from aio_pika import connect_robust, RobustConnection
from aio_pika.abc import AbstractChannel, AbstractQueue
from aiormq.connection import parse_bool, parse_timeout

from .config.app import RABBIT


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
        if self.transport is None:
            print(f"""[x] RabbitMQ connection list, retry in {RABBIT["reconnection_time"]}""")


async def start_amqp_listener(app) -> None:
    """
    Starts AQMP connection for the listener logic that is goin to be running in background, it
    also defines a message handler that is goind to execute the logic for each message the listener
    receives
    Args:
        app: fastapi instance
    """
    connection = await connect_robust(
        f"""amqp://{RABBIT["user"]}:{RABBIT["password"]}@{RABBIT["host"]}:{RABBIT["port"]}/""",
        client_properties={"connection_name": "webhooks"},
        connection_class=CustomRobustConnection,
        reconnect_interval=15
    )
    async with connection:
        print("[x] RabbitMQ connected ... OK")
        app.state.rabbit = connection
        queue_name: str = RABBIT["notification_queue"]
        channel: AbstractChannel = await connection.channel()
        queue: AbstractQueue = await channel.declare_queue(
            queue_name,
            durable=True
        )
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)

                    if queue.name in message.body.decode():
                        break