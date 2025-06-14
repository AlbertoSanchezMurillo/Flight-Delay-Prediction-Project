# Flight Delay Prediction Project
## Description
This project focuses on predicting flight delays using a distributed infrastructure based on different technologies. The system is designed to process large volumes of flight data and perform real-time predictions using a Random Forest model. Below is a description of the defined services in the docker-compose.yml file along with the Docker images used

## Project Architecture

 **MongoDB:**   NoSQL database used for storing project data.

- Image: mongo:7.0.17

- Volume: ./data_mongo:/data/db for data persistence.

- Port: 27017

**Mongo Seed:** Auxiliary container that imports initial data (origin_dest_distances) into MongoDB.

- Image: mongo:7.0.17
- Depends on: mongo
- Command: Runs mongoimport after a delay to load the data.

**Flask App:** Web application to interact with the system.

- Image: Built from Dockerfile located at resources/web/Dockerfile.
- Port: 5010
- Depends on: mongo, mongo-seed, kafka

**Kafka:** Distributed messaging system for real-time data streaming.

- Image: bitnami/kafka:3.9
- Volume: kafka_data:/bitnami/kafka for persistence.
- Ports: 9092, 9094

**Spark Master:** Apache Spark master node for cluster management.

- Image: bde2020/spark-master:3.2.1-hadoop3.2
- Volume: ./models:/models/models (for persistent models).
- Ports: 7077, 8088

**Spark Worker 1 and 2:** Worker nodes for distributed Spark processing.

- Image: bde2020/spark-worker:3.2.1-hadoop3.2
- Volume: ./models:/models/models.
- Ports: 8086 (worker-1), 8087 (worker-2)

**Spark Submit:** Container that runs Spark applications for batch/stream processing.

- Image: bde2020/spark-submit:3.2.1-hadoop3.2
- Volumes: ./flight_prediction:/app, ./models:/models/models
- Depends on: Spark master and workers, Kafka, MongoDB

**Dataloader:** Service to download and prepare initial data.

- Image: python:3.8-slim
- Command: Updates packages, installs curl, runs data download script.
- Depends on: mongo

**NiFi:** Platform for automating and managing data flows.

- Image: apache/nifi:1.24.0
- Port: 8085 (mapped to internal 8080)
- Volume: ./nifi_output:/output
- Depends on: Kafka

**Hadoop Namenode:** Master node of the Hadoop Distributed File System (HDFS).

- Image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
- Volume: ./volumes/namenode:/hadoop/dfs/name
- Ports: 50070, 9870

**Hadoop Datanode:** Data node in the HDFS cluster.

- Image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
- Volume: ./volumes/datanode:/hadoop/dfs/data
- Ports: 50075, 9864
- Depends on: hadoop-namenode

**Airflow:** Workflow orchestration and pipeline management platform.

- Image: Built from Dockerfile.airflow
- Port: 8089 (mapped to internal 8080)
- Volumes: Contains DAGs, resources, Python packages, and MLflow experiments.
- Depends on: postgres

**Postgres:** Relational database used by Airflow.

- Image: postgres:13
- Volume: postgres_data:/var/lib/postgresql/data
- Port: 5432

**MLflow:** Platform for managing machine learning lifecycle.

- Image: ghcr.io/mlflow/mlflow:v2.0.1
- Port: 5000
- Volume: ./mlflow_new:/mlflow_new


## How to Run the Flight Delay Prediction Project

### 1. Build and Start Containers

Once you clone the repository, you can create and start the containers using Docker Compose.

Run this command in your terminal:

```bash
docker compose up --build
```

