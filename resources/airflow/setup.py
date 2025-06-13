from airflow import DAG
from airflow.operators.python import PythonOperator  # operador actualizado
from datetime import datetime, timedelta
import subprocess
import os

def train_with_spark_and_mlflow():
    # Ruta al script y datos montados en el contenedor
    base_path = "/opt/airflow"  # raíz montada de recursos
    script_path = os.path.join(base_path, "resources", "train_spark_mllib_model.py")
    data_path = os.path.join(base_path, "data", "simple_flight_delay_features.jsonl.bz2")

    # Ejecutar script con ambos argumentos
    result = subprocess.run(["python", script_path, data_path], capture_output=True, text=True)

    # Log de salida y errores
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 6, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'mlflow_rf_from_json_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
)

run_rf_training = PythonOperator(
    task_id='train_with_mlflow_and_spark',
    python_callable=train_with_spark_and_mlflow,
    dag=dag,
)
