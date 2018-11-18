#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt', 'r') as f:
    install_requires = [
        s for s in [
            line.strip(' \n') for line in f
        ] if not s.startswith('#') and s != ''
    ]


setup(
    name='airflow_operators_metrics',
    description='Collector system metrics of airflow processes',
    version='0.1',
    install_requires=install_requires,
)
