<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')
const openId = ref(0)
const detail = ref(null)

const GRAIN_LABEL = { length: '长向', width: '宽向' }
const grainLabel = (g) => GRAIN_LABEL[g] ?? g ?? '—'

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function toggle(id) {
  err.value = ''
  if (openId.value === id) {
    openId.value = 0
    detail.value = null
    return
  }
  try {
    detail.value = await getJSON(`/api/runs/${id}`)
    openId.value = id
  } catch (e) {
    err.value = String(e.message || e)
  }
}
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果。列表与详情均回放写入时的卷向与 sheets，不随纸卷改宽重择。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id" class="run-row" @click="toggle(r.id)">
        <span>{{ r.box_name }}</span>
        <span class="meta">
          {{ r.result?.paper_m2 ?? '—' }} m² · {{ grainLabel(r.result?.grain) }} {{ r.result?.sheets ?? '—' }} 张
          <span v-if="r.result?.tie_break" class="pill">破平</span>
        </span>
        <div v-if="openId === r.id && detail" class="run-detail">
          <p class="stat-line">
            纸卷 {{ detail.result?.paper_name ?? '—' }}（写入时卷宽 {{ detail.result?.roll_width ?? '—' }} m）
            · 选用 {{ grainLabel(detail.result?.grain) }} {{ detail.result?.sheets ?? '—' }} 张
            <span v-if="detail.result?.tie_break" class="pill">两向相同·破平优先长向</span>
          </p>
          <p class="stat-line">
            两向试算：长向主尺 {{ detail.result?.dim_len ?? '—' }} m → {{ detail.result?.sheets_len ?? '—' }} 张；
            宽向主尺 {{ detail.result?.dim_wid ?? '—' }} m → {{ detail.result?.sheets_wid ?? '—' }} 张
          </p>
          <p class="stat-line meta">#{{ detail.id }} · {{ detail.created_at }}<template v-if="detail.note"> · {{ detail.note }}</template></p>
        </div>
      </li>
    </ul>
  </div>
</template>
