<script setup>
import { ref, onMounted } from 'vue'
import { entitiesAPI } from './utils/api.js'
import { getOrCreateSessionTraceId, logTraceInfo } from './utils/tracing.js'

const entities = ref([])
const loading = ref(false)
const error = ref('')
const sessionTraceId = ref('')
const lastBackendTraceId = ref('')

// Форма для создания новой entity
const newEntity = ref({
  name: '',
  description: ''
})
const creating = ref(false)

// Инициализация session trace ID
onMounted(() => {
  sessionTraceId.value = getOrCreateSessionTraceId()
  logTraceInfo('APP_MOUNTED', sessionTraceId.value, { component: 'App.vue' })
  fetchEntities()
})

const fetchEntities = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await entitiesAPI.getAll()
    entities.value = result.entities
    
    // Сохраняем информацию о трассировке для отображения
    if (result.trace_info) {
      lastBackendTraceId.value = result.trace_info.backend_trace_id
    }
    
    logTraceInfo('ENTITIES_FETCHED', sessionTraceId.value, { 
      count: entities.value.length,
      backendTraceId: lastBackendTraceId.value 
    })
  } catch (err) {
    error.value = `Error fetching entities: ${err.message}`
    console.error('Error fetching entities:', err)
  } finally {
    loading.value = false
  }
}

const createEntity = async () => {
  if (!newEntity.value.name.trim()) {
    error.value = 'Name is required'
    return
  }

  creating.value = true
  error.value = ''
  
  try {
    const result = await entitiesAPI.create({
      name: newEntity.value.name.trim(),
      description: newEntity.value.description.trim()
    })
    
    // Сохраняем информацию о трассировке
    if (result.trace_info) {
      lastBackendTraceId.value = result.trace_info.backend_trace_id
    }
    
    logTraceInfo('ENTITY_CREATED', sessionTraceId.value, {
      entityName: newEntity.value.name,
      backendTraceId: lastBackendTraceId.value
    })
    
    // Очищаем форму
    newEntity.value.name = ''
    newEntity.value.description = ''
    
    // Обновляем список
    await fetchEntities()
  } catch (err) {
    error.value = `Ошибка при создании записи: ${err.message}`
    console.error('Error creating entity:', err)
  } finally {
    creating.value = false
  }
}

// Тестовые функции для демонстрации трассировки
const testRandomStatus = async () => {
  try {
    await entitiesAPI.testRandomStatus()
  } catch (err) {
    console.error('Random status test failed:', err)
  }
}

const testRandomSleep = async () => {
  try {
    await entitiesAPI.testRandomSleep()
  } catch (err) {
    console.error('Random sleep test failed:', err)
  }
}

const testChain = async () => {
  try {
    await entitiesAPI.testChain()
  } catch (err) {
    console.error('Chain test failed:', err)
  }
}

// Загружаем данные при монтировании компонента
</script>

<template>
  <div class="container">
    <header>
      <h1>🔍 OpenTelemetry Tracing Example</h1>
      <p>FastAPI + Vue.js с передачей trace_id</p>
      <div class="trace-info">
        <p><strong>Session Trace ID:</strong> <code>{{ sessionTraceId }}</code></p>
        <p v-if="lastBackendTraceId"><strong>Last Backend Trace ID:</strong> <code>{{ lastBackendTraceId }}</code></p>
      </div>
      <div class="links">
        <p><a href="http://localhost:8000/docs" target="_blank">📖 FastAPI docs</a></p>
        <p><a href="http://localhost:3000" target="_blank">📊 Grafana</a></p>
      </div>
    </header>

    <main>
      <!-- Тестовые кнопки для трассировки -->
      <div class="test-section">
        <h3>🧪 Test actions</h3>
        <div class="test-buttons">
          <button @click="testRandomStatus" class="test-btn">🎲 Random Status</button>
          <button @click="testRandomSleep" class="test-btn">😴 Random Sleep</button>
          <button @click="testChain" class="test-btn">🔗 Chain Request</button>
        </div>
      </div>
      <!-- Форма для добавления новой записи -->
      <div class="form-section">
        <h3>➕ Add new entity</h3>
        <form @submit.prevent="createEntity" class="entity-form">
          <div class="form-group">
            <label for="name">Name:</label>
            <input 
              id="name"
              type="text" 
              v-model="newEntity.name" 
              placeholder="Enter name"
              required
              :disabled="creating"
            />
          </div>
          
          <div class="form-group">
            <label for="description">Description:</label>
            <input 
              id="description"
              type="text" 
              v-model="newEntity.description" 
              placeholder="Enter description (optional)"
              :disabled="creating"
            />
          </div>
          
          <button type="submit" :disabled="creating || !newEntity.name.trim()" class="create-btn">
            {{ creating ? 'Создаем...' : '➕ Add' }}
          </button>
        </form>
      </div>

      <!-- Управление списком -->
      <div class="controls">
        <button @click="fetchEntities" :disabled="loading">
          {{ loading ? 'Loading...' : '🔄 Refresh List' }}
        </button>
      </div>

      <div v-if="error" class="error">
        {{ error }}
      </div>

      <div v-if="loading" class="loading">
        Loading data...
      </div>

      <div v-else-if="entities.length === 0 && !error" class="empty-state">
        📭 The list is empty
      </div>

      <div v-else class="entities-list">
        <h2>📋 List ({{ entities.length }})</h2>
        <div v-for="entity in entities" :key="entity.id" class="entity-item">
          <div class="entity-id">#{{ entity.id }}</div>
          <div class="entity-name">{{ entity.name }}</div>
          <div class="entity-description" v-if="entity.description">
            {{ entity.description }}
          </div>
          <div class="entity-description" v-else>
            <em>Description is missing</em>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

h2 {
  color: #34495e;
  margin-bottom: 20px;
}

h3 {
  color: #34495e;
  margin-bottom: 15px;
}

.trace-info {
  background-color: #e8f4fd;
  border: 1px solid #bee5eb;
  border-radius: 6px;
  padding: 15px;
  margin: 15px 0;
  font-family: 'Courier New', monospace;
}

.trace-info code {
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #dee2e6;
  font-size: 12px;
  word-break: break-all;
}

.links {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 15px;
}

.links a {
  color: #3498db;
  text-decoration: none;
  font-weight: 600;
}

.links a:hover {
  text-decoration: underline;
}

.test-section {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.test-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.test-btn {
  background-color: #fd79a8;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.test-btn:hover {
  background-color: #e84393;
}

.form-section {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 30px;
}

.entity-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group input:disabled {
  background-color: #ecf0f1;
  cursor: not-allowed;
}

.create-btn {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.create-btn:hover:not(:disabled) {
  background-color: #229954;
}

.create-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.controls {
  text-align: center;
  margin-bottom: 30px;
}

button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #2980b9;
}

button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
  padding: 20px;
}

.error {
  background-color: #e74c3c;
  color: white;
  padding: 15px;
  border-radius: 6px;
  margin: 20px 0;
  text-align: center;
}

.empty-state {
  text-align: center;
  color: #7f8c8d;
  padding: 40px;
  font-size: 18px;
}

.entities-list {
  margin-top: 20px;
}

.entity-item {
  background-color: #ecf0f1;
  border: 1px solid #bdc3c7;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: box-shadow 0.3s;
}

.entity-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.entity-id {
  font-weight: bold;
  color: #3498db;
  font-size: 14px;
  margin-bottom: 8px;
}

.entity-name {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.entity-description {
  color: #7f8c8d;
  line-height: 1.4;
}
</style>
