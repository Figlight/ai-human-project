<template>
  <div class="conversations-view">
    <div class="page-header">
      <h1>📋 历史记录</h1>
      <p class="subtitle">查看您与AI导游的历史对话记录</p>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else-if="sessions.length">
      <div v-for="session in sessions" :key="session.id" class="date-group session-group">
        <div class="date-header session-header" @click="toggleSession(session)">
          <span class="session-icon">💬</span>
          <span class="date-label session-title">{{ session.title }}</span>
          <span class="session-time">{{ session.time }}</span>
          <span class="expand-icon">{{ session.expanded ? '▼' : '▶' }}</span>
        </div>
        <div v-show="session.expanded" class="group-items">
          <div v-if="session.loadingMessages" class="loading-messages">加载会话详情中...</div>
          <template v-else>
            <div class="session-actions" style="display: flex; justify-content: flex-end; gap: 8px; margin-bottom: 10px; padding: 10px 0 0;">
              <button class="btn btn-danger btn-sm" @click.stop="handleDeleteSession(session.id)">
                🗑️ 删除此会话
              </button>
              <button class="btn btn-primary btn-sm" @click="continueConversation(session.id)">
                💬 进入并继续此会话
              </button>
            </div>
            <div v-for="msg in session.messages" :key="msg.id" class="conversation-item card" :class="msg.role">
              <div class="conv-role">{{ msg.role === 'user' ? '🙋 我' : '🤖 小导' }}</div>
              <div class="conv-text">{{ msg.content }}</div>
              <div class="conv-time">{{ msg.time }}</div>
            </div>
          </template>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <div class="empty-icon">💬</div>
      <p>暂无对话记录</p>
      <router-link to="/chat" class="btn btn-primary">开始对话 →</router-link>
    </div>

    <!-- Custom Glassmorphic Confirm Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="confirm-modal card">
        <div class="confirm-header">
          <span class="confirm-icon">⚠️</span>
          <h3>确认删除此对话记录吗？</h3>
        </div>
        <div class="confirm-body">
          <p>删除后将无法恢复，您将无法再查看或继续该对话内容。</p>
        </div>
        <div class="confirm-actions">
          <button class="btn btn-outline" @click="showConfirmModal = false">取消</button>
          <button class="btn btn-danger" @click="confirmDeleteSession">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api.js'

const router = useRouter()
const sessions = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.getSessions()
    if (res.code === 200 && res.data) {
      sessions.value = res.data.map(s => ({
        ...s,
        messages: [],
        messagesLoaded: false,
        expanded: false,
        loadingMessages: false
      }))
    }
  } catch (e) {
    console.warn('Failed to load sessions:', e)
  } finally {
    loading.value = false
  }
})

async function toggleSession(session) {
  session.expanded = !session.expanded
  if (session.expanded && !session.messagesLoaded) {
    session.loadingMessages = true
    try {
      const res = await api.getHistory(session.id)
      if (res.code === 200 && res.data) {
        session.messages = res.data
        session.messagesLoaded = true
      }
    } catch (e) {
      console.warn('Failed to load session history:', e)
    } finally {
      session.loadingMessages = false
    }
  }
}

function continueConversation(sessionId) {
  router.push({ path: '/chat', query: { session_id: sessionId } })
}

const showConfirmModal = ref(false)
const sessionToDelete = ref(null)

function handleDeleteSession(sessionId) {
  sessionToDelete.value = sessionId
  showConfirmModal.value = true
}

async function confirmDeleteSession() {
  if (sessionToDelete.value === null) return
  try {
    const res = await api.deleteSession(sessionToDelete.value)
    if (res.code === 200) {
      sessions.value = sessions.value.filter(s => s.id !== sessionToDelete.value)
    }
  } catch (e) {
    console.warn('Failed to delete session:', e)
  } finally {
    showConfirmModal.value = false
    sessionToDelete.value = null
  }
}
</script>

<style scoped>
.conversations-view { display: flex; flex-direction: column; gap: 16px; }
.page-header h1 { font-size: 24px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 4px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.empty-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.date-group { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.session-group { margin-bottom: 12px; }
.date-header { display: flex; align-items: center; padding: 14px 20px; cursor: pointer; user-select: none; }
.date-header:hover { background: #F8FAFC; }
.session-icon { font-size: 16px; margin-right: 10px; }
.date-label { font-weight: 600; font-size: 15px; flex: 1; }
.session-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 60%; }
.session-time { font-size: 13px; color: var(--text-secondary); margin-right: 16px; }
.expand-icon { color: var(--text-secondary); font-size: 12px; }
.group-items { padding: 0 16px 16px; display: flex; flex-direction: column; gap: 8px; }
.loading-messages { text-align: center; padding: 20px; color: var(--text-secondary); font-size: 13px; }
.conversation-item { padding: 14px 16px; }
.conversation-item.user { border-left: 3px solid var(--primary); }
.conversation-item.assistant { border-left: 3px solid #10B981; }
.conv-role { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; }
.conv-text { font-size: 14px; line-height: 1.7; white-space: pre-wrap; }
.conv-time { font-size: 11px; color: var(--text-secondary); margin-top: 6px; text-align: right; }
.btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; cursor: pointer; }

/* Custom Confirm Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.25s ease-out;
}

.confirm-modal {
  width: 400px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: scaleUp 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.confirm-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 12px;
}

.confirm-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.confirm-modal h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}

.confirm-body {
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.6;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  width: 100%;
}

.confirm-actions .btn {
  flex: 1;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-actions .btn-outline {
  border: 1px solid var(--border);
  background: white;
  color: var(--text-secondary);
}

.confirm-actions .btn-outline:hover {
  background: #F8FAFC;
  color: var(--text);
}

.confirm-actions .btn-danger {
  background: #EF4444;
  color: white;
  border: none;
}

.confirm-actions .btn-danger:hover {
  background: #DC2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
