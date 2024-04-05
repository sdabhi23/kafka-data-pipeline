# Kafka Data Pipeline

This streaming data pipeline uses Kafka as the backbone and Flink for data processing and transformations. Kafka Connect is used for writing the streams to S3 compatible blob stores and Redis (low latency KV store for realtime ML inference). Spark is used for the batch job to backfill the ml feature data.

This setup has been created and tested using Python 3.10 on Ubuntu 22.04 (running in WSL on a windows machine).

## Definition

A Kafka cluster is available to you, maintained by the cloud infrastructure team. All user transactions are being sent by our backend in real time in the `transactions` Kafka topic. The schema of the records being sent to this Kafka topic is as below:

```jsonc
{
    "user_id": int, // The id of the user making the transaction
    "transaction_timestamp_millis": long // The timestamp, in milliseconds since epoch, of the transaction,
    "amount": float // The amount of the transaction. Negative is a debit, positive is a credit.,
    "currency": string // a 3 letters symbol indicating the currency of the transaction
    "counterpart_id": int // The id of the counterpart of this transaction
}
```

1. Create the transactions topic in your local Kafka cluster, with a 1 day retention period. Choose and justify your partitioning strategy. Make use of a schema registry to handle schema validation and evolution. Create 2 users that will be used later by consumers:
    1. `transactions-backup-job-user`
    2. `transactions-ml-features-job-user`
  
2. Create a service called `transactions-producer` pushing fake data in your Kafka topic. Minimal working code is expected here, no need for unit tests or clean code. The purpose of this service is only to generate fake data to your Kafka topic in order to showcase the behavior of the consumers you will build later.

3. Create a consumer named `transactions-job-backup` of the transactions topic that will persist all records flowing through the topic to scalable file based storage. The output schema should be the same as input schema. The chosen format should enable scalable SQL queries via SparkSQL.

4. Create a consumer named transactions-ml-features-job of the transactions topic that will:
    1. compute the total number of transactions per user. The schema of generated events will be as follow:
       ```jsonc
       {
            "user_id": int, # The id of the user making the transaction
            "total_transactions_count": int # The total count of transactions for this user
       }
       ```
   2. output the results of the computation to file based storage. The chosen format should enable scalable SQL queries via SparkSQL. NB: these data will be used by:
       1. analytics team to build scheduled reports
       2. data science team to train their ML models with historical data
   3. output the results of the computation to a low latency key-value store of your choice. This will be used by the ML model in real time to make predictions on incoming data.

5. Discuss how would you backfill your transactions-ml-features to use all historical available. Eventually, modify the code of your transaction-ml-features service to support this use case. When running an historical backfill, data should be sinked only to the file based storage, not to the low latency key-value store. 


## Choices & Caveats

* Right now, the backfill job is a Spark batch job which is not idempotent. This could have been a streaming job, where in a service reads events from transactions backups and emits them to the `ml-features-historical` topic in Kafka.
* There are 2 ways to make the backfill idempotent, read the existing data in Spark and perform a dedupe **OR** use a Flink streaming job to make sure duplicates are not written to S3.
* ML features Avro schema have a workaround for schema compatibility when writing to Kafka from Flink. [^1] [^2]
* I have changed the data schema for the historical data being recorded for the ML Feature. As per my judgement the computation outputs a fact (number of transactions performed by a user). Being able to associate it with some dimension (like transaction time, transaction id, etc) is very important to be able to use it for any ML usecase. The ingestion maybe delayed due to any number of reasons, so the ingestion time cannot be relied upon for this.
* I have used a separate queue and schema for writing computed ML Features to Redis because the Redis Kafka connector does not support Avro deserialization and field extraction. So the other 2 alternatives were to either build a custom connector or to write raw bytes to Redis and let the downstream application take care of deserialization. ML inference pipelines are already quite heavy and complex at times, so I felt it is simpler to have the data directly available as a string in Redis.
* The entire codebase is in Python because all the tools used offer robust and feature complete Python APIs. While there is some performance overhead when using Python over Scala / Java, the ease of use was the final deciding factor. [^3]

[^1]: Flink SQL automatically uploads Avro schema (StackOverflow) [link](https://stackoverflow.com/questions/76524654/flink-sql-automatically-uploads-avro-schema)
[^2]: Avro types to Flink SQL types for Avro Schema Registry (Confluent Docs) [link](https://docs.confluent.io/cloud/current/flink/reference/serialization.html#avro-types-to-flink-sql-types)
[^3]: Flink's Scala APIs are deprecated and awill be removed in the next major version [FLIP-265](https://cwiki.apache.org/confluence/display/FLINK/FLIP-265+Deprecate+and+remove+Scala+API+support)

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
> | Service    | URL                      | Remarks                                                                                 |
> |------------|--------------------------|-----------------------------------------------------------------------------------------|
> | Kafka      | <http://localhost:8080/> | The connector section will keep on breaking till you bring up the Kafka Connect cluster |
> | Redis      | <http://localhost:8001/> | N/A                                                                                     |
> | Flink      | <http://localhost:8081/> | N/A                                                                                     |
> | Minio (S3) | <http://localhost:9001/> | Use `minioadmin` as both username & password                                            |
>

:drum: Now time to start our producer and see if the data flows properly!

```bash
pipenv run producer
```

Now, for the backfill job, use the following command for bringing up a tiny Spark cluster and running the backfill job on it.

```bash
pipenv run ml-features-backfill
```

For stopping all the services gracefully and cleaning up the volumes and networks run the following command

```bash
pipenv run shutdown-all-services
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
```
