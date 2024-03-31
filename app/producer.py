import time
import random
from faker import Faker
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


from commons import Config

# Fetch schema from registry
registry_client = SchemaRegistryClient({"url": Config.SCHEMA_REGISTRY_URL_LOCAL})
latest_version = registry_client.get_latest_version(Config.SCHEMA_SUBJECT_TRANSACTIONS)

transaction_avro_serializer = AvroSerializer(
    schema_registry_client=registry_client,
    schema_str=latest_version.schema.schema_str,
    conf={
        "auto.register.schemas": False,
    },
)

# Initialize Kafka producer
producer = SerializingProducer(
    {
        "bootstrap.servers": Config.BOOTSTRAP_SERVERS_LOCAL,
        "security.protocol": "plaintext",
        "value.serializer": transaction_avro_serializer,
        "delivery.timeout.ms": 120000,
        "enable.idempotence": "true",
        "client.id": "transactions-producer",
    }
)

# Initialise faker
fake = Faker()


# Function to handle delivery reports
def delivery_report(err, msg):
    if err is not None:
        print("Message delivery failed:", err)
    else:
        print(f"Message delivered to {msg.topic()} [partition: {msg.partition()}] [key: {msg.key().decode()}]")


# Function to trigger any available delivery report callbacks from previous produce() calls
def cleanup(producer, extra = None):
    if extra is not None:
        print(extra)

    events_processed = producer.poll(1)
    print(f"Events_processed: {events_processed}")

    messages_in_queue = producer.flush(1)
    print(f"Messages_in_queue: {messages_in_queue}")


while True:
    try:
        data = {
            "user_id": fake.random_int(min=1, max=20),
            "transaction_timestamp_millis": int(time.time() * 1000),
            "amount": round(random.uniform(-1000, 1000), 2),
            "currency": fake.currency_code(),
            "counterpart_id": fake.random_int(min=30, max=50),
        }

        producer.produce(Config.TOPIC_NAME_TRANSACTIONS, key=str(data["user_id"]).zfill(2).encode(), value=data, on_delivery=delivery_report)

        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting due to manual interrupt...")
        break
    except Exception as e:
        print(e)
        raise
    finally:
        # Trigger any available delivery report callbacks from previous produce() calls
        cleanup(producer)
