FROM apache/spark-py:v3.4.0

USER 0

RUN chmod -R 777 /opt/spark

WORKDIR /opt/spark/jars

RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-hadoop-cloud_2.12/3.3.4/spark-hadoop-cloud_2.12-3.3.4.jar
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar
RUN wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.691/aws-java-sdk-bundle-1.12.691.jar

WORKDIR /opt/spark/work-dir

USER 185

COPY run.sh /opt/start-spark/

CMD /opt/start-spark/run.sh