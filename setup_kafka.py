from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.admin import AdminClient, NewTopic


admin_client = AdminClient({"bootstrap.servers": "localhost:19092", "client.id": "setup_kafka"})
topic_name = "transactions"
transactions_topic = NewTopic(
    topic=topic_name,
    num_partitions=4,
    replication_factor=1,
    config={"retention.ms": 24 * 60 * 60 * 1000, "segment.ms": 24 * 60 * 60 * 1000},
)

created_topics = admin_client.create_topics(new_topics=[transactions_topic], validate_only=False)

for topic, future in created_topics.items():
    try:
        future.result()
        print(f"Topic '{topic_name}' created successfully with 1 day data retention.")
    except Exception as e:
        print(f"Failed to create topic '{topic_name}': {e}")


record_schema = Schema(
    """
{
  "type": "record",
  "name": "TransactionRecord",
  "fields": [
    {"name": "user_id", "type": "int"},
    {"name": "transaction_timestamp_millis", "type": "long"},
    {"name": "amount", "type": "float"},
    {"name": "currency", "type": "string"},
    {"name": "counterpart_id", "type": "int"}
  ]
}
""",
    "AVRO",
)

schema_registry_client = SchemaRegistryClient({"url": "http://localhost:18081"})

try:
    schema_id = schema_registry_client.register_schema("transaction", record_schema)
    print(f"Schema for transactions registered successfully with schema id: {schema_id}")
except Exception as e:
    print(f"Schema registration failed with error: {e}")
