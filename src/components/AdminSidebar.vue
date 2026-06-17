<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <span>🏔️</span>
        <span>管理后台</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="sidebar-item"
        active-class="active"
      >
        <span class="sidebar-icon">{{ item.icon }}</span>
        <span class="sidebar-label">{{ item.label }}</span>
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <router-link to="/chat" class="btn btn-outline back-btn">
        ← 返回游客端
      </router-link>
    </div>
  </aside>
</template>

<script setup>
const menuItems = [
  { path: '/admin', icon: '📊', label: '数据大屏' },
  { path: '/admin/knowledge', icon: '📚', label: '知识库管理' },
  { path: '/admin/digital-human', icon: '🤖', label: '数字人配置' },
  { path: '/admin/analytics', icon: '📈', label: '游客洞察' }
]
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  background: var(--bg-dark);
  color: white;
  display: flex;
  flex-direction: column;
  z-index: 200;
}
.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
}
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255,255,255,0.6);
  transition: all 0.2s;
}
.sidebar-item:hover {
  background: rgba(255,255,255,0.06);
  color: white;
}
.sidebar-item.active {
  background: rgba(79,108,247,0.2);
  color: #7B93FA;
}
.sidebar-icon { font-size: 20px; }
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.back-btn {
  width: 100%;
  font-size: 13px;
  padding: 8px;
  color: rgba(255,255,255,0.5);
  border-color: rgba(255,255,255,0.15);
}
.back-btn:hover {
  color: white;
  border-color: rgba(255,255,255,0.3);
}
</style>
