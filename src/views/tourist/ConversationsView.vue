<template>
  <div class="conversations-view">
    <div class="page-header">
      <h1>📋 历史记录</h1>
      <p class="subtitle">查看您与AI导游的历史对话记录</p>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else-if="groupedConversations.length">
      <div v-for="group in groupedConversations" :key="group.date" class="date-group">
        <div class="date-header" @click="group.expanded = !group.expanded">
          <span class="date-label">{{ group.date }}</span>
          <span class="date-count">{{ group.items.length }} 条消息</span>
          <span class="expand-icon">{{ group.expanded ? '▼' : '▶' }}</span>
        </div>
        <div v-show="group.expanded" class="group-items">
          <div v-for="msg in group.items" :key="msg.id" class="conversation-item card" :class="msg.role">
            <div class="conv-role">{{ msg.role === 'user' ? '🙋 我' : '🤖 小导' }}</div>
            <div class="conv-text">{{ msg.content }}</div>
            <div class="conv-time">{{ msg.time }}</div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <div class="empty-icon">💬</div>
      <p>暂无对话记录</p>
      <router-link to="/chat" class="btn btn-primary">开始对话 →</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api, getSessionId } from '../../api.js'

const history = ref([])
const loading = ref(true)
const sessionId = getSessionId()

onMounted(async () => {
  try {
    const res = await api.getHistory(sessionId)
    if (res.code === 200) history.value = res.data || []
  } catch (e) {
    console.warn('Failed to load history:', e)
  } finally {
    loading.value = false
  }
})

const groupedConversations = computed(() => {
  if (!history.value.length) return []
  const groups = {}
  history.value.forEach(msg => {
    const date = msg.time || '今天'
    if (!groups[date]) groups[date] = { date, expanded: true, items: [] }
    groups[date].items.push(msg)
  })
  return Object.values(groups)
})
</script>

<style scoped>
.conversations-view { display: flex; flex-direction: column; gap: 16px; }
.page-header h1 { font-size: 24px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 4px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.empty-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.date-group { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.date-header { display: flex; align-items: center; padding: 14px 20px; cursor: pointer; user-select: none; }
.date-header:hover { background: #F8FAFC; }
.date-label { font-weight: 600; font-size: 15px; flex: 1; }
.date-count { font-size: 13px; color: var(--text-secondary); margin-right: 12px; }
.expand-icon { color: var(--text-secondary); font-size: 12px; }
.group-items { padding: 0 16px 16px; display: flex; flex-direction: column; gap: 8px; }
.conversation-item { padding: 14px 16px; }
.conversation-item.user { border-left: 3px solid var(--primary); }
.conversation-item.assistant { border-left: 3px solid #10B981; }
.conv-role { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; }
.conv-text { font-size: 14px; line-height: 1.7; }
.conv-time { font-size: 11px; color: var(--text-secondary); margin-top: 6px; text-align: right; }
</style>
