from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType

# Crear sesión de Spark
spark = SparkSession.builder \
    .appName("FlightDelayPredictionDebug") \
    .config("spark.mongodb.output.uri", "mongodb://mongo:27017/agile_data_science.flight_delay_ml_response") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Esquema del JSON (con todos los campos como opcionales)
schema = StructType([
    StructField("Origin", StringType(), True),
    StructField("Dest", StringType(), True),
    StructField("FlightNum", StringType(), True),
    StructField("Distance", FloatType(), True),
    StructField("DepDelay", FloatType(), True),
    StructField("Carrier", StringType(), True),
    StructField("FlightDate", StringType(), True),
    StructField("DayOfYear", IntegerType(), True),
    StructField("DayOfMonth", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True),
    StructField("Timestamp", StringType(), True),
    StructField("UUID", StringType(), True),
])

# Lectura desde Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "flight-delay-ml-request") \
    .option("startingOffsets", "latest") \
    .load()

# Parseo del JSON
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Mostrar en consola para debug
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
