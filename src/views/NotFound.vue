<template>
  <div class="not-found">
    <div class="nf-content">
      <div class="nf-code">404</div>
      <div class="nf-title">页面未找到</div>
      <p class="nf-desc">您访问的页面不存在，请检查路径是否正确。</p>
      <div class="nf-actions">
        <router-link to="/chat" class="btn btn-primary">← 返回首页</router-link>
        <router-link to="/admin" class="btn btn-outline">管理后台</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
}
.nf-content { text-align: center; }
.nf-code {
  font-size: 96px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}
.nf-title { font-size: 24px; font-weight: 700; margin: 8px 0; }
.nf-desc { color: var(--text-secondary); margin-bottom: 24px; }
.nf-actions { display: flex; gap: 12px; justify-content: center; }
</style>
