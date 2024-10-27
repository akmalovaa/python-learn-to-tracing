$Env:AUTOMAT_EXPOSE_PORT = 8000
$Env:OTEL_PYTHON_LOG_CORRELATION = "true"
$Env:OTEL_PYTHON_LOG_LEVEL = "debug"
$Env:OTEL_RESOURCE_ATTRIBUTES="service.name=automat,service.instance.id=automat-instance-1"
$Env:OTEL_TRACES_EXPORTER = "otlp"
$Env:OTEL_LOGS_EXPORTER = "otlp"
$Env:OTEL_METRICS_EXPORTER = "otlp"
$Env:OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED = "true"
$Env:OTEL_EXPORTER_OTLP_ENDPOINT = "http://localhost:4317"
opentelemetry-instrument python main_auto.py