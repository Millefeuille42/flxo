<script setup>
import { ref } from 'vue'
import { apiLogin } from '../api.js'

const emit = defineEmits(['logged-in'])

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  const u = username.value.trim()
  const p = password.value
  if (!u || !p) return
  loading.value = true
  try {
    const data = await apiLogin(u, p)
    emit('logged-in', data.access_token)
  } catch (e) {
    error.value = e.status === 401 ? 'Identifiants incorrects' : 'Erreur de connexion'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-bg">
    <div class="login-card">
      <h1 class="login-title">FlxO</h1>
      <p class="login-subtitle">Flex Office Planner</p>
      <form @submit.prevent="submit" class="login-form">
        <input
          v-model="username"
          type="text"
          placeholder="Identifiant"
          autocomplete="username"
          class="login-input"
          autofocus
        />
        <input
          v-model="password"
          type="password"
          placeholder="Mot de passe"
          autocomplete="current-password"
          class="login-input"
        />
        <p v-if="error" class="login-error">{{ error }}</p>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}
.login-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 40px 48px;
  width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
}
.login-title {
  font-size: 32px;
  font-weight: 700;
  color: #222;
  margin: 0;
}
.login-subtitle {
  font-size: 14px;
  color: #888;
  margin: -12px 0 0;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}
.login-input {
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}
.login-input:focus {
  outline: none;
  border-color: #4A90D9;
}
.login-error {
  color: #e74c3c;
  font-size: 13px;
  margin: 0;
}
.login-btn {
  background: #4A90D9;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}
.login-btn:hover:not(:disabled) {
  background: #357ABD;
}
.login-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
