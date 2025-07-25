/**
 * HTTP клиент с поддержкой трассировки
 */

import axios from 'axios';
import { createTracingHeaders, createOperationTraceId, logTraceInfo } from './tracing.js';

const API_BASE_URL = 'http://localhost:8000';

// Создаем экземпляр axios с предустановленной конфигурацией
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
});

// Добавляем interceptor для автоматического добавления trace_id
apiClient.interceptors.request.use(
    (config) => {
        // Генерируем trace_id для каждого запроса
        const operation = `${config.method?.toUpperCase()}_${config.url?.replace(/^\//, '').replace(/\//g, '_')}`;
        const traceId = createOperationTraceId(operation);

        // Добавляем заголовки трассировки
        const tracingHeaders = createTracingHeaders(traceId);
        config.headers = {
            ...config.headers,
            ...tracingHeaders,
        };

        // Сохраняем trace_id в конфиге для логирования
        config.metadata = {
            traceId,
            operation,
            startTime: Date.now(),
        };

        logTraceInfo(`REQUEST_START: ${operation}`, traceId, {
            url: config.url,
            method: config.method,
            data: config.data,
        });

        return config;
    },
    (error) => {
        logTraceInfo('REQUEST_ERROR', 'unknown', { error: error.message });
        return Promise.reject(error);
    }
);

// Добавляем interceptor для логирования ответов
apiClient.interceptors.response.use(
    (response) => {
        const { traceId, operation, startTime } = response.config.metadata || {};
        const duration = Date.now() - (startTime || 0);

        logTraceInfo(`RESPONSE_SUCCESS: ${operation}`, traceId, {
            status: response.status,
            duration: `${duration}ms`,
            backendTraceId: response.headers['x-backend-trace-id'],
            responseData: response.data,
        });

        return response;
    },
    (error) => {
        const { traceId, operation, startTime } = error.config?.metadata || {};
        const duration = Date.now() - (startTime || 0);

        logTraceInfo(`RESPONSE_ERROR: ${operation}`, traceId, {
            status: error.response?.status,
            duration: `${duration}ms`,
            error: error.message,
            responseData: error.response?.data,
        });

        return Promise.reject(error);
    }
);

// API методы
export const entitiesAPI = {
    // Получить все entities
    async getAll() {
        const response = await apiClient.get('/entities/');
        return response.data;
    },

    // Получить entity по ID
    async getById(entityId) {
        const response = await apiClient.get(`/entities/${entityId}/`);
        return response.data;
    },

    // Создать новую entity
    async create(entityData) {
        const response = await apiClient.post('/entities/', entityData);
        return response.data;
    },

    // Работа с Redis
    async getRedisValue() {
        const response = await apiClient.get('/redis-get/');
        return response.data;
    },

    async setRedisValue(value) {
        const response = await apiClient.post('/redis-set/', null, {
            params: { value }
        });
        return response.data;
    },

    async deleteRedisValue() {
        const response = await apiClient.post('/redis-delete/');
        return response.data;
    },

    // Тестовые endpoints
    async testRandomStatus() {
        const response = await apiClient.get('/random_status');
        return response.data;
    },

    async testRandomSleep() {
        const response = await apiClient.get('/random_sleep');
        return response.data;
    },

    async testChain() {
        const response = await apiClient.get('/chain');
        return response.data;
    },
};

export default apiClient;
