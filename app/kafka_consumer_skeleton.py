from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.table import StreamTableEnvironment
from pyflink.datastream.connectors.file_system import RollingPolicy, FileSink, BucketAssigner
from pyflink.table.types import DataTypes
from pyflink.datastream.formats.parquet import ParquetBulkWriters, Configuration

from commons import Config


def kafka_read():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)
    env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)

    tenv = StreamTableEnvironment.create(env)

    create_kafka_table = f"""
        create table kafka_transactions (
            user_id INT,
            transaction_timestamp_millis BIGINT,
            amount DOUBLE,
            currency STRING,
            counterpart_id INT,
            ingestion_ts TIMESTAMP(0) METADATA FROM 'timestamp'
        ) with (
            'connector' = 'kafka',
            'topic' = '{Config.TOPIC_NAME_TRANSACTIONS}',
            'properties.bootstrap.servers' = 'redpanda-0:9092',
            'properties.group.id' = 'flink-kafka-test-consumer',
            'scan.startup.mode' = 'earliest-offset',
            'value.format' = 'avro-confluent',
            'value.avro-confluent.url' = 'http://redpanda-0:18081',
            'value.avro-confluent.subject' = '{Config.TOPIC_NAME_TRANSACTIONS}'
        );
    """

    tenv.execute_sql(create_kafka_table)

    # create_s3_table = """
    #     create table s3_backup_transactions (
    #         user_id INT,
    #         transaction_timestamp_millis BIGINT,
    #         amount DOUBLE,
    #         currency STRING,
    #         counterpart_id INT,
    #         ingestion_ts TIMESTAMP(0),
    #         ingestion_date STRING,
    #         ingestion_hour STRING,
    #         ingestion_minute STRING
    #     ) PARTITIONED BY (ingestion_date, ingestion_hour, ingestion_minute) with (
    #         'connector' = 'filesystem',
    #         'path' = 's3://backup/',
    #         'format' = 'parquet',
    #         'sink.partition-commit.delay' = '1 m',
    #         'sink.partition-commit.policy.kind' = 'success-file'
    #     );
    # """

    # tenv.execute_sql(create_s3_table)

    # ingest_into_s3 = """
    #     INSERT INTO s3_backup_transactions
    #     SELECT
    #         user_id,
    #         transaction_timestamp_millis,
    #         amount,
    #         currency,
    #         counterpart_id,
    #         ingestion_ts,
    #         DATE_FORMAT(ingestion_ts, 'yyyy-MM-dd'),
    #         DATE_FORMAT(ingestion_ts, 'HH'),
    #         DATE_FORMAT(ingestion_ts, 'mm')
    #     FROM kafka_transactions;
    # """

    # tenv.execute_sql(ingest_into_s3)

    # tenv.execute_sql("select count(*) from s3_backup_transactions;").print()

    kafka_table = tenv.sql_query("select * from kafka_transactions;")

    kafka_data_stream = tenv.to_data_stream(kafka_table)

    # kafka_table.execute().print()

    row_type = DataTypes.ROW(
        [
            DataTypes.FIELD("user_id", DataTypes.INT()),
            DataTypes.FIELD("transaction_timestamp_millis", DataTypes.BIGINT()),
            DataTypes.FIELD("amount", DataTypes.DOUBLE()),
            DataTypes.FIELD("currency", DataTypes.STRING()),
            DataTypes.FIELD("counterpart_id", DataTypes.INT()),
            DataTypes.FIELD("ingestion_ts", DataTypes.TIMESTAMP(precision=0)),
        ]
    )

    sink = (
        FileSink.for_bulk_format(
            "/tmp/backup/kafka-test-0",
            ParquetBulkWriters.for_row_type(row_type, hadoop_config=Configuration(), utc_timestamp=True),
        )
        .with_bucket_assigner(BucketAssigner.base_path_bucket_assigner())
        .with_rolling_policy(RollingPolicy.on_checkpoint_rolling_policy())
        .build()
    )

    # ds.map(lambda e: e, output_type=avro_type_info)

    kafka_data_stream.sink_to(sink)

    print(env.get_execution_plan())

    env.execute("kafka read and process")

if __name__ == "__main__":
    kafka_read()
