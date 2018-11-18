import os
import time
import logging
import socket

import psutil
import prometheus_client as prom

from airflow_operators_metrics.metrics import MetricsContainer


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    http_port = int(os.getenv('HTTP_PORT', 8000))
    sleep_seconds = int(os.getenv('SLEEP_SECONDS', 4))
    name_prefix = os.getenv('METRIC_NAME_PREFIX')
    hostname_path = os.getenv('HOSTNAME_PATH')
    custom_procfs_path = os.getenv('CUSTOM_PROCFS_PATH')

    if custom_procfs_path:
        psutil.PROCFS_PATH = custom_procfs_path

    labels = {'hostname': socket.gethostname()}
    if hostname_path:
        with open(hostname_path) as fp:
            host_hostname = labels['host_hostname'] = fp.read().strip()
            logging.info('hostname from file %s', host_hostname)

    prom.start_http_server(http_port)
    metrics = MetricsContainer(name_prefix, global_labels=labels)
    try:
        while True:
            metrics.collect()
            time.sleep(sleep_seconds)
    except KeyboardInterrupt:
        pass
