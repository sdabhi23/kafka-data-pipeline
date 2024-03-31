from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.admin import AdminClient, NewTopic

from commons import Config, TOPICS_TO_SETUP, SCHEMA_TO_SETUP

print("Setting up Kafka topics...")

admin_client = AdminClient({"bootstrap.servers": Config.BOOTSTRAP_SERVERS_LOCAL, "client.id": "setup-kafka"})

topics = []

for topic_name in TOPICS_TO_SETUP:
    kafka_topic = NewTopic(
        topic=topic_name,
        num_partitions=4,
        replication_factor=1,
        config={"retention.ms": 24 * 60 * 60 * 1000, "segment.ms": 24 * 60 * 60 * 1000},
    )

    topics.append(kafka_topic)

created_topics = admin_client.create_topics(new_topics=topics, validate_only=False)

for topic, future in created_topics.items():
    try:
        future.result()
        print(f"Topic '{topic}' created successfully with 1 day data retention.")
    except Exception as e:
        print(f"Failed to create topic '{topic}': {e}")

print("Setting up schemas in schema registry...")

schema_registry_client = SchemaRegistryClient({"url": Config.SCHEMA_REGISTRY_URL_LOCAL})

for schema_subject in SCHEMA_TO_SETUP:
    topic_name = schema_subject.replace('-value', '')
    print(f"Processing schema for {topic_name}")

    with open(f"app/avro/{topic_name}.avsc") as f:
        schema_str = f.read()

    schema = Schema(schema_str, "AVRO")

    try:
        schema_id = schema_registry_client.register_schema(schema_subject, schema)
        print(f"Schema registered successfully with schema id: {schema_id}")
    except Exception as e:
        print(f"Schema registration failed with error: {e}")
