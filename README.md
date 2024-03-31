# Kafka Data Pipeline

```SQL
INSTALL httpfs
LOAD httpfs
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

ML features Avro schema have a workaround for schema compatibility when writing to Kafka from Flink. [[StackOverflow Question](https://docs.confluent.io/cloud/current/flink/reference/serialization.html#avro-types-to-flink-sql-types)] [[Confluent Docs](https://stackoverflow.com/questions/76524654/flink-sql-automatically-uploads-avro-schema)]
