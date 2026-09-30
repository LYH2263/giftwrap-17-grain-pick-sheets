<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'

const items = ref([])
const err = ref('')
const widths = ref({})
const saving = ref(0)

onMounted(load)

async function load() {
  err.value = ''
  try {
    items.value = (await getJSON('/api/papers')).items
    widths.value = Object.fromEntries(items.value.map((p) => [p.id, p.roll_width]))
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function saveWidth(p) {
  err.value = ''
  saving.value = p.id
  try {
    await patchJSON(`/api/papers/${p.id}`, { roll_width: Number(widths.value[p.id]) })
    await load()
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    saving.value = 0
  }
}
</script>

<template>
  <div class="page">
    <h1>包装纸</h1>
    <p class="lede">测算已绑卷：算纸按卷宽做两向 sheets 试算。改卷宽只影响此后的测算，已落库的用纸档仍按写入时的卷宽回放。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-else class="paper-grid">
      <div v-for="p in items" :key="p.id" class="paper-tile">
        <strong>{{ p.name }}</strong>
        <span class="meta">当前卷宽 {{ p.roll_width }} m</span>
        <div class="row tile-row">
          <input
            v-model.number="widths[p.id]"
            class="width-input"
            type="number"
            min="0.01"
            step="0.05"
            aria-label="卷宽（米）"
          />
          <button class="ghost" :disabled="saving === p.id" @click="saveWidth(p)">改卷宽</button>
        </div>
      </div>
    </div>
  </div>
</template>
