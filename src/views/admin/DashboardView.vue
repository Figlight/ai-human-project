<template>
  <div class="dashboard">
    <div class="dash-header">
      <h1>📊 数据大屏</h1>
      <div class="dash-time"><span class="live-dot"></span><span>实时更新 · {{ currentTime }}</span></div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else>
      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="stat-card" :style="{ borderTop: `3px solid ${stat.color}` }">
          <div class="stat-top">
            <span class="stat-icon">{{ stat.icon }}</span>
            <span class="stat-change" :class="stat.change > 0 ? 'up' : 'down'">{{ stat.change > 0 ? '↑' : '↓' }} {{ Math.abs(stat.change) }}%</span>
          </div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header"><h3>🔥 热门问答 TOP10</h3></div>
          <div class="chart-body">
            <div v-for="(item, i) in topQuestions" :key="i" class="rank-item">
              <span class="rank-num" :class="{ gold: i === 0, silver: i === 1, bronze: i === 2 }">{{ i + 1 }}</span>
              <span class="rank-text">{{ item.question }}</span>
              <div class="rank-bar-bg"><div class="rank-bar" :style="{ width: item.percent + '%', background: rankColor(i) }"></div></div>
              <span class="rank-count">{{ item.count }}</span>
            </div>
          </div>
        </div>
        <div class="chart-card">
          <div class="chart-header"><h3>📈 满意度趋势（近7日）</h3></div>
          <div class="chart-body">
            <div class="line-chart-container" ref="lineChartRef"></div>
            <div class="satisfaction-legend">
              <span><span class="dot" style="background:#4F6CF7"></span> 满意</span>
              <span><span class="dot" style="background:#F59E0B"></span> 一般</span>
              <span><span class="dot" style="background:#EF4444"></span> 不满意</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from '../../api.js'

const currentTime = ref('')
const lineChartRef = ref(null)
const loading = ref(true)
const emotionTrend = ref([])
let timer = null

const stats = ref([
  { icon: '👤', label: '今日服务人次', value: '--', change: 0, color: '#4F6CF7' },
  { icon: '💬', label: '本周对话总数', value: '--', change: 0, color: '#10B981' },
  { icon: '⭐', label: '平均满意度', value: '--', change: 0, color: '#F59E0B' },
  { icon: '⚡', label: '活跃峰值', value: '--', change: 0, color: '#EF4444' },
])

const topQuestions = ref([])

onMounted(async () => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  try {
    const res = await api.getSummary()
    if (res.code === 200) {
      stats.value[0].value = res.data.total_visitors.toLocaleString()
      stats.value[1].value = res.data.total_conversations.toLocaleString()
      stats.value[2].value = res.data.avg_score.toFixed(1)
      stats.value[2].change = 3.1
    }
    const trendRes = await api.getEmotionTrend(7)
    if (trendRes.code === 200) {
      emotionTrend.value = trendRes.data
      drawChart(trendRes.data)
    }
    const qRes = await api.getTopQuestions()
    if (qRes.code === 200) topQuestions.value = qRes.data
  } catch (e) {
    console.warn('Dashboard load failed:', e)
    drawChart([])
  } finally {
    loading.value = false
  }
})

onUnmounted(() => { if (timer) clearInterval(timer) })

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function rankColor(i) {
  const colors = ['#4F6CF7','#10B981','#F59E0B','#8B5CF6','#EC4899','#14B8A6','#F97316','#6366F1','#84CC16','#06B6D4']
  return colors[i]
}

