import asyncio
from aio_pika import (
    Channel,
    connect_robust, 
    Connection,
    exceptions,
    Message,
    Queue
)
from .config.app import (
    RABBIT_HOST,
    RABBIT_USER,
    RABBIT_PASSWORD,
    RABBIT_NOTIFICATION_QUEUE
)

async def start_amqp_listener(app) -> None:
    """
    Starts AQMP connection for the listener logic that is goin to be running in background, it
    also defines a message handler that is goind to execute the logic for each message the listener
    receives
    Args:
        app: fastapi instance
    """
    connection: Connection = await connect()
    app.state.rabbit = connection
    channel: Channel = await connection.channel()
    queue: Queue = await channel.declare_queue(
        f"{RABBIT_NOTIFICATION_QUEUE}", 
        durable=True
    )
    
    async def message_handler(message: Message) -> None:
        async with message.process():
            print(message.body)

    await queue.consume(message_handler)

async def connect() -> Connection:
    """
    Generates the RabbitMQ connection, if connection cannot be stablished, a new task is
    queue to retry in X seconds 
    """
    while True:
        try:
            connection: Connection = await connect_robust(
                f"amqp://{RABBIT_USER}:{RABBIT_PASSWORD}@{RABBIT_HOST}/"
            )
            print("[x] RabbitMQ connected ... OK")
            return connection
        except exceptions.AMQPConnectionError:
            print("[x] Failed to connect to RabbitMQ, retrying...")
            await asyncio.sleep(60)

async def check_amqp_connection(app) -> None:
    """
    Validates every X seconds if rabbit connection is healthy, if not it tries every X seconds
    to reconnect
    Args:
        app: fastapi instance
    """
    connection: Connection = app.state.rabbit
    while True:
        if connection is not None and connection.is_closed:
            await connect()
        await asyncio.sleep(60)