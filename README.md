# Flight Delay Prediction Project
## Description
This project focuses on predicting flight delays using a distributed infrastructure based on different technologies. The system is designed to process large volumes of flight data and perform real-time predictions using a Random Forest model. Below is a description of the defined services in the docker-compose.yml file along with the Docker images used

## Project Architecture

 **1. MongoDB:**   NoSQL database used for storing project data.

- Image: mongo:7.0.17

- Volume: ./data_mongo:/data/db for data persistence.

- Port: 27017

**2. Mongo Seed:** Auxiliary container that imports initial data (origin_dest_distances) into MongoDB.

- Image: mongo:7.0.17
- Depends on: mongo
- Command: Runs mongoimport after a delay to load the data.

**3. Flask App:** Web application to interact with the system.

- Image: Built from Dockerfile located at resources/web/Dockerfile.
- Port: 5010
- Depends on: mongo, mongo-seed, kafka

**4. Kafka:** Distributed messaging system for real-time data streaming.

- Image: bitnami/kafka:3.9
- Volume: kafka_data:/bitnami/kafka for persistence.
- Ports: 9092, 9094

**5. Spark Master:** Apache Spark master node for cluster management.

- Image: bde2020/spark-master:3.2.1-hadoop3.2
- Volume: ./models:/models/models (for persistent models).
- Ports: 7077, 8088

**6. Spark Worker 1 and 2:** Worker nodes for distributed Spark processing.

- Image: bde2020/spark-worker:3.2.1-hadoop3.2
- Volume: ./models:/models/models.
- Ports: 8086 (worker-1), 8087 (worker-2)

**7. Spark Submit:** Container that runs Spark applications for batch/stream processing.

- Image: bde2020/spark-submit:3.2.1-hadoop3.2
- Volumes: ./flight_prediction:/app, ./models:/models/models
- Depends on: Spark master and workers, Kafka, MongoDB

**8. Dataloader:** Service to download and prepare initial data.

- Image: python:3.8-slim
- Command: Updates packages, installs curl, runs data download script.
- Depends on: mongo

**9. NiFi:** Platform for automating and managing data flows.

- Image: apache/nifi:1.24.0
- Port: 8085 (mapped to internal 8080)
- Volume: ./nifi_output:/output
- Depends on: Kafka

**10. Hadoop Namenode:** Master node of the Hadoop Distributed File System (HDFS).

- Image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
- Volume: ./volumes/namenode:/hadoop/dfs/name
- Ports: 50070, 9870

**11. Hadoop Datanode:** Data node in the HDFS cluster.

- Image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
- Volume: ./volumes/datanode:/hadoop/dfs/data
- Ports: 50075, 9864
- Depends on: hadoop-namenode

**12. Airflow:** Workflow orchestration and pipeline management platform.

- Image: Built from Dockerfile.airflow
- Port: 8089 (mapped to internal 8080)
- Volumes: Contains DAGs, resources, Python packages, and MLflow experiments.
- Depends on: postgres

**13. Postgres:** Relational database used by Airflow.

- Image: postgres:13
- Volume: postgres_data:/var/lib/postgresql/data
- Port: 5432

**14. MLflow:** Platform for managing machine learning lifecycle.

- Image: ghcr.io/mlflow/mlflow:v2.0.1
- Port: 5000
- Volume: ./mlflow_new:/mlflow_new
- Command: MLflow server with artifacts stored in ./mlflow_new/artifacts
   
## Archivos Clave
1. docker-compose.yml

Este archivo define los contenedores para los servicios de MongoDB, Kafka, Spark, MLflow, Hadoop y otros servicios, como el FlaskApp y Dataloader. Los servicios están conectados a una red llamada hdfs y utilizan volúmenes persistentes para almacenar los datos y modelos.

2. MakePrediction.scala

Este archivo es el núcleo del proceso de predicción en Spark. Utiliza Spark Streaming para leer datos en tiempo real desde Kafka, aplica transformaciones en los datos utilizando modelos preentrenados (como StringIndexerModel y RandomForestClassificationModel), y luego guarda las predicciones en Kafka, MongoDB y HDFS. Además, imprime los resultados en consola.

val df = spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "kafka:9092")
  .option("subscribe", "flight-delay-ml-request")
  .option("failOnDataLoss", "false")
  .load()

3. Dockerfile.airflow

Este archivo personaliza la imagen de Docker para Apache Airflow, donde se instalan las dependencias necesarias, como MLflow y Kafka. Es útil para la orquestación de tareas, aunque la implementación específica de Airflow aún está pendiente.

## Pasos para Ejecutar el Proyecto
1. Clonar el repositorio y construir los contenedores
Clona este repositorio y navega hasta la carpeta raíz del proyecto. Luego, construye los contenedores con el siguiente comando:
    docker-compose up --build

2. Cargar los datos en MongoDB
Los datos de vuelos se importan automáticamente desde el contenedor mongo-seed. Asegúrate de que mongo y mongo-seed estén ejecutándose correctamente.

3. Iniciar Kafka y Spark
Los contenedores kafka y spark-master se inician automáticamente. Asegúrate de que Kafka esté transmitiendo datos en tiempo real y que Spark esté procesando estos datos.

4. Ejecutar el modelo de predicción
El modelo de predicción se ejecuta dentro del contenedor spark-submit, donde se carga el modelo entrenado y se realizan las predicciones. Las predicciones se envían a Kafka, MongoDB y HDFS.

Los resultados se pueden consultar desde MongoDB o Kafka, dependiendo del flujo de datos que prefieras.
