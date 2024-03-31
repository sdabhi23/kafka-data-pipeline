FROM flink:1.17.2

# install python3 and pip3
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

# install PyFlink
RUN pip3 install apache-flink==1.17.2  confluent-kafka==2.3.0

WORKDIR /opt/flink/lib

# core dependencies for avro, parquet & kafka
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-avro-confluent-registry/1.17.2/flink-avro-confluent-registry-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-parquet/1.17.2/flink-parquet-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-avro/1.17.2/flink-avro-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/avro/avro/1.11.3/avro-1.11.3.jar

# jackson dependencies required for deserialising Avro records with confluent registry
RUN wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.13.4/jackson-core-2.13.4.jar
RUN wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.13.4/jackson-databind-2.13.4.jar
RUN wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-annotations/2.13.4/jackson-annotations-2.13.4.jar

# confluent registry dependencies
RUN wget https://packages.confluent.io/maven/io/confluent/kafka-schema-registry-client/7.2.2/kafka-schema-registry-client-7.2.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.2.2/kafka-clients-3.2.2.jar
RUN wget https://repo1.maven.org/maven2/com/google/guava/guava/30.1.1-jre/guava-30.1.1-jre.jar

# hadoop dependencies required for writing to s3
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar
RUN wget https://repo1.maven.org/maven2/org/codehaus/woodstox/stax2-api/4.2.2/stax2-api-4.2.2.jar
RUN wget https://repo1.maven.org/maven2/com/fasterxml/woodstox/woodstox-core/6.5.1/woodstox-core-6.5.1.jar
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/thirdparty/hadoop-shaded-guava/1.2.0/hadoop-shaded-guava-1.2.0.jar
RUN wget https://repo1.maven.org/maven2/org/apache/parquet/parquet-hadoop/1.13.1/parquet-hadoop-1.13.1.jar
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-mapreduce-client-core/3.3.4/hadoop-mapreduce-client-core-3.3.4.jar
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-mapreduce-client-jobclient/3.3.4/hadoop-mapreduce-client-jobclient-3.3.4.jar

# parquet related dependencies
RUN wget https://repo1.maven.org/maven2/org/apache/parquet/parquet-column/1.13.1/parquet-column-1.13.1.jar
RUN wget https://repo1.maven.org/maven2/org/apache/parquet/parquet-format-structures/1.13.1/parquet-format-structures-1.13.1.jar
RUN wget https://repo1.maven.org/maven2/org/apache/parquet/parquet-common/1.13.1/parquet-common-1.13.1.jar
RUN wget https://repo1.maven.org/maven2/org/apache/parquet/parquet-encoding/1.13.1/parquet-encoding-1.13.1.jar
