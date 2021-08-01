# Testing Airflow DAGs with Great Expectations

## Evaluation

- GreatExpectationsOperator is experimental and not fully supported yet
- Version 3 API doesn't work with GreatExpectationsOperator on Airflow
- Great Expectations needs to be installed on the Airflow Worker
- Great Expectations folder has to be mounted
- When connecting to Postgres container on local machine, the host name should be `localhost`,
  **BUT** when connecting from the Airflow Worker to run a DAG, the host name should be `postgres`.
- To run the BashOperator using GE CLI commands, `cd` into the directory where `great_expectations` folder is located

## Recommendations

- Use Version 2 API when you want to use Great Expectations with Airflow
- Specify the library to be installed (`great_expectations`) in the `PIP_ADDITIONAL_REQUIREMENTS` in the `docker-compose` file
- **Prerequisites:** Create a Data Context, connect to a Datasource, create an Expectations Suite, create a Checkpoint, and have an Airflow DAG ready
- Recommended to use BashOperator to validate data batches since it is the most intuitive and straightforward
- Can also use PythonOperator for validation but additional setup is necessary
- Simply plug in the BashOperator as a Task within the Airflow DAG
- **DO NOT** use GreatExpectationsOperator
- **DO NOT** use Version 3 API in conjunction with Airflow
- Keep in mind the host names to be used:
  - when connecting to Postgres from local machine or when connecting from Airflow Worker container
  - when running Airflow on local machine or when running Airflow on Docker
  - specify/edit the credentials in the `config-variables.yml` file in the `uncommitted` folder

## Debugging

- Version 3 API in Airflow is not supported: cannot find table, cannot get batches, cannot connect to Datasources (`KeyError`)
- Connectivity issues to Postgres container
- BashOperator cannot find Great Expectations folder
- **Very useful for debugging** to enter the Airflow Worker container (with `docker exec -it`) and directly run commands inside
  - helps with finding where folders are located
  - helps with comparison between running GE CLI commands in the container vs running CLI commands in local machine
  - helps with connectivity issues and resolving host names
