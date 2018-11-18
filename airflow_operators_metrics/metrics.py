import logging
import typing as t
from dataclasses import dataclass

import psutil
from prometheus_client import Gauge, Summary

logger = logging.getLogger(__name__)

COLLECT_TIME = Summary('airflow_collecting_stats_seconds',
                       'Time spent processing collecting stats')


@dataclass
class ProcessMetrics:
    dag: str
    operator: str
    exec_date: str
    is_local: bool
    is_raw: bool

    mem_rss: int
    mem_vms: int
    mem_shared: int
    mem_text: int
    mem_data: int
    mem_lib: int
    mem_uss: int
    mem_pss: int
    mem_swap: int

    # cpu_num: int
    cpu_percent: float
    cpu_times_user: float
    cpu_times_system: float


class MetricsContainer:
    def __init__(self, prefix=None,
                 global_labels: t.Optional[t.Dict[str, str]]=None):
        self._prefix = prefix
        self._global_labels = global_labels
        labels = ('name', 'dag', 'operator', 'exec_date')
        if global_labels:
            labels = labels + tuple(global_labels.keys())

        def gauge(name, documentation, labelnames=(), *args, **kwargs):
            if prefix:
                name = f'{prefix}_{name}'
            labelnames += labels
            return Gauge(name, documentation, labelnames, *args, **kwargs)

        self._mem_rss = gauge('airflow_process_mem_rss',
                              'Non-swapped physical memory')
        self._mem_vms = gauge('airflow_process_mem_vms',
                              'Amount of virtual memory')
        self._mem_shared = gauge('airflow_process_mem_shared',
                                 'Amount of shared memory')
        self._mem_text = gauge('airflow_process_mem_text',
                               'Devoted to executable code')
        self._mem_lib = gauge('airflow_process_mem_lib', 'Used by shared libraries')
        self._mem_uss = gauge('airflow_process_mem_uss',
                              'Mem unique to a process and which would be freed '
                              'if the process was terminated right now')
        self._mem_swap = gauge('airflow_process_mem_swap',
                               'Amount of swapped memory')
        self._mem_pss = gauge('airflow_process_mem_pss',
                              'Shared with other processes, accounted in a way that '
                              'the amount is divided evenly between processes '
                              'that share it')

        # self._cpu_num = gauge('airflow_process_mem_swap',
        # 'Amount of swapped memory')
        self._cpu_percent = gauge('airflow_process_cpu_percent',
                                  'System-wide CPU utilization as a percentage '
                                  'of the process')
        self._cpu_times_user = gauge('airflow_process_cpu_times_user',
                                     'CPU times user')
        self._cpu_times_system = gauge('airflow_process_cpu_times_system',
                                       'CPU times system')

    @COLLECT_TIME.time()
    def collect(self):
        handled = 0
        for process_metrics in _get_processes_metrics():
            self._handle_process_metrics(process_metrics)
            handled += 1
        logger.info(f'Gathered metrics from {handled} processes')

    def _handle_process_metrics(self, metrics: ProcessMetrics):
        name = _get_process_name(metrics)
        labels = {'name': name, 'dag': metrics.dag,
                  'operator': metrics.operator, 'exec_date': metrics.exec_date}
        if self._global_labels:
            labels.update(self._global_labels)

        self._mem_rss.labels(**labels).set(metrics.mem_rss)
        self._mem_vms.labels(**labels).set(metrics.mem_vms)
        self._mem_shared.labels(**labels).set(metrics.mem_shared)
        self._mem_text.labels(**labels).set(metrics.mem_text)
        self._mem_uss.labels(**labels).set(metrics.mem_uss)
        self._mem_swap.labels(**labels).set(metrics.mem_swap)
        self._mem_pss.labels(**labels).set(metrics.mem_pss)

        self._cpu_percent.labels(**labels).set(metrics.cpu_percent)
        self._cpu_times_user.labels(**labels).set(metrics.cpu_times_user)
        self._cpu_times_system.labels(**labels).set(metrics.cpu_times_system)


def _get_processes_metrics() -> t.Iterator[ProcessMetrics]:
    for process in psutil.process_iter():
        airflow_data = get_airflow_data(process)
        if not airflow_data:
            continue

        mem = process.memory_full_info()
        cpu_times = process.cpu_times()

        yield ProcessMetrics(
            dag=airflow_data['dag'],
            operator=airflow_data['operator'],
            exec_date=airflow_data['exec_date'],
            is_local=airflow_data['is_local'],
            is_raw=airflow_data['is_raw'],

            mem_rss=mem.rss,
            mem_vms=mem.vms,
            mem_shared=mem.shared,
            mem_text=mem.text,
            mem_data=mem.data,
            mem_lib=mem.lib,
            mem_uss=mem.uss,
            mem_pss=mem.pss,
            mem_swap=mem.swap,

            cpu_percent=process.cpu_percent(),
            cpu_times_user=cpu_times.user,
            cpu_times_system=cpu_times.system,
        )


def _get_process_name(metrics: ProcessMetrics):
    dag, operator = metrics.dag, metrics.operator
    if dag not in operator:
        name_parts = [f'{dag}.{operator}']
    else:
        name_parts = [operator]
    name_parts.append(metrics.exec_date)
    if metrics.is_local:
        name_parts.append('local')
    if metrics.is_raw:
        name_parts.append('is_raw')
    return '_'.join(name_parts)


def get_airflow_data(
        process: psutil.Process) -> t.Optional[t.Dict[str, t.Union[str, bool]]]:
    cmdline = process.cmdline()
    if not cmdline or not cmdline[0].startswith('/usr/bin/python'):
        return None

    for cmd_arg in process.cmdline():
        if 'airflow run' not in cmd_arg:
            continue

        airflow_args = cmd_arg.split()
        dag = airflow_args[3]
        operator = airflow_args[4]
        exec_date = airflow_args[5][5:25]
        is_local = any([i == '--local' for i in airflow_args])
        is_raw = any([i == '--raw' for i in airflow_args])

        return {
            'dag': dag,
            'operator': operator,
            'exec_date': exec_date,
            'is_local': is_local,
            'is_raw': is_raw,
        }
