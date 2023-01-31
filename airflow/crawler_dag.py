import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

base_dir = "/Users/ecokim/Desktop/work/research_portal_crawler"
venv = base_dir+'/venv/bin'
dag=DAG(
    dag_id='portal_crawler',
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval=None
)

crawl_category=BashOperator(
    task_id="crawl_category",
    bash_command=f"{venv}/ansible-playbook -i {base_dir}/ansible/hosts {base_dir}/ansible/crawl_category.yml",
    dag=dag
)

def test():
    print('test success')

test_func=PythonOperator(
    task_id="test_func",
    python_callable=test,
    dag=dag
)

crawl_category >> test_func
