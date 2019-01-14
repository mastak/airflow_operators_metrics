## Airflow operator stats

Gather system information about airflow processes. 

### How to use 

* Run airflow_operators_metrics container on each node with airflow workers like:  
```
docker run -d -v /proc:/host/proc:ro -v /etc/hostname:/host/hostname:ro -e CUSTOM_PROCFS_PATH=/host/proc -e HOSTNAME_PATH=/host/hostname mastak/airflow_operator_stats:alpine
```


* Add scrapper config to the prometheus, docker swarm example:
```
scrape_configs:
  - job_name: 'airflow-exporter'
    dns_sd_configs:
    - names:
      - 'tasks.airflow-exporter'
      type: 'A'
      port: 8000
```      
* Add dashboard to the Grafana, create your own or you can use it: https://grafana.com/dashboards/9672

### Example

Example folder contains docker-compose.yml for general information,
but right now it does not work.