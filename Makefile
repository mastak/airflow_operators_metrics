.PHONY: all build push

BASE ?= ubuntu

alpine:
	$(eval BASE := alpine)

all: build push

build:
	docker build -f $(BASE).Dockerfile -t mastak/airflow_operator_stats:$(BASE) .

push:
	docker push mastak/airflow_operator_stats:$(BASE)

run:
	docker run --privileged --cap-add SYS_PTRACE -v /proc:/host-proc:ro \
	-e CUSTOM_PROCFS_PATH=/host-proc \
	mastak/airflow_operator_stats:$(BASE)
