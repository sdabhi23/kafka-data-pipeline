FROM flink:1.17.2

# install python3 and pip3
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

# install PyFlink
RUN pip3 install apache-flink==1.17.2

WORKDIR /opt/flink/lib

# install kafka connector, avro, parquet, confluent registry connector
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-avro-confluent-registry/1.17.2/flink-avro-confluent-registry-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-parquet/1.17.2/flink-parquet-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-avro/1.17.2/flink-avro-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-csv/1.17.2/flink-csv-1.17.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/avro/avro/1.11.3/avro-1.11.3.jar

RUN wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.13.4/jackson-core-2.13.4.jar
RUN wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.13.4/jackson-databind-2.13.4.jar
RUN wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-annotations/2.13.4/jackson-annotations-2.13.4.jar

RUN wget https://packages.confluent.io/maven/io/confluent/kafka-schema-registry-client/7.2.2/kafka-schema-registry-client-7.2.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.2.2/kafka-clients-3.2.2.jar
RUN wget https://repo1.maven.org/maven2/com/google/guava/guava/30.1.1-jre/guava-30.1.1-jre.jar