<template>
  <button
    class="voice-btn"
    :class="{ recording: isRecording }"
    @mousedown="startRecording"
    @mouseup="stopRecording"
    @mouseleave="stopRecording"
    @touchstart.prevent="startRecording"
    @touchend="stopRecording"
  >
    <div class="btn-inner">
      <svg v-if="!isRecording" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="22"/>
      </svg>
      <div v-else class="recording-icon">
        <div class="rec-bar" v-for="i in 5" :key="i"></div>
      </div>
    </div>
    <span class="voice-label">{{ isRecording ? '松手识别' : '按住说话' }}</span>
  </button>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['voice-start', 'voice-end'])
const isRecording = ref(false)

function startRecording() {
  isRecording.value = true
  emit('voice-start')
}

function stopRecording() {
  if (isRecording.value) {
    isRecording.value = false
    emit('voice-end')
  }
}
</script>

<style scoped>
.voice-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--card);
  border: 2px solid var(--border);
  transition: all 0.2s;
  min-width: 80px;
}
.voice-btn:hover {
  border-color: var(--primary);
  background: #EEF2FF;
}
.voice-btn.recording {
  border-color: var(--danger);
  background: #FEF2F2;
  animation: record-pulse 1s ease-in-out infinite;
}
@keyframes record-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.3); }
  50% { box-shadow: 0 0 0 12px rgba(239,68,68,0); }
}
.btn-inner {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}
.recording .btn-inner { color: var(--danger); }
.voice-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}
.recording .voice-label { color: var(--danger); }

.recording-icon {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 24px;
}
.rec-bar {
  width: 3px;
  background: var(--danger);
  border-radius: 2px;
  animation: rec-bar 0.4s ease-in-out infinite alternate;
}
.rec-bar:nth-child(1) { height: 10px; animation-delay: 0s; }
.rec-bar:nth-child(2) { height: 16px; animation-delay: 0.1s; }
.rec-bar:nth-child(3) { height: 22px; animation-delay: 0.2s; }
.rec-bar:nth-child(4) { height: 16px; animation-delay: 0.3s; }
.rec-bar:nth-child(5) { height: 10px; animation-delay: 0.4s; }
@keyframes rec-bar {
  0% { transform: scaleY(0.5); }
  100% { transform: scaleY(1); }
}
</style>
