# Python tracing

Repository for experiments to understand tracing: 
- Python (FastAPI, uv)
- Frontend (Vue.js)
- OpenTelemetry collector
- Tempo
- Grafana
- Prometheus

![scheme](./images/scheme.png)

### Useful materials
**main:**
- https://github.com/open-telemetry/opentelemetry-collector
- https://opentelemetry.io/docs/languages/python/getting-started/
- 

**web:**
- https://jorzel.hashnode.dev/understanding-distributed-tracing-a-python-guide-with-opentelemetry-and-grafana-tempo
- https://www.aspecto.io/blog/getting-started-with-opentelemetry-python/
- https://uptrace.dev/get/instrument/opentelemetry-fastapi.html#fastapi-instrumentation
- 

**github examples:**
- https://github.com/SigNoz/opentelemetry-python-example
- https://github.com/neverlock/python-opentelemetry-rabbitmq-tempo
- https://github.com/jorzel/tracing-otel
- https://github.com/softwarebloat/python-tracing-demo
- https://github.com/blueswen/fastapi-observability
- https://github.com/GRomR1/monitoring-microservices-demo
- https://github.com/lperdereau/opentelemetry-poc
- https://github.com/pasdam/playground-docker-grafana-prometheus-loki-tempo


### scripts:

```shell
k6 run scripts/k6_fastapi_get.js
```

### locahost services

Start
```
docker compose up -d
```

After run docker compose
- [Python_app](http://localhost:8000)
- [Grafana](http://localhost:3000)
- [Prometheus](http://localhost:9090)

test alembic migrations
```
#local
uv run alembic -c otel_py_example/alembic.ini upgrade head
# docker
chmod +x scripts/alembic.sh && ./scripts/alembic.sh current
./scripts/alembic.sh upgrade head
```

dev
```
docker-compose down && docker-compose up -d --build
```

