import signal
import time

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def eat_memory(mem_size, seconds_limit=60*10):
    def _eat_memory():
        """ Create var some with size ~mem_size and sleep in loop until seconds_limit
        or SIGINT or SIGTERM
        """
        some = '1' * mem_size
        _eat_memory.is_stop = False
        end_time = time.time() + seconds_limit

        def stop():
            _eat_memory.is_stop = True

        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)

        while not _eat_memory.is_stop and time.time() < end_time:
            time.sleep(1)
    return _eat_memory


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}


dag = DAG(
    dag_id='memory',
    schedule_interval='@hourly',
    default_args=args,
)


memory_consumer = PythonOperator(
    task_id='memory_consumer',
    dag=dag,
    python_callable=eat_memory(mem_size=1024 * 1024 * 200),  # ~200Mb
)
