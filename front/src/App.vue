<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const entities = ref([])
const loading = ref(false)
const error = ref('')

// Форма для создания новой entity
const newEntity = ref({
  name: '',
  description: ''
})
const creating = ref(false)

const API_BASE_URL = 'http://localhost:8000'

const fetchEntities = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.get(`${API_BASE_URL}/entities/`)
    entities.value = response.data.entities  // API возвращает {entities: [...]}
  } catch (err) {
    error.value = `Ошибка при загрузке данных: ${err.message}`
    console.error('Error fetching entities:', err)
  } finally {
    loading.value = false
  }
}

const createEntity = async () => {
  if (!newEntity.value.name.trim()) {
    error.value = 'Название обязательно для заполнения'
    return
  }

  creating.value = true
  error.value = ''
  
  try {
    await axios.post(`${API_BASE_URL}/entities/`, {
      name: newEntity.value.name.trim(),
      description: newEntity.value.description.trim()
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

// Загружаем данные при монтировании компонента
onMounted(() => {
  fetchEntities()
})
</script>

<template>
  <div class="container">
    <header>
      <h1>🔍 OpenTelemetry Tracing Example</h1>
      <p>FastAPI simple get/entities</p>
      <p><a href="http://localhost:8000/docs" target="_blank">FastAPI docs</a></p>
      <p><a href="http://localhost:3000" target="_blank">Grafana</a></p>
    </header>

    <main>
      <!-- Форма для добавления новой записи -->
      <div class="form-section">
        <h3>➕ Добавить новую запись</h3>
        <form @submit.prevent="createEntity" class="entity-form">
          <div class="form-group">
            <label for="name">Название:</label>
            <input 
              id="name"
              type="text" 
              v-model="newEntity.name" 
              placeholder="Введите название"
              required
              :disabled="creating"
            />
          </div>
          
          <div class="form-group">
            <label for="description">Описание:</label>
            <input 
              id="description"
              type="text" 
              v-model="newEntity.description" 
              placeholder="Введите описание (необязательно)"
              :disabled="creating"
            />
          </div>
          
          <button type="submit" :disabled="creating || !newEntity.name.trim()" class="create-btn">
            {{ creating ? 'Создаем...' : '➕ Добавить' }}
          </button>
        </form>
      </div>

      <!-- Управление списком -->
      <div class="controls">
        <button @click="fetchEntities" :disabled="loading">
          {{ loading ? 'Загрузка...' : '🔄 Обновить список' }}
        </button>
      </div>

      <div v-if="error" class="error">
        {{ error }}
      </div>

      <div v-if="loading" class="loading">
        Загружаем данные...
      </div>

      <div v-else-if="entities.length === 0 && !error" class="empty-state">
        📭 Список пуст
      </div>

      <div v-else class="entities-list">
        <h2>📋 Список ({{ entities.length }})</h2>
        <div v-for="entity in entities" :key="entity.id" class="entity-item">
          <div class="entity-id">#{{ entity.id }}</div>
          <div class="entity-name">{{ entity.name }}</div>
          <div class="entity-description" v-if="entity.description">
            {{ entity.description }}
          </div>
          <div class="entity-description" v-else>
            <em>Описание отсутствует</em>
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
