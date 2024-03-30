import argparse
import logging
import sys

from pyflink.common import SimpleStringSchema, Encoder, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.connectors.file_system import FileSink, RollingPolicy
from pyflink.table import StreamTableEnvironment


word_count_data = [
    "To be, or not to be,--that is the question:--",
    "Whether 'tis nobler in the mind to suffer",
    "The slings and arrows of outrageous fortune",
    "Or to take arms against a sea of troubles,",
    "And by opposing end them?--To die,--to sleep,--",
    "No more; and by a sleep to say we end",
    "The heartache, and the thousand natural shocks",
    "That flesh is heir to,--'tis a consummation",
    "Devoutly to be wish'd. To die,--to sleep;--",
    "To sleep! perchance to dream:--ay, there's the rub;",
    "For in that sleep of death what dreams may come,",
    "When we have shuffled off this mortal coil,",
    "Must give us pause: there's the respect",
    "That makes calamity of so long life;",
    "For who would bear the whips and scorns of time,",
    "The oppressor's wrong, the proud man's contumely,",
    "The pangs of despis'd love, the law's delay,",
    "The insolence of office, and the spurns",
    "That patient merit of the unworthy takes,",
    "When he himself might his quietus make",
    "With a bare bodkin? who would these fardels bear,",
    "To grunt and sweat under a weary life,",
    "But that the dread of something after death,--",
    "The undiscover'd country, from whose bourn",
    "No traveller returns,--puzzles the will,",
    "And makes us rather bear those ills we have",
    "Than fly to others that we know not of?",
    "Thus conscience does make cowards of us all;",
    "And thus the native hue of resolution",
    "Is sicklied o'er with the pale cast of thought;",
    "And enterprises of great pith and moment,",
    "With this regard, their currents turn awry,",
    "And lose the name of action.--Soft you now!",
    "The fair Ophelia!--Nymph, in thy orisons",
    "Be all my sins remember'd.",
]


def kafka_read():
    env = StreamExecutionEnvironment.get_execution_environment()
    tenv = StreamTableEnvironment.create(env)

    create_kafka_table = """
        create table raw_transactions (
            `kafka_key` STRING,
            `user_id` INT,
            `transaction_timestamp_millis` BIGINT,
            `amount` FLOAT,
            `currency` STRING,
            `counterpart_id` INT,
            `ts` TIMESTAMP(3) METADATA FROM 'timestamp'
        ) with (
            'connector' = 'kafka',
            'topic' = 'transactions',
            'properties.bootstrap.servers' = 'redpanda-0:9092',
            'properties.group.id' = 'flink-kafka-test-consumer',
            'scan.startup.mode' = 'earliest-offset',
            'key.format' = 'raw',
            'key.fields' = 'kafka_key',
            'value.format' = 'avro-confluent',
            'value.avro-confluent.url' = 'http://redpanda-0:8082',
            'value.avro-confluent.subject' = 'transactions'
        );
    """

    tenv.execute_sql(create_kafka_table)

    tenv.execute_sql("select * from raw_transactions").print()

    # kafka_source = (
    #     KafkaSource.builder()
    #     .set_bootstrap_servers("redpanda-0:9092")
    #     .set_topics("test")
    #     .set_group_id("flink-test")
    #     .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    #     .set_value_only_deserializer(SimpleStringSchema())
    #     .build()
    # )

    # ds = env.from_source(kafka_source, WatermarkStrategy.no_watermarks(), "Test Kafka Source")

    # sink = (
    #     FileSink.for_row_format("s3://backup/kafka-test-0", Encoder.simple_string_encoder("UTF-8"))
    #     .with_rolling_policy(
    #         RollingPolicy.default_rolling_policy(
    #             part_size=1024, rollover_interval=1 * 60 * 1000, inactivity_interval=20 * 1000
    #         )
    #     )
    #     .build()
    # )


    # ds.sink_to(sink)

    # tenv.execute("kafkaread")


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--output", dest="output", required=False, help="Output file to write results to.")

    # argv = sys.argv[1:]
    # known_args, _ = parser.parse_known_args(argv)

    # word_count(known_args.output)
    kafka_read()
