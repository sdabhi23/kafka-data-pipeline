FROM docker.redpanda.com/redpandadata/connectors:v1.0.21

USER root

ENV CONFLUENT_PLUGIN_BASE_URL=https://d1i4a15mxbxib1.cloudfront.net/api/plugins

ENV PLUGINS_BASE=/opt/kafka/redpanda-plugins

WORKDIR /tmp/plugin_installs

# install s3 plugin for kafka connect
RUN curl -O "${CONFLUENT_PLUGIN_BASE_URL}/confluentinc/kafka-connect-s3/versions/10.5.9/confluentinc-kafka-connect-s3-10.5.9.zip" && \
    unzip confluentinc-kafka-connect-s3-10.5.9.zip && \
    mkdir -p ${PLUGINS_BASE}/kafka-connect-s3 && \
    cp /tmp/plugin_installs/confluentinc-kafka-connect-s3-10.5.9/lib/* ${PLUGINS_BASE}/kafka-connect-s3/

RUN curl -O "${CONFLUENT_PLUGIN_BASE_URL}/confluentinc/kafka-connect-avro-converter/versions/7.6.0/confluentinc-kafka-connect-avro-converter-7.6.0.zip" && \
    unzip confluentinc-kafka-connect-avro-converter-7.6.0.zip && \
    mkdir -p ${PLUGINS_BASE}/kafka-connect-avro-connector && \
    cp /tmp/plugin_installs/confluentinc-kafka-connect-avro-converter-7.6.0/lib/* ${PLUGINS_BASE}/kafka-connect-avro-connector/

RUN curl -O "${CONFLUENT_PLUGIN_BASE_URL}/redis/redis-kafka-connect/versions/0.9.0/redis-redis-kafka-connect-0.9.0.zip" && \
    unzip redis-redis-kafka-connect-0.9.0.zip && \
    mkdir -p ${PLUGINS_BASE}/redis-kafka-connect && \
    cp /tmp/plugin_installs/redis-redis-kafka-connect-0.9.0/lib/* ${PLUGINS_BASE}/redis-kafka-connect/

RUN curl -O "${CONFLUENT_PLUGIN_BASE_URL}/jcustenborder/kafka-connect-redis/versions/0.0.5/jcustenborder-kafka-connect-redis-0.0.5.zip" && \
    unzip jcustenborder-kafka-connect-redis-0.0.5.zip && \
    mkdir -p ${PLUGINS_BASE}/kafka-connect-redis && \
    cp /tmp/plugin_installs/jcustenborder-kafka-connect-redis-0.0.5/lib/* ${PLUGINS_BASE}/kafka-connect-redis/

RUN rm -rf /tmp/plugin_installs

USER 1001