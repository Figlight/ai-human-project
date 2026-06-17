<template>
  <div class="app" :class="layout">
    <!-- Tourist Header -->
    <header v-if="layout === 'tourist'" class="tourist-header">
      <div class="header-inner">
        <div class="header-left">
          <span class="logo-icon">🏔️</span>
          <span class="logo-text">景区导览AI数字人</span>
        </div>
        <nav class="header-nav">
          <router-link to="/chat" class="nav-item" active-class="active">
            <span>💬</span> AI对话
          </router-link>
          <router-link to="/attractions" class="nav-item" active-class="active">
            <span>🗺️</span> 景点路线
          </router-link>
          <router-link to="/conversations" class="nav-item" active-class="active">
            <span>📋</span> 历史记录
          </router-link>
        </nav>
        <div class="header-right">
          <router-link to="/admin" class="btn btn-outline" style="font-size:13px;padding:6px 16px;">
            ⚙️ 管理后台
          </router-link>
        </div>
      </div>
    </header>

    <!-- Admin Layout -->
    <template v-else-if="layout === 'admin'">
      <AdminSidebar />
      <main class="admin-main">
        <router-view />
      </main>
    </template>

    <!-- Tourist Main -->
    <main v-if="layout === 'tourist'" class="tourist-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminSidebar from './components/AdminSidebar.vue'

const route = useRoute()
const layout = computed(() => route.meta?.layout || 'tourist')
</script>

<style scoped>
.app {
  min-height: 100vh;
}

/* Tourist Layout */
.tourist-header {
  background: white;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-icon { font-size: 24px; }
.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.header-nav {
  display: flex;
  gap: 4px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}
.nav-item:hover {
  background: #F1F5F9;
  color: var(--text);
}
.nav-item.active {
  background: #EEF2FF;
  color: var(--primary);
}
.tourist-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 60px);
}

/* Admin Layout */
.admin-main {
  margin-left: 240px;
  padding: 24px 32px;
  min-height: 100vh;
  background: var(--bg);
}
</style>
