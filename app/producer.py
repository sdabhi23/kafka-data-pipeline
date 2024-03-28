import time
import random
from faker import Faker
from confluent_kafka import Producer, SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


from commons import Config

registry_client = SchemaRegistryClient({"url": Config.SCHEMA_REGISTRY_URL})
latest_version = registry_client.get_latest_version(Config.TOPIC_NAME)

value_avro_serializer = AvroSerializer(
    schema_registry_client=registry_client,
    schema_str=latest_version.schema.schema_str,
    conf={
        "auto.register.schemas": False,
        "subject.name.strategy": lambda ctx, record_name: ctx.topic,
    },
)

# Kafka Producer
producer = SerializingProducer(
    {
        "bootstrap.servers": Config.BOOTSTRAP_SERVERS,
        "security.protocol": "plaintext",
        "value.serializer": value_avro_serializer,
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
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


while True:
    try:
        data = {
            "user_id": fake.random_int(min=1, max=1000),
            "transaction_timestamp_millis": int(time.time() * 1000),
            "amount": round(random.uniform(-1000, 1000), 2),
            "currency": fake.currency_code(),
            "counterpart_id": fake.random_int(min=1, max=1000),
        }
        producer.produce(Config.TOPIC_NAME, value=data, on_delivery=delivery_report)

        # Trigger any available delivery report callbacks from previous produce() calls
        events_processed = producer.poll(1)
        print(f"events_processed: {events_processed}")

        messages_in_queue = producer.flush(1)
        print(f"messages_in_queue: {messages_in_queue}")

        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting due to manual interrupt...")
    except Exception as e:
        print(e)
        raise
    finally:
        events_processed = producer.poll(1)
        print(f"events_processed: {events_processed}")

        messages_in_queue = producer.flush(1)
        print(f"messages_in_queue: {messages_in_queue}")
