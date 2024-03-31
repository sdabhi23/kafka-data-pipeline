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

create_live_kafka_table = f"""
    create table ml_features_live (
        user_id STRING NOT NULL,
        total_transactions_count STRING NOT NULL,
        PRIMARY KEY (user_id) NOT ENFORCED
    ) with (
        'connector' = 'upsert-kafka',
        'topic' = '{Config.TOPIC_NAME_ML_FEATURES_LIVE}',
        'properties.bootstrap.servers' = '{Config.BOOTSTRAP_SERVERS_DOCKER}',
        'properties.group.id' = 'transactions-ml-features-job-user',
        'key.format' = 'csv',
        'key.fields-prefix' = 'user_',
        'value.format' = 'csv',
        'value.fields-include'='EXCEPT_KEY'
    );
"""
# 'value.avro-confluent.url' = '{Config.SCHEMA_REGISTRY_URL_DOCKER}',
#         'value.avro-confluent.subject' = '{Config.SCHEMA_SUBJECT_ML_FEATURES_LIVE}',

tenv.execute_sql(create_live_kafka_table)

agg_query_live = """
    INSERT INTO ml_features_live
    SELECT
        CAST(user_id AS STRING),
        CAST(CAST(COUNT(user_id) AS INT) AS STRING)
    FROM kafka_transactions
    GROUP BY user_id
    HAVING CAST(CAST(COUNT(user_id) AS INT) AS STRING) IS NOT NULL;
"""

res_live = tenv.execute_sql(agg_query_live)

res_live.wait()