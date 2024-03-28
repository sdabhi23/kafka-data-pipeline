from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.admin import AdminClient, NewTopic

from commons import Config


admin_client = AdminClient({"bootstrap.servers": Config.BOOTSTRAP_SERVERS, "client.id": "setup-kafka"})

transactions_topic = NewTopic(
    topic=Config.TOPIC_NAME,
    num_partitions=4,
    replication_factor=1,
    config={"retention.ms": 24 * 60 * 60 * 1000, "segment.ms": 24 * 60 * 60 * 1000},
)

created_topics = admin_client.create_topics(new_topics=[transactions_topic], validate_only=False)

for topic, future in created_topics.items():
    try:
        future.result()
        print(f"Topic '{Config.TOPIC_NAME}' created successfully with 1 day data retention.")
    except Exception as e:
        print(f"Failed to create topic '{Config.TOPIC_NAME}': {e}")

with open(f"app/avro/transaction.avsc") as f:
    schema_str = f.read()

record_schema = Schema(schema_str, "AVRO")

schema_registry_client = SchemaRegistryClient({"url": Config.SCHEMA_REGISTRY_URL})

try:
    schema_id = schema_registry_client.register_schema(Config.TOPIC_NAME, record_schema)
    print(f"Schema for transactions registered successfully with schema id: {schema_id}")
except Exception as e:
    print(f"Schema registration failed with error: {e}")
