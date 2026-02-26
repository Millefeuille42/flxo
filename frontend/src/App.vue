<script setup>
import { onMounted, ref } from 'vue'
import WeekNav from './components/WeekNav.vue'
import PersonForm from './components/PersonForm.vue'
import FloorPlan from './components/FloorPlan.vue'
import WeekGrid from './components/WeekGrid.vue'
import LoginView from './components/LoginView.vue'
import { sortedPersons, selectedPersonId, removePerson, authToken, loggedUser, isLoading, ssoEnabled, logoUrl, initApp } from './state.js'
import { setToken, apiDeleteUser } from './api.js'

onMounted(async () => {
  if (authToken.value) {
    try {
      await initApp()
    } catch (e) {
      if (e.status === 401) {
        setToken(null)
        authToken.value = null
      }
    }
  }
})

async function onLoggedIn(token) {
  setToken(token)
  authToken.value = token
  await initApp()
}

const personToDelete = ref(null)

function confirmDelete(person) {
  personToDelete.value = person
}

async function doDelete() {
  const person = personToDelete.value
  personToDelete.value = null
  if (person.backendId) {
    try {
      await apiDeleteUser(person.backendId)
    } catch (e) {
      console.error('Failed to delete user:', e)
      return
    }
  }
  removePerson(person.id)
}

function logout() {
  setToken(null)
  authToken.value = null
  loggedUser.value = null
}
</script>

<template>
  <LoginView v-if="!authToken" @logged-in="onLoggedIn" />
  <div v-else-if="isLoading" class="app-loading">Chargement...</div>
  <div v-else class="app-root">
    <div class="topbar">
      <span class="topbar-user">{{ loggedUser?.username }}</span>
      <button class="logout-btn" @click="logout">Se déconnecter</button>
    </div>
    <div class="app">
    <header class="app-header">
      <img v-if="logoUrl" :src="logoUrl" alt="Logo" class="app-logo" />
      <WeekNav />
    </header>
    <main class="app-main">
      <aside class="sidebar">
        <FloorPlan />
        <PersonForm v-if="!ssoEnabled" />
        <div class="person-list" v-if="sortedPersons.length">
          <div
            v-for="p in sortedPersons"
            :key="p.id"
            :class="['person-chip', { active: selectedPersonId === p.id }]"
            @click="selectedPersonId = p.id"
          >
            <span class="chip-dot" :style="{ background: p.color }"></span>
            <span class="chip-name">{{ p.name }}{{ p.isLoggedUser ? ' (moi)' : '' }}</span>
            <button v-if="!ssoEnabled" class="chip-remove" @click.stop="confirmDelete(p)" title="Supprimer">&times;</button>
          </div>
        </div>
      </aside>
      <section class="grid-area">
        <WeekGrid />
      </section>
    </main>
  </div>
  </div>

  <div v-if="personToDelete" class="modal-overlay" @click.self="personToDelete = null">
    <div class="modal">
      <p>Supprimer <strong>{{ personToDelete.name }}</strong> ?</p>
      <div class="modal-actions">
        <button class="modal-confirm" @click="doDelete">Supprimer</button>
        <button class="modal-cancel" @click="personToDelete = null">Annuler</button>
      </div>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #fafafa;
  color: #333;
}
.topbar {
  width: 100%;
  background: #1a1a2e;
  color: #ccc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 6px 20px;
  font-size: 13px;
}
.topbar-user {
  opacity: 0.7;
}
.logout-btn {
  background: none;
  border: 1px solid #555;
  color: #ccc;
  border-radius: 4px;
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.logout-btn:hover {
  border-color: #aaa;
  color: #fff;
}
.app-loading {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #888;
}
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}
.app-logo {
  height: 32px;
  width: auto;
}
.app-main {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}
.sidebar {
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.grid-area {
  flex: 1;
  min-width: 0;
}
.person-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.person-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.15s;
}
.person-chip:hover {
  background: #eee;
}
.person-chip.active {
  background: #e8eeff;
  font-weight: 600;
}
.chip-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.chip-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chip-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #bbb;
  padding: 0 2px;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.15s, color 0.15s;
  flex-shrink: 0;
}
.person-chip:hover .chip-remove {
  opacity: 1;
}
.chip-remove:hover {
  color: #e74c3c;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal {
  background: white;
  border-radius: 8px;
  padding: 24px 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  min-width: 260px;
  text-align: center;
}
.modal p {
  font-size: 15px;
  margin-bottom: 20px;
  color: #333;
}
.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}
.modal-confirm {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 7px 18px;
  font-size: 13px;
  cursor: pointer;
}
.modal-confirm:hover {
  background: #c0392b;
}
.modal-cancel {
  background: none;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 7px 18px;
  font-size: 13px;
  cursor: pointer;
}
.modal-cancel:hover {
  background: #f5f5f5;
}
</style>
