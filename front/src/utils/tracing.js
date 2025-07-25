/**
 * Утилиты для работы с трассировкой (tracing)
 */

// Генерация уникального trace_id в формате UUID-подобного ID
export function generateTraceId() {
    // Генерируем 32-символьный hex-идентификатор (128 бит)
    return 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Создание заголовков для HTTP запросов с trace_id
export function createTracingHeaders(traceId = null) {
    const currentTraceId = traceId || generateTraceId();

    return {
        'X-Trace-ID': currentTraceId,
        'Content-Type': 'application/json',
        // Можно добавить дополнительные заголовки для OpenTelemetry
        'X-Request-ID': generateTraceId().substring(0, 16),
    };
}

// Получение trace_id из localStorage или создание нового
export function getOrCreateSessionTraceId() {
    const SESSION_TRACE_KEY = 'app_session_trace_id';

    let sessionTraceId = localStorage.getItem(SESSION_TRACE_KEY);

    if (!sessionTraceId) {
        sessionTraceId = generateTraceId();
        localStorage.setItem(SESSION_TRACE_KEY, sessionTraceId);
    }

    return sessionTraceId;
}

// Очистка session trace_id (например, при логауте)
export function clearSessionTraceId() {
    localStorage.removeItem('app_session_trace_id');
}

// Создание trace_id для конкретной операции (комбинирует session + operation)
export function createOperationTraceId(operation = 'default') {
    const sessionId = getOrCreateSessionTraceId().substring(0, 16);
    const operationId = generateTraceId().substring(0, 16);
    return `${sessionId}-${operationId}-${operation}`.substring(0, 32);
}

// Логирование trace информации
export function logTraceInfo(operation, traceId, additionalData = {}) {
    console.log(`[TRACE] ${operation}:`, {
        traceId,
        timestamp: new Date().toISOString(),
        ...additionalData
    });
}
