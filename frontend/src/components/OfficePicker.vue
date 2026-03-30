<script setup>
import { offices, activeOfficeId, switchOffice } from '../state.js'
</script>

<template>
  <div v-if="offices.length > 1" class="office-picker">
    <select id="office-select" name="office" aria-label="Bureau" :value="activeOfficeId" @change="switchOffice(Number($event.target.value))">
      <option v-for="o in offices" :key="o.id" :value="o.id">{{ o.name }}</option>
    </select>
  </div>
</template>

<style scoped>
.office-picker select {
  background: #23272e;
  color: #fff;
  border: 1px solid #555;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
}
.office-picker select:hover {
  border-color: #888;
}
</style>
