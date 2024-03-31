FROM docker.redpanda.com/redpandadata/connectors:v1.0.21

USER root

ENV CONFLUENT_PLUGIN_BASE_URL=https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc

ENV PLUGINS_BASE=/opt/kafka/redpanda-plugins

WORKDIR /tmp/plugin_installs

# install s3 plugin for kafka connect
RUN curl -O "${CONFLUENT_PLUGIN_BASE_URL}/kafka-connect-s3/versions/10.5.9/confluentinc-kafka-connect-s3-10.5.9.zip" && \
    unzip confluentinc-kafka-connect-s3-10.5.9.zip && \
    mkdir -p ${PLUGINS_BASE}/kafka-connect-s3 && \
    cp /tmp/plugin_installs/confluentinc-kafka-connect-s3-10.5.9/lib/* ${PLUGINS_BASE}/kafka-connect-s3/

RUN curl -O "${CONFLUENT_PLUGIN_BASE_URL}/kafka-connect-avro-converter/versions/7.6.0/confluentinc-kafka-connect-avro-converter-7.6.0.zip" && \
    unzip confluentinc-kafka-connect-avro-converter-7.6.0.zip && \
    mkdir -p ${PLUGINS_BASE}/kafka-connect-avro-connector && \
    cp /tmp/plugin_installs/confluentinc-kafka-connect-avro-converter-7.6.0/lib/* ${PLUGINS_BASE}/kafka-connect-avro-connector/

RUN rm -rf /tmp/plugin_installs

# RUN wget "${CONFLUENT_PLUGIN_BASE_URL}/kafka-connect-avro-converter/versions/7.6.0/confluentinc-kafka-connect-avro-converter-7.6.0.zip" && \
#     unzip confluentinc-kafka-connect-avro-converter-7.6.0.zip && \
#     mkdir -p ${CONFLUENT_PLUGIN_BASE_URL}/kafka-connect-avro-connector && \
#     cp ./confluentinc-kafka-connect-avro-converter-7.6.0/lib ${CONFLUENT_PLUGIN_BASE_URL}/kafka-connect-avro-connector && \
#     rm -rf confluentinc-kafka-connect-avro-converter-7.6.0/ && \
#     rm -rf confluentinc-kafka-connect-avro-converter-7.6.0.zip


USER 1001