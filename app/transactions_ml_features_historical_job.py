from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

from commons import Config


env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)

tenv = StreamTableEnvironment.create(env)

create_kafka_table = f"""
    create table kafka_transactions (
        user_id INT,
        transaction_timestamp_millis BIGINT,
        amount DOUBLE,
        currency STRING,
        counterpart_id INT,
        transaction_ts AS TO_TIMESTAMP_LTZ(transaction_timestamp_millis, 3),
        ingestion_ts TIMESTAMP(0) METADATA FROM 'timestamp',
        WATERMARK FOR transaction_ts AS transaction_ts
    ) with (
        'connector' = 'kafka',
        'topic' = '{Config.TOPIC_NAME_TRANSACTIONS}',
        'properties.bootstrap.servers' = '{Config.BOOTSTRAP_SERVERS_DOCKER}',
        'properties.group.id' = 'transactions-ml-features-job-user',
        'properties.auto.offset.reset' = 'earliest',
        'scan.startup.mode' = 'group-offsets',
        'value.format' = 'avro-confluent',
        'value.avro-confluent.url' = '{Config.SCHEMA_REGISTRY_URL_DOCKER}',
        'value.avro-confluent.subject' = '{Config.SCHEMA_SUBJECT_TRANSACTIONS}',
        'value.avro-confluent.properties.auto.register.schemas' = 'false'
    );
"""

tenv.execute_sql(create_kafka_table)

create_historical_kafka_table = f"""
    create table ml_features_historical (
        user_id INT NOT NULL,
        transaction_timestamp_millis BIGINT NOT NULL,
        total_transactions_count INT NOT NULL
    ) with (
        'connector' = 'kafka',
        'topic' = '{Config.TOPIC_NAME_ML_FEATURES_HISTORICAL}',
        'properties.bootstrap.servers' = '{Config.BOOTSTRAP_SERVERS_DOCKER}',
        'properties.group.id' = 'transactions-ml-features-job-user',
        'key.format' = 'csv',
        'key.fields' = 'user_id',
        'value.format' = 'avro-confluent',
        'value.avro-confluent.url' = '{Config.SCHEMA_REGISTRY_URL_DOCKER}',
        'value.avro-confluent.subject' = '{Config.SCHEMA_SUBJECT_ML_FEATURES_HISTORICAL}'
    );
"""

tenv.execute_sql(create_historical_kafka_table)

agg_query_historical = """
    INSERT INTO ml_features_historical
    SELECT
        user_id,
        transaction_timestamp_millis,
        CAST(
            COUNT(user_id) OVER (
                PARTITION BY user_id
                ORDER BY transaction_ts
                RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )
            AS INT
        )
    FROM kafka_transactions;
"""

res_historical = tenv.execute_sql(agg_query_historical)

res_historical.wait()
