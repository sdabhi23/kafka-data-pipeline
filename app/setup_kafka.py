from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.admin import AdminClient, NewTopic

from commons import Config

print("Setting up Kafka topics...")

admin_client = AdminClient({"bootstrap.servers": Config.BOOTSTRAP_SERVERS, "client.id": "setup-kafka"})

transactions_topic = NewTopic(
    topic=Config.TOPIC_NAME_TRANSACTIONS,
    num_partitions=4,
    replication_factor=1,
    config={"retention.ms": 24 * 60 * 60 * 1000, "segment.ms": 24 * 60 * 60 * 1000},
)

ml_features_topic = NewTopic(
    topic=Config.TOPIC_NAME_ML_FEATURES,
    num_partitions=4,
    replication_factor=1,
    config={"retention.ms": 24 * 60 * 60 * 1000, "segment.ms": 24 * 60 * 60 * 1000},
)

created_topics = admin_client.create_topics(new_topics=[transactions_topic, ml_features_topic], validate_only=False)

for topic, future in created_topics.items():
    try:
        future.result()
        print(f"Topic '{topic}' created successfully with 1 day data retention.")
    except Exception as e:
        print(f"Failed to create topic '{topic}': {e}")

print("Setting up schemas in schema registry...")

schema_registry_client = SchemaRegistryClient({"url": Config.SCHEMA_REGISTRY_URL})

print("Processing schema for transactions")

with open(f"app/avro/transaction.avsc") as f:
    transaction_schema_str = f.read()
transaction_schema = Schema(transaction_schema_str, "AVRO")

try:
    schema_id = schema_registry_client.register_schema(Config.SCHEMA_SUBJECT_TRANSACTIONS, transaction_schema)
    print(f"Schema registered successfully with schema id: {schema_id}")
except Exception as e:
    print(f"Schema registration failed with error: {e}")

print("Processing schema for ML features")

with open(f"app/avro/ml_feature.avsc") as f:
    ml_feature_schema_str = f.read()
ml_feature_schema = Schema(ml_feature_schema_str, "AVRO")

try:
    schema_id = schema_registry_client.register_schema(Config.SCHEMA_SUBJECT_ML_FEATURES, ml_feature_schema)
    print(f"Schema registered successfully with schema id: {schema_id}")
except Exception as e:
    print(f"Schema registration failed with error: {e}")
