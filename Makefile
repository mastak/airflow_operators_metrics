.PHONY: all build push

all: build push

build:
	docker build -f ubuntu.Dockerfile -t mastak/airflow_operator_stats:ubuntu .

push:
	docker push mastak/airflow_operator_stats:ubuntu

run:
	docker run --privileged --cap-add SYS_PTRACE -v /proc:/host-proc:ro \
	-e CUSTOM_PROCFS_PATH=/host-proc \
	mastak/airflow_operator_stats:ubuntu