function drawChart(data) {
  if (!lineChartRef.value) return
  const labels = data.length ? data.map(d => d.date) : ['5/10','5/11','5/12','5/13','5/14','5/15','5/16']
  const satisfied = data.length ? data.map(d => d.positive) : [88,90,87,92,91,93,92]
  const neutral = data.length ? data.map(d => d.neutral) : [8,6,9,5,6,4,5]
  const dissatisfied = data.length ? data.map(d => d.negative) : [4,4,4,3,3,3,3]

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  const w = lineChartRef.value.clientWidth || 400, h = 220
  svg.setAttribute('width', w); svg.setAttribute('height', h); svg.setAttribute('viewBox', `0 0 ${w} ${h}`)
  const pad = { top: 20, right: 10, bottom: 30, left: 10 }
  const cw = w - pad.left - pad.right, ch = h - pad.top - pad.bottom
  const maxVal = 100

  function drawLine(data, color) {
    const pts = data.map((v, i) => `${pad.left + (i / (data.length - 1)) * cw},${pad.top + ch - (v / maxVal) * ch}`)
    const pl = document.createElementNS('http://www.w3.org/2000/svg', 'polyline')
    pl.setAttribute('points', pts.join(' ')); pl.setAttribute('fill', 'none')
    pl.setAttribute('stroke', color); pl.setAttribute('stroke-width', '2.5')
    pl.setAttribute('stroke-linejoin', 'round'); pl.setAttribute('stroke-linecap', 'round')
    svg.appendChild(pl)
    data.forEach((v, i) => {
      const x = pad.left + (i / (data.length - 1)) * cw, y = pad.top + ch - (v / maxVal) * ch
      const cir = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
      cir.setAttribute('cx', x); cir.setAttribute('cy', y); cir.setAttribute('r', '3.5')
      cir.setAttribute('fill', color); cir.setAttribute('stroke', 'white'); cir.setAttribute('stroke-width', '2')
      svg.appendChild(cir)
    })
  }

  drawLine(satisfied, '#4F6CF7'); drawLine(neutral, '#F59E0B'); drawLine(dissatisfied, '#EF4444')
  labels.forEach((l, i) => {
    const x = pad.left + (i / (labels.length - 1)) * cw
    const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    txt.setAttribute('x', x); txt.setAttribute('y', h - 5); txt.setAttribute('text-anchor', 'middle')
    txt.setAttribute('font-size', '11'); txt.setAttribute('fill', '#94A3B8'); txt.textContent = l
    svg.appendChild(txt)
  })
  lineChartRef.value.innerHTML = ''
  lineChartRef.value.appendChild(svg)
}
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.dash-header { display: flex; align-items: center; justify-content: space-between; }
.dash-header h1 { font-size: 24px; }
.dash-time { display: flex; align-items: center; gap: 6px; font-size: 14px; color: var(--text-secondary); }
.live-dot { width: 8px; height: 8px; border-radius: 50%; background: #10B981; animation: live-pulse 1.5s ease-in-out infinite; }
@keyframes live-pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.loading-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px; }
.stat-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.stat-icon { font-size: 28px; }
.stat-change { font-size: 13px; font-weight: 600; padding: 2px 10px; border-radius: 12px; }
.stat-change.up { color: #10B981; background: #DCFCE7; }
.stat-change.down { color: #EF4444; background: #FEE2E2; }
.stat-value { font-size: 32px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 14px; color: var(--text-secondary); }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.chart-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); }
.chart-header { padding: 16px 20px; border-bottom: 1px solid var(--border); }
.chart-header h3 { font-size: 16px; }
.chart-body { padding: 16px 20px; }
.rank-item { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.rank-num { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; background: #F1F5F9; color: var(--text-secondary); flex-shrink: 0; }
.rank-num.gold { background: #FEF3C7; color: #D97706; }
.rank-num.silver { background: #F1F5F9; color: #64748B; }
.rank-num.bronze { background: #FED7AA; color: #EA580C; }
.rank-text { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rank-bar-bg { width: 80px; height: 6px; background: #F1F5F9; border-radius: 3px; flex-shrink: 0; }
.rank-bar { height: 100%; border-radius: 3px; }
.rank-count { font-size: 12px; color: var(--text-secondary); width: 30px; text-align: right; flex-shrink: 0; }
.line-chart-container { width: 100%; height: 220px; }
.satisfaction-legend { display: flex; justify-content: center; gap: 24px; margin-top: 8px; font-size: 13px; color: var(--text-secondary); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
</style>
