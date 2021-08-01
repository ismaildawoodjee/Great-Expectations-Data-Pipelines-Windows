from datetime import datetime, timedelta
from utils import local_to_s3

from airflow import DAG
from airflow.models import Variable

from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

# Get exported variables from Airflow (taskbar Admin -> Variables)
# Add AWS connection as well (taskbar Admin -> Connections or use Shell command)
BUCKET_NAME = Variable.get("BUCKET_NAME")

# Default arguments for defining the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": True,
    "wait_for_downstream": True,
    "start_date": datetime.now(),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

# Running DAG everyday at midnight
dag = DAG(
    dag_id="retail_data_pipeline",
    default_args=default_args,
    schedule_interval="0 0 * * *",
    max_active_runs=1,
)

# Copies PostgresDB data into a CSV file in the temporary folder
extract_retail_data = PostgresOperator(
    dag=dag,
    task_id="extract_retail_data",
    sql="./scripts/sql/extract_retail_data.sql",
    postgres_conn_id="postgres_default",
    params={"to_temp": "/temp/retail_profiling.csv"},
)

validate_extract_retail_data = BashOperator(
    dag=dag,
    task_id="validate_extract_retail_data",
    bash_command="cd /opt/airflow/; \
great_expectations checkpoint run retail_checkpoint",
)

# Moves CSV file from temp folder to S3 data lake raw folder
load_retail_data = PythonOperator(
    dag=dag,
    task_id="load_retail_data",
    python_callable=local_to_s3,
    op_kwargs={
        "file_name": "/temp/retail_profiling.csv",
        "key": "raw/retail/{{ ds }}/retail_profiling.csv",  # `ds` is the Jinja macro for execution date
        "bucket_name": BUCKET_NAME,
        "remove_local": True,
    },
)

end_of_data_pipeline = DummyOperator(dag=dag, task_id="end_of_data_pipeline")


(
    extract_retail_data
    >> validate_extract_retail_data
    >> load_retail_data
    >> end_of_data_pipeline
)
