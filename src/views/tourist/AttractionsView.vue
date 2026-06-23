<template>
  <div class="attractions-view">
    <div class="page-header">
      <h1>🗺️ 景点与路线</h1>
      <p class="subtitle">选择您感兴趣的主题，为您推荐最佳游览路线</p>
    </div>

    <div class="tags-section">
      <div class="section-label">选择兴趣标签</div>
      <div class="tags-row">
        <span v-for="tag in tags" :key="tag.key" class="tag" :class="{ active: selectedTags.includes(tag.key) }" @click="toggleTag(tag.key)">
          {{ tag.icon }} {{ tag.label }}
        </span>
      </div>
      <button class="btn btn-primary recommend-btn" @click="recommendRoutes">✨ 推荐路线</button>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-if="routes.length && !loading" class="routes-section">
      <div class="section-header">
        <h2>推荐路线</h2>
        <span class="route-count">{{ routes.length }} 条</span>
      </div>
      <div class="routes-grid">
        <div v-for="route in routes" :key="route.id" class="route-card card" :class="{ highlighted: isRouteMatchingPreference(route) }" @click="selectRoute(route)">
          <div class="route-badge" :style="{ background: route.color }">{{ route.duration }}</div>
          <h3 class="route-name">{{ route.name }}</h3>
          <p class="route-desc">{{ route.description }}</p>
          <div class="route-spots">
            <span v-for="spot in route.spots" :key="spot" class="spot-tag">{{ spot }}</span>
          </div>
          <div class="route-meta">
            <span>📏 {{ route.distance }}</span>
            <span>⏱️ {{ route.time }}</span>
            <span>{{ route.tag }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedRoute" class="route-detail card">
      <div class="detail-header">
        <h2>{{ selectedRoute.name }}</h2>
        <button class="btn btn-outline" @click="selectedRoute = null">收起</button>
      </div>
      <div class="detail-timeline">
        <div v-for="(spot, i) in selectedRoute.spots" :key="spot" class="timeline-item">
          <div class="timeline-dot" :style="{ background: selectedRoute.color }">{{ i + 1 }}</div>
          <div class="timeline-content">
            <h4>{{ spot }}</h4>
            <p>{{ spotDescriptions[spot] || '敬请期待详细讲解...' }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="all-attractions">
      <div class="section-header">
        <h2>全部景点</h2>
        <span class="attraction-count">{{ attractions.length }} 个</span>
      </div>
      <div class="attractions-grid">
        <div v-for="item in attractions" :key="item.name" class="attraction-card card">
          <div class="attraction-img" :style="{ background: item.color }"><span class="img-icon">{{ item.icon }}</span></div>
          <div class="attraction-info">
            <h3>{{ item.name }}</h3>
            <p>{{ item.description }}</p>
            <div class="attraction-tags">
              <span class="tag" v-for="t in item.tags" :key="t">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api.js'

const tags = ref([])
const attractions = ref([])
const routes = ref([])
const selectedTags = ref([])
const selectedRoute = ref(null)
const spotDescriptions = ref({})
const loading = ref(false)

function getUserId() {
  try {
    const userUserStr = sessionStorage.getItem('user_user')
    const userUser = userUserStr ? JSON.parse(userUserStr) : null
    return userUser ? userUser.id : 'anonymous'
  } catch (e) {
    return 'anonymous'
  }
}

function getPreferenceStorageKey() {
  return `visitor_preference_${getUserId()}`
}

const activePreference = ref('')

onMounted(async () => {
  activePreference.value = localStorage.getItem(getPreferenceStorageKey()) || ''
  try {
    const [tagRes, attrRes, routeRes] = await Promise.all([
      api.listTags(), api.listAttractions(), api.listRoutes(),
    ])
    if (tagRes.code === 200) tags.value = tagRes.data
    if (attrRes.code === 200) attractions.value = attrRes.data
    if (routeRes.code === 200) routes.value = routeRes.data
    
    // 初始化同步偏好标签
    if (activePreference.value) {
      selectedTags.value = [activePreference.value]
      await recommendRoutes()
    }
  } catch (e) {
    console.warn('Failed to load attractions data:', e)
  }
})

function toggleTag(key) {
  if (activePreference.value === key) {
    activePreference.value = ''
    selectedTags.value = []
    localStorage.removeItem(getPreferenceStorageKey())
  } else {
    activePreference.value = key
    selectedTags.value = [key]
    localStorage.setItem(getPreferenceStorageKey(), key)
  }
  recommendRoutes()
}

async function selectRoute(route) {
  selectedRoute.value = route
  const descs = {}
  for (const spot of route.spots) {
    try {
      const res = await api.getSpotDescription(spot)
      if (res.code === 200) descs[spot] = res.data.description
    } catch (_) {}
  }
  spotDescriptions.value = descs
}

async function recommendRoutes() {
  if (!selectedTags.value.length) {
    try {
      const res = await api.listRoutes()
      if (res.code === 200) routes.value = res.data
    } catch (_) {}
    return
  }
  loading.value = true
  try {
    const res = await api.recommendRoutes(selectedTags.value)
    if (res.code === 200) routes.value = res.data
  } catch (e) {
    console.warn('Recommend failed:', e)
  } finally {
    loading.value = false
  }
}

function isRouteMatchingPreference(route) {
  if (!activePreference.value) return false
  // 历史人文 (history) -> 路线 1
  // 自然风光 (nature) -> 路线 2
  // 休闲亲子 (family) -> 路线 3
  // 打卡拍照 (photo) -> 路线 1, 2
  if (activePreference.value === 'history' && route.id === 1) return true
  if (activePreference.value === 'nature' && route.id === 2) return true
  if (activePreference.value === 'family' && route.id === 3) return true
  if (activePreference.value === 'photo' && (route.id === 1 || route.id === 2)) return true
  return false
}
</script>

<style scoped>
.attractions-view { display: flex; flex-direction: column; gap: 24px; }
.page-header h1 { font-size: 24px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 4px; }
.tags-section { background: white; border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px 24px; }
.section-label { font-size: 14px; font-weight: 600; margin-bottom: 12px; }
.tags-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.recommend-btn { width: 100%; }
.loading-state { text-align: center; padding: 40px; color: var(--text-secondary); }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h2 { font-size: 18px; }
.route-count, .attraction-count { color: var(--text-secondary); font-size: 14px; }
.routes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.route-card { cursor: pointer; transition: all 0.25s ease; border: 1px solid var(--border); }
.route-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.route-card.highlighted {
  border: 2px solid var(--primary);
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.15), 0 0 12px rgba(99, 102, 241, 0.08);
  position: relative;
  overflow: hidden;
}
.route-card.highlighted::before {
  content: '✨ 偏好首选';
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 20px;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
  z-index: 2;
}
.route-badge { display: inline-block; padding: 3px 12px; border-radius: 12px; color: white; font-size: 12px; font-weight: 600; margin-bottom: 8px; }
.route-name { font-size: 17px; margin-bottom: 6px; }
.route-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 10px; }
.route-spots { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.spot-tag { padding: 2px 10px; background: #F1F5F9; border-radius: 12px; font-size: 12px; color: var(--text-secondary); }
.route-meta { display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary); }
.route-detail { margin-top: 8px; }
.detail-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.detail-header h2 { font-size: 18px; }
.timeline-item { display: flex; gap: 16px; padding-bottom: 24px; position: relative; }
.timeline-item:not(:last-child)::before { content: ''; position: absolute; left: 18px; top: 36px; bottom: 0; width: 2px; background: var(--border); }
.timeline-dot { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px; flex-shrink: 0; }
.timeline-content h4 { font-size: 15px; margin-bottom: 4px; }
.timeline-content p { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
.attractions-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.attraction-card { overflow: hidden; }
.attraction-img { height: 120px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
.img-icon { font-size: 40px; }
.attraction-info h3 { font-size: 16px; margin-bottom: 4px; }
.attraction-info p { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.attraction-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.attraction-tags .tag { font-size: 11px; padding: 2px 10px; cursor: default; }
</style>
