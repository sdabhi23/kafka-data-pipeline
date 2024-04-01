from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import input_file_name

spark = (
    SparkSession.builder.config(
        "spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    )
    .appName("MLFeaturesBackfill")
    .getOrCreate()
)

sc = spark.sparkContext


sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "minioadmin")
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "minioadmin")
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "http://minio-0:9000")
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
sc._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

df: DataFrame = spark.read.parquet("s3a://backup/topics/transactions/*/*/*/*.parquet").withColumn(
    "input_file_name", input_file_name()
)

df.createOrReplaceTempView("transactions")

df.show(5, vertical=True, truncate=False)

print(df.count())

backfill_df: DataFrame = spark.sql(
    """
    SELECT
        user_id,
        transaction_timestamp_millis,
        COUNT(user_id) OVER (
            PARTITION BY user_id
            ORDER BY transaction_timestamp_millis
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as total_transactions_count,
        REPLACE(
            ARRAY_JOIN(
                ARRAY_APPEND(
                    ARRAY_EXCEPT(
                        SPLIT(input_file_name, '/'),
                        SLICE(SPLIT(input_file_name, '/'), -1, 1)
                    ), 'backfill.parquet'
                ), '/'
            ), 'transactions', 'ml-features-historical'
        ) as output_file_name
    FROM transactions
"""
)

backfill_df.show(5, vertical=True, truncate=False)

print(backfill_df.count())

backfill_df.printSchema()

output_file_names = [row.output_file_name for row in backfill_df.select("output_file_name").distinct().collect()]

for filename in output_file_names:
    backfill_df.select("user_id", "transaction_timestamp_millis", "total_transactions_count").filter(
        backfill_df["output_file_name"] == filename
    ).write.parquet(filename, mode="overwrite", compression="snappy")
