# Proyecto de Predicción de Retrasos de Vuelos
## Descripción

Este proyecto se enfoca en la predicción de retrasos de vuelos utilizando una infraestructura distribuida basada en tecnologías como Apache Spark, MLflow, Hadoop, Kafka, MongoDB y Docker. El sistema está diseñado para procesar grandes volúmenes de datos de vuelos y realizar predicciones en tiempo real a través de un modelo de Random Forest.

## Tecnologías Utilizadas

    Apache Spark: Framework para el procesamiento de grandes volúmenes de datos en un entorno distribuido.

    MLflow: Plataforma de gestión de modelos de machine learning, que permite el seguimiento, almacenamiento y reutilización de los modelos entrenados.

    Kafka: Sistema de mensajería distribuido utilizado para enviar y recibir datos de vuelos en tiempo real.

    MongoDB: Base de datos NoSQL que almacena datos sobre vuelos y las predicciones de retrasos.

    Hadoop: Sistema de almacenamiento distribuido para gestionar grandes volúmenes de datos.

    Docker: Plataforma para contenerizar los servicios y asegurar que el entorno de ejecución sea consistente en todos los sistemas.

## Arquitectura del Proyecto

La arquitectura del proyecto está definida en un docker-compose.yml, que define los contenedores necesarios para ejecutar los distintos servicios. A continuación se describe cada servicio:
1. MongoDB
    Imagen: mongo:7.0.17
    Propósito: Almacena los datos relacionados con los vuelos y las predicciones de retrasos.
    Volumen: Utiliza un volumen persistente ./data_mongo:/data/db.

2. Kafka
    Imagen: bitnami/kafka:3.9
    Propósito: Transmite los datos de vuelos en tiempo real.
    Puertos: 9092:9092 y 9094:9094.
    Configuración: Utiliza una configuración básica para crear y gestionar tópicos en Kafka.

3. Spark Master y Spark Workers
    Imagen: bde2020/spark-master:3.2.1-hadoop3.2
    Propósito: Realiza el procesamiento y entrenamiento del modelo de machine learning sobre los datos de vuelos.
    Puertos: 7077:7077 para el master y 8088:8080 para la interfaz web.
    Dependencias: Los workers (spark-worker-1 y spark-worker-2) se conectan al master para distribuir el procesamiento.

4. FlaskApp
    Imagen: Personalizada desde el Dockerfile en resources/web/Dockerfile.
    Propósito: Proporciona una interfaz para interactuar con el sistema de predicción de retrasos de vuelos.
    Puertos: 5010:5010.

5. Dataloader
    Imagen: python:3.8-slim
    Propósito: Carga y prepara los datos necesarios para el entrenamiento y la predicción.
    Comando: Ejecuta un script que descarga y prepara los datos.

6. Hadoop (HDFS)
    Imágenes: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8 y bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    Propósito: Almacena grandes volúmenes de datos procesados en HDFS (Hadoop Distributed File System).

7. MLflow
    Imagen: ghcr.io/mlflow/mlflow:v2.0.1
    Propósito: Gestiona los modelos de machine learning entrenados y permite su seguimiento y almacenamiento.
    Puertos: 5000:5000.
   
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

FROM apache/airflow:2.0.2

USER root

RUN pip install mlflow kafka-python pymongo

USER airflow

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
