docker compose -f docker-compose.spark.yml down --volumes
docker compose -f docker-compose.flink.yml down --volumes
docker compose -f docker-compose.kafka-connect.yml down --volumes
docker compose -f docker-compose.yml down --volumes