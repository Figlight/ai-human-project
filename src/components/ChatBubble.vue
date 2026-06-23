<template>
  <div class="chat-bubble" :class="[role]">
    <div class="avatar-icon" v-if="role === 'assistant'">
      <span>🤖</span>
    </div>
    <div class="bubble-content">
      <div class="bubble" :class="{ emotion: role === 'assistant' && emotion }">
        <div v-if="role === 'assistant' && emotion" class="emotion-tag">{{ emotionText }}</div>
        <div class="message-text">{{ text }}</div>
      </div>
      <div class="bubble-meta">
        <span class="time">{{ time }}</span>
        <span v-if="role === 'assistant'" class="audio-indicator" @click="$emit('replay', text)">🔊</span>
      </div>
    </div>
    <div class="avatar-icon" v-if="role === 'user'">
      <span>👤</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: { type: String, required: true },
  role: { type: String, default: 'user' },
  emotion: { type: String, default: '' },
  time: { type: String, default: '' }
})

const emit = defineEmits(['replay'])

const emotionText = computed(() => {
  const map = { happy: '😊 高兴', surprised: '😮 惊讶', sad: '😢 遗憾', neutral: '😌 平和', excited: '🤩 热情' }
  return map[props.emotion] || ''
})
</script>

<style scoped>
.chat-bubble {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: flex-start;
}
.chat-bubble.user {
  flex-direction: row-reverse;
}
.avatar-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.assistant .avatar-icon { background: #EEF2FF; }
.user .avatar-icon { background: #FEF3C7; }

.bubble-content {
  max-width: 70%;
}
.bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  position: relative;
}
.assistant .bubble {
  background: white;
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}
.assistant .bubble.emotion {
  border-color: #C7D2FE;
  background: #F5F7FF;
}
.user .bubble {
  background: var(--primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.emotion-tag {
  font-size: 12px;
  color: var(--primary);
  margin-bottom: 6px;
  font-weight: 500;
}

.bubble-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  padding: 0 4px;
}
.time {
  font-size: 11px;
  color: var(--text-secondary);
}
.audio-indicator {
  font-size: 12px;
  cursor: pointer;
}
.user .bubble-meta {
  justify-content: flex-end;
}
.message-text {
  white-space: pre-wrap;
}
</style>
