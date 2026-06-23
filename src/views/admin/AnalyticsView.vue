<template>
  <div class="analytics-view">
    <div class="page-header">
      <div>
        <h1>📈 游客洞察</h1>
        <p class="subtitle">分析交互记录，生成游客关注点分析、情感趋势报告及服务建议</p>
      </div>
      <div class="header-actions">
        <select class="input-field date-select" v-model="dateRange" @change="loadData">
          <option value="7d">近7天</option>
          <option value="30d">近30天</option>
          <option value="90d">近90天</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else>
      <div class="summary-grid">
        <div class="summary-card card">
          <span class="summary-icon">😊</span>
          <div class="summary-data"><span class="summary-value">{{ summary.positive_ratio }}%</span><span class="summary-label">积极情感占比</span></div>
        </div>
        <div class="summary-card card">
          <span class="summary-icon">😐</span>
          <div class="summary-data"><span class="summary-value">{{ summary.neutral_ratio }}%</span><span class="summary-label">中性情感占比</span></div>
        </div>
        <div class="summary-card card">
          <span class="summary-icon">😢</span>
          <div class="summary-data"><span class="summary-value">{{ summary.negative_ratio }}%</span><span class="summary-label">消极情感占比</span></div>
        </div>
        <div class="summary-card card">
          <span class="summary-icon">⭐</span>
          <div class="summary-data"><span class="summary-value">{{ summary.avg_score }}</span><span class="summary-label">平均评分</span></div>
        </div>
      </div>

      <div class="cols-2">
        <div class="card">
          <h3>😌 情感趋势</h3>
          <div class="emotion-chart" ref="emotionChartRef"></div>
        </div>
        <div class="card">
          <h3>🔥 高频关键词</h3>
          <div class="word-cloud">
            <span v-for="w in keywords" :key="w.text" class="word-item" :style="{ fontSize: w.size + 'px', color: w.color, opacity: w.opacity }">{{ w.text }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-header"><h3>💡 服务建议</h3></div>
        <div class="suggestions-list">
          <div v-for="s in suggestions" :key="s.id" class="suggestion-item">
            <div class="sug-icon">{{ s.type === 'improve' ? '🔧' : s.type === 'praise' ? '🌟' : '📌' }}</div>
            <div class="sug-content">
              <div class="sug-title">{{ s.title }}</div>
              <div class="sug-desc">{{ s.description }}</div>
            </div>
            <span class="sug-urgency" :class="s.urgency">{{ s.urgency === 'high' ? '高优先级' : s.urgency === 'medium' ? '中优先级' : '低优先级' }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-header"><h3>💬 典型交互示例</h3></div>
        <div class="sample-list">
          <div v-for="s in samples" :key="s.id" class="sample-item">
            <div class="sample-q"><span class="sample-role user">游客</span>{{ s.question }}</div>
            <div class="sample-a"><span class="sample-role ai">小导</span>{{ s.answer }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { api } from '../../api.js'

const dateRange = ref('7d')
const emotionChartRef = ref(null)
const loading = ref(true)
const summary = reactive({ positive_ratio: 0, neutral_ratio: 0, negative_ratio: 0, avg_score: 0 })
const keywords = ref([])
const suggestions = ref([])
const samples = ref([])

onMounted(() => loadData())

async function loadData() {
  loading.value = true
  let trendData = []
  try {
    const days = parseInt(dateRange.value)
    const [sumRes, trendRes, kwRes, sugRes, samRes] = await Promise.all([
      api.getSummary(),
      api.getEmotionTrend(days),
      api.getKeywords(),
      api.getSuggestions(),
      api.getConversationSamples(),
    ])
    if (sumRes.code === 200) Object.assign(summary, sumRes.data)
    if (kwRes.code === 200) keywords.value = kwRes.data
    if (sugRes.code === 200) suggestions.value = sugRes.data
    if (samRes.code === 200) samples.value = samRes.data
    if (trendRes.code === 200) trendData = trendRes.data
  } catch (e) {
    console.warn('Analytics load failed:', e)
  } finally {
    loading.value = false
    await nextTick()
    drawChart(trendData)
  }
}

function drawChart(data) {
  if (!emotionChartRef.value || !data?.length) return
  const labels = data.map(d => d.date)
  const positive = data.map(d => d.positive)
  const neutral = data.map(d => d.neutral)
  const negative = data.map(d => d.negative)

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  const w = emotionChartRef.value.clientWidth || 500, h = 250
  svg.setAttribute('width', w); svg.setAttribute('height', h); svg.setAttribute('viewBox', `0 0 ${w} ${h}`)
  const pad = { top: 10, right: 10, bottom: 30, left: 50 }
  const cw = w - pad.left - pad.right, ch = h - pad.top - pad.bottom
  const gap = cw / labels.length, barW = gap * 0.6
  const maxVal = 100

  labels.forEach((label, i) => {
    const x = pad.left + i * gap + (gap - barW) / 2
    let y = pad.top + ch
    const draw = (val, color) => {
      const bh = (val / maxVal) * ch
      const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      r.setAttribute('x', x); r.setAttribute('y', y - bh); r.setAttribute('width', barW); r.setAttribute('height', bh)
      r.setAttribute('fill', color); r.setAttribute('rx', '3')
      svg.appendChild(r)
      y -= bh
    }
    draw(negative[i] || 0, '#EF4444'); draw(neutral[i] || 0, '#F59E0B'); draw(positive[i] || 0, '#4F6CF7')
    const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    txt.setAttribute('x', x + barW / 2); txt.setAttribute('y', h - 5); txt.setAttribute('text-anchor', 'middle')
    txt.setAttribute('font-size', '11'); txt.setAttribute('fill', '#94A3B8'); txt.textContent = label
    svg.appendChild(txt)
  })

  for (let v = 0; v <= 100; v += 25) {
    const y = pad.top + ch - (v / maxVal) * ch
    const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    txt.setAttribute('x', pad.left - 8); txt.setAttribute('y', y + 4); txt.setAttribute('text-anchor', 'end')
    txt.setAttribute('font-size', '11'); txt.setAttribute('fill', '#94A3B8'); txt.textContent = v + '%'
    svg.appendChild(txt)
  }

  emotionChartRef.value.innerHTML = ''
  emotionChartRef.value.appendChild(svg)
}
</script>

<style scoped>
.analytics-view { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; }
.page-header h1 { font-size: 24px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 2px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.date-select { width: 120px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.summary-card { display: flex; align-items: center; gap: 14px; }
.summary-icon { font-size: 32px; }
.summary-data { flex: 1; display: flex; flex-direction: column; }
.summary-value { font-size: 28px; font-weight: 700; }
.summary-label { font-size: 13px; color: var(--text-secondary); }
.cols-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.cols-2 .card h3 { font-size: 16px; margin-bottom: 16px; }
.emotion-chart { width: 100%; height: 250px; }
.word-cloud { display: flex; flex-wrap: wrap; gap: 10px; padding: 8px; min-height: 240px; align-content: center; justify-content: center; }
.word-item { display: inline-block; padding: 4px 8px; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-weight: 500; }
.word-item:hover { transform: scale(1.1); background: #F1F5F9; }
.section-header { margin-bottom: 16px; }
.section-header h3 { font-size: 16px; }
.suggestions-list { display: flex; flex-direction: column; gap: 12px; }
.suggestion-item { display: flex; gap: 14px; padding: 14px 16px; background: #F8FAFC; border-radius: 10px; align-items: flex-start; }
.sug-icon { font-size: 24px; flex-shrink: 0; }
.sug-content { flex: 1; }
.sug-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.sug-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
.sug-urgency { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 12px; white-space: nowrap; flex-shrink: 0; }
.sug-urgency.high { background: #FEE2E2; color: #DC2626; }
.sug-urgency.medium { background: #FEF3C7; color: #D97706; }
.sug-urgency.low { background: #DCFCE7; color: #16A34A; }
.sample-list { display: flex; flex-direction: column; gap: 16px; }
.sample-item { padding: 14px; background: #F8FAFC; border-radius: 10px; }
.sample-q, .sample-a { margin-bottom: 8px; font-size: 14px; }
.sample-role { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-right: 8px; }
.sample-role.user { background: #DBEAFE; color: #2563EB; }
.sample-role.ai { background: #DCFCE7; color: #16A34A; }
</style>
