<script setup>
import { ref } from 'vue'
import { addPerson } from '../state.js'
import { apiCreateUser } from '../api.js'

const showForm = ref(false)
const name = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  const trimmed = name.value.trim()
  const pwd = password.value
  if (!trimmed || !pwd) return
  error.value = ''
  loading.value = true
  try {
    const user = await apiCreateUser(trimmed, pwd)
    addPerson(user, { select: true })
    name.value = ''
    password.value = ''
    showForm.value = false
  } catch (e) {
    if (typeof e.detail === 'string') {
      error.value = e.detail
    } else if (Array.isArray(e.detail)) {
      error.value = e.detail.map(d => d.msg.replace(/^Value error,\s*/i, '')).join(' · ')
    } else {
      error.value = 'Erreur lors de la création'
    }
  } finally {
    loading.value = false
  }
}

function cancel() {
  name.value = ''
  password.value = ''
  error.value = ''
  showForm.value = false
}
</script>

<template>
  <div class="person-form">
    <button v-if="!showForm" @click="showForm = true" class="add-btn">+ Personne</button>
    <div v-else class="form-inline">
      <input
        v-model="name"
        @keyup.escape="cancel"
        placeholder="Identifiant..."
        class="name-input"
        autocomplete="off"
        autofocus
      />
      <input
        v-model="password"
        @keyup.enter="submit"
        @keyup.escape="cancel"
        type="password"
        placeholder="Mot de passe..."
        class="name-input"
        autocomplete="new-password"
      />
      <p v-if="error" class="form-error">{{ error }}</p>
      <div class="form-actions">
        <button @click="submit" class="ok-btn" :disabled="loading">OK</button>
        <button @click="cancel" class="cancel-btn">&#x2715;</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.person-form {
  margin: 12px 0;
}
.add-btn {
  background: #4A90D9;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}
.add-btn:hover {
  background: #357ABD;
}
.form-inline {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.name-input {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 14px;
  width: 100%;
}
.form-error {
  color: #e74c3c;
  font-size: 12px;
  margin: 0;
}
.form-actions {
  display: flex;
  gap: 6px;
}
.ok-btn {
  background: #2ECC71;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
}
.ok-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
.cancel-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
}
</style>
