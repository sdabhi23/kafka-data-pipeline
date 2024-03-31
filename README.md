# Kafka Data Pipeline

This streaming data pipeline uses Kafka as the backbone and Flink for data processing and transformations. Kafka Connect is used for writing the streams to S3 compatiable blob stores and Redis (low latency KV store for realtime ML inference).

This setup has been created and tested using Python 3.10 on Ubuntu 22.04 (running in WSL on a windows machine).

## Steps for setup

First and foremost, setup Pipenv! There are a bunch of shortcuts defined using pipenv!

```bash
pip install pipenv
pipenv install
```

Now let's build our docker images!

```bash
pipenv run build-docker
```

Bring up the core services (Redpanda Kafka, Minio for S3 and Redis)

```bash
pipenv run start-services
```

Configure Kafka correctly

```bash
pipenv run configure-kafka
```

Bring up the Flink cluster and start the FLink jobs for ML Feature processing

```bash
pipenv run start-flink
```

Bring up the Kafka connect cluster

```bash
pipenv run start-kafka-connect
```

> [!TIP]
> Web consoles are available for all the services we have setup. You can use them to view task progess / data for any service / job.
>
> | Service    | URL                    | Remarks                                                                                 |
> |------------|------------------------|-----------------------------------------------------------------------------------------|
> | Kafka      | http://localhost:8080/ | The connector section will keep on breaking till you bring up the Kafka Connect cluster |
> | Redis      | http://localhost:8001/ | N/A                                                                                     |
> | Flink      | http://localhost:8081/ | N/A                                                                                     |
> | Minio (S3) | http://localhost:9001/ | Use `minioadmin` as both username & password                                            |
>

:drum: Now time to start our producer and see if the data flows properly!

```bash
pipenv run producer
```

## Test the data stored on S3

Download the DuckDB binary from <https://duckdb.org/docs/installation/> (pick `Command line` environment) and run the cli. You can then feed the following SQL statements to query the data stored as parquet files in S3.

```SQL
INSTALL httpfs;
LOAD httpfs;
SET s3_region='us-east-1';
SET s3_url_style='path';
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin' ;
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;

CREATE TABLE transactions AS SELECT * FROM read_parquet('s3://backup/topics/transactions/*/*/*/*.parquet');

-- check for duplicates
SELECT
    user_id, transaction_timestamp_millis, count(*) as txn_count
FROM transactions
GROUP BY user_id, transaction_timestamp_millis
HAVING count(*) > 1;

-- rolling count by timestamp
```

## Notes

* ML features Avro schema have a workaround for schema compatibility when writing to Kafka from Flink. [[StackOverflow Question](https://docs.confluent.io/cloud/current/flink/reference/serialization.html#avro-types-to-flink-sql-types)] [[Confluent Docs](https://stackoverflow.com/questions/76524654/flink-sql-automatically-uploads-avro-schema)]
