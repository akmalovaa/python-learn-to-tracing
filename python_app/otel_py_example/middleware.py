"""
Middleware для обработки trace_id из фронтенда
"""

import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.propagate import extract
from opentelemetry.context import Context
from loguru import logger


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware для обработки trace_id, переданного из фронтенда
    """

    def __init__(self, app, trace_header_name: str = "X-Trace-ID"):
        super().__init__(app)
        self.trace_header_name = trace_header_name
        self.tracer = trace.get_tracer(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Извлекаем trace_id из заголовка
        frontend_trace_id = request.headers.get(self.trace_header_name)

        # Получаем контекст из стандартных заголовков OpenTelemetry (если есть)
        carrier = dict(request.headers)
        parent_context = extract(carrier)

        # Если фронтенд передал свой trace_id, логируем его
        if frontend_trace_id:
            logger.info(f"Received trace_id from frontend: {frontend_trace_id}")

        # Создаем новый спан для этого запроса
        with self.tracer.start_as_current_span(
            name=f"{request.method} {request.url.path}",
            context=parent_context,
            kind=SpanKind.SERVER,
        ) as span:
            # Добавляем атрибуты к спану
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.route", request.url.path)

            if frontend_trace_id:
                span.set_attribute("frontend.trace_id", frontend_trace_id)
                span.set_attribute("custom.trace_id", frontend_trace_id)

            # Сохраняем trace_id в request state для использования в handlers
            request.state.frontend_trace_id = frontend_trace_id
            request.state.otel_trace_id = trace.format_trace_id(span.get_span_context().trace_id)

            try:
                # Выполняем запрос
                response = await call_next(request)

                # Добавляем статус код в спан
                span.set_attribute("http.status_code", response.status_code)

                if response.status_code >= 400:
                    span.set_status(Status(StatusCode.ERROR))
                else:
                    span.set_status(Status(StatusCode.OK))

                # Добавляем trace_id в заголовки ответа для фронтенда
                response.headers["X-Backend-Trace-ID"] = request.state.otel_trace_id
                if frontend_trace_id:
                    response.headers["X-Frontend-Trace-ID"] = frontend_trace_id

                return response

            except Exception as e:
                # Записываем ошибку в спан
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Error processing request: {e}")
                raise


def get_trace_id_from_request(request: Request) -> Optional[str]:
    """
    Вспомогательная функция для получения trace_id из request
    """
    return getattr(request.state, "frontend_trace_id", None)


def get_current_trace_id() -> str:
    """
    Получить текущий OpenTelemetry trace_id
    """
    current_span = trace.get_current_span()
    if current_span and current_span.get_span_context().trace_id:
        return trace.format_trace_id(current_span.get_span_context().trace_id)
    return "unknown"


def create_child_span(name: str, attributes: dict = None) -> trace.Span:
    """
    Создать дочерний спан с переданными атрибутами
    """
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(name)

    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span
