<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const papers = ref([])
const bid = ref(null)
const pid = ref(null)
const out = ref(null)
const err = ref('')
const busy = ref(false)

const GRAIN_LABEL = { length: '长向（卷宽对齐长向主尺）', width: '宽向（卷宽对齐宽向主尺）' }

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    papers.value = (await getJSON('/api/papers')).items.filter((p) => p.data_quality !== 'dirty')
    if (papers.value.length) pid.value = papers.value[0].id
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function go(save) {
  err.value = ''
  if (!pid.value) {
    err.value = '请先选择纸卷：测算必须绑卷。'
    return
  }
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', { box_id: bid.value, paper_id: pid.value, save: true })
      : await getJSON(`/api/estimate?box_id=${bid.value}&paper_id=${pid.value}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">测算绑卷：选盒与纸卷后按两种卷向试算 sheets，择优取用；确认后写入用纸档。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model.number="pid">
        <option v-for="p in papers" :key="p.id" :value="p.id">{{ p.name }}（卷宽 {{ p.roll_width }} m）</option>
      </select>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        选用卷向 <strong>{{ GRAIN_LABEL[out.grain] ?? out.grain }}</strong>，需
        <strong>{{ out.sheets }}</strong> 张
        <span v-if="out.tie_break" class="pill">两向相同·破平优先长向</span>
      </p>
      <div class="trial-grid">
        <div class="trial-cell" :class="{ picked: out.grain === 'length' }">
          <span class="trial-title">卷宽对齐长向主尺</span>
          <span class="meta">长向主尺 {{ out.dim_len }} m ÷ 卷宽 {{ out.roll_width }} m</span>
          <strong>{{ out.sheets_len }} 张</strong>
        </div>
        <div class="trial-cell" :class="{ picked: out.grain === 'width' }">
          <span class="trial-title">卷宽对齐宽向主尺</span>
          <span class="meta">宽向主尺 {{ out.dim_wid }} m ÷ 卷宽 {{ out.roll_width }} m</span>
          <strong>{{ out.sheets_wid }} 张</strong>
        </div>
      </div>
      <p class="stat-line" v-if="out.ribbon">
        十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m
      </p>
      <p v-if="out.run_id" class="stat-line">已写入用纸档 #{{ out.run_id }}。</p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>
