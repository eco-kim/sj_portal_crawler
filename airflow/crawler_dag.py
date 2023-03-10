import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from crawl import category

base_dir = ""
venv = base_dir+'/venv/bin'
dag=DAG(
    dag_id='portal_crawler',
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval=None
)

crawl_category = PythonOperator(
    task_id='category',
    Python_callable=category,
    dag=dag
)

##인스턴스 분배 작업 추가예정

crawl_items = BashOperator(
    task_id="items",
    bash_command=f"{venv}/ansible-playbook -i {base_dir}/ansible/hosts {base_dir}/ansible/crawl_items.yml",
    dag=dag
)

def test():
    print('test success')

test_func=PythonOperator(
    task_id="test_func",
    python_callable=test,
    dag=dag
)

crawl_category >> crawl_items >> test_func
