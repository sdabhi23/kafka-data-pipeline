/opt/spark/sbin/start-master.sh
/opt/spark/sbin/start-worker.sh spark://localhost:7077

while true
do
    echo "${C}###### [$(date "+%D %T %Z")] #####${NC}"
    /opt/spark/sbin/spark-daemon.sh status org.apache.spark.deploy.master.Master 1
    sleep 1
    /opt/spark/sbin/spark-daemon.sh status org.apache.spark.deploy.worker.Worker 1
    sleep 10
done