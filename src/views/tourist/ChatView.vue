<template>
  <div class="chat-view">
    <div class="chat-layout">
      <div class="digital-human-panel">
        <DigitalHumanAvatar
          :state="digitalHumanState"
          :emotion="currentEmotion"
          :name="digitalHumanConfig.name"
          :title="digitalHumanConfig.title"
          :outfitColor="digitalHumanConfig.outfit_color"
          :characterId="digitalHumanConfig.character_id"
          :volume="audioVolume"
        />



        <div class="interaction-hints">
          <button class="btn btn-primary new-chat-btn" @click="handleNewChat" style="width: 100%; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; gap: 6px;">
            <span>➕</span> 新建会话
          </button>
          <div class="hint-item" v-for="hint in hints" :key="hint" @click="sendHint(hint)">
            {{ hint }}
          </div>
        </div>
      </div>

      <div class="chat-panel">
        <div class="chat-messages" ref="messagesRef">
          <div class="welcome-msg" v-if="messages.length === 0">
            <div class="welcome-icon">🏔️</div>
            <div class="welcome-title">欢迎来到景区智能导览</div>
            <div class="welcome-desc">我是AI导游小导，您可以问我关于景点的任何问题，也可以使用语音或拍照输入。</div>
          </div>
          <ChatBubble
            v-for="msg in messages"
            :key="msg.id"
            :text="msg.text"
            :role="msg.role"
            :emotion="msg.emotion"
            :time="msg.time"
            @replay="handleReplayAudio"
          />
        </div>

        <div class="chat-input-area">
          <div class="input-row">
            <!-- 拍照识别功能：暂作为后续课设新增需求储备，当前先隐藏 -->
            <!-- <button class="action-btn camera-btn" title="拍照识别" @click="takePhoto">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </button> -->
            <input
              v-model="inputText"
              class="input-field chat-input"
              placeholder="输入您的问题..."
              @keyup.enter="sendText"
            />
            <button class="action-btn send-btn" :disabled="!inputText.trim() || loading" @click="sendText">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
          <div class="input-extras">
            <VoiceInput @voice-start="onVoiceStart" @voice-end="onVoiceEnd" />
            <button class="action-btn gps-btn" @click="toggleGPS">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="10" r="3"/>
                <path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 7 8 11.7z"/>
              </svg>
              <span class="gps-text">定位 {{ gpsActive ? '已开启' : '未开启' }}</span>
            </button>
            <button class="action-btn feedback-toggle-btn" @click="showFeedbackModal = true" title="评价服务">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              <span class="gps-text">评价服务</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- 拍照识别隐藏 input：暂隐藏 -->
    <!-- <input ref="photoInput" type="file" accept="image/*" capture="environment" style="display:none" @change="onPhotoTaken" /> -->

    <!-- Feedback Modal -->
    <div v-if="showFeedbackModal" class="modal-overlay" @click.self="showFeedbackModal = false">
      <div class="feedback-modal card">
        <h3>⭐ 导览服务评价</h3>
        <p class="feedback-desc">您的反馈将直接帮助我们提升景区导览服务质量</p>
        
        <div class="rating-stars">
          <span
            v-for="star in 5"
            :key="star"
            class="star"
            :class="{ active: star <= feedbackRating }"
            @click="feedbackRating = star"
          >★</span>
        </div>
        
        <textarea
          v-model="feedbackSuggestion"
          class="feedback-input"
          rows="4"
          placeholder="说说您的建议，或者有什么地方可以改进..."
        ></textarea>
        
        <div class="feedback-actions">
          <button class="btn btn-outline" @click="showFeedbackModal = false">取消</button>
          <button class="btn btn-primary" :disabled="submittingFeedback" @click="submitFeedback">
            {{ submittingFeedback ? '提交中...' : '提交反馈' }}
          </button>
        </div>
        
        <div v-if="feedbackMsg" class="feedback-msg" :class="feedbackMsg.type">
          {{ feedbackMsg.text }}
        </div>
      </div>
    </div>

    <!-- Glassmorphic Preference Modal -->
    <div v-if="showPreferenceModal" class="preference-overlay">
      <div class="preference-modal">
        <div class="pref-title-glow">🌟</div>
        <h2 class="pref-title">定制您的专属讲解重点</h2>
        <p class="pref-desc">选择您的兴趣偏好，AI导游将为您定制专属的讲解重点与推荐路线</p>
        
        <div class="pref-options-grid">
          <div
            v-for="opt in prefOptions"
            :key="opt.key"
            class="pref-option-card"
            :class="{ selected: selectedModalPreference === opt.key }"
            @click="selectedModalPreference = opt.key"
          >
            <span class="pref-icon">{{ opt.icon }}</span>
            <span class="pref-label">{{ opt.label }}</span>
            <span class="pref-sub-desc">{{ opt.desc }}</span>
          </div>
        </div>
        
        <button
          class="btn btn-primary start-tour-btn"
          :disabled="!selectedModalPreference"
          @click="savePreference(selectedModalPreference)"
        >
          开启专属导览之旅 ✨
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import DigitalHumanAvatar from '../../components/DigitalHumanAvatar.vue'
import VoiceInput from '../../components/VoiceInput.vue'
import ChatBubble from '../../components/ChatBubble.vue'
import { api, getSessionId, startNewSession } from '../../api.js'

const route = useRoute()
const messagesRef = ref(null)
const inputText = ref('')
const photoInput = ref(null)
const digitalHumanState = ref('idle')
const currentEmotion = ref('neutral')
const gpsActive = ref(false)
const loading = ref(false)
const messages = ref([])
const sessionId = ref('')
const digitalHumanConfig = ref({
  name: '小导',
  title: '智能导游',
  character_id: 'guide1',
  outfit_id: 'outfit1',
  outfit_color: 'linear-gradient(135deg, #4F6CF7, #8B5CF6)',
  speed: 1.0
})
let msgId = 0

// 兴趣讲解偏好状态
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
const showPreferenceModal = ref(false)
const selectedModalPreference = ref('')

const prefOptions = [
  { key: 'history', icon: '🏛️', label: '历史人文', desc: '探索古迹底蕴与历史典故故事' },
  { key: 'photo', icon: '📸', label: '打卡拍照', desc: '寻找绝美取景机位与拍摄时机' },
  { key: 'nature', icon: '🌸', label: '自然风光', desc: '漫步山水林海尽享治愈与放松' },
  { key: 'family', icon: '👨‍👩‍👧', label: '休闲亲子', desc: '舒适好走不累，寻找休息与游乐区' }
]

function savePreference(key) {
  if (!key) return
  activePreference.value = key
  localStorage.setItem(getPreferenceStorageKey(), key)
  showPreferenceModal.value = false
  
  const labels = {
    history: '历史人文',
    photo: '打卡拍照',
    nature: '自然风光',
    family: '休闲亲子'
  }
  const prefLabel = labels[key] || '默认游览'
  
  if (messages.value.length === 0) {
    inputText.value = `你好！我已经把游览偏好设置为【${prefLabel}】，请介绍一下你自己，并告诉我景区内有哪些值得关注的内容？`
    sendText()
  } else {
    addMessage(`已为您切换讲解重点为：✨【${prefLabel}】偏好。接下来的游览中，我将为您重点介绍相关内容。`, 'assistant')
  }
}

function selectPreference(key) {
  activePreference.value = key
  localStorage.setItem(getPreferenceStorageKey(), key)
  
  const labels = {
    history: '历史人文',
    photo: '打卡拍照',
    nature: '自然风光',
    family: '休闲亲子'
  }
  const prefLabel = labels[key] || '默认游览'
  addMessage(`已为您切换讲解重点为：✨【${prefLabel}】偏好。接下来的游览中，我将为您重点介绍相关内容。`, 'assistant')
}

function openPreferenceModal() {
  selectedModalPreference.value = activePreference.value
  showPreferenceModal.value = true
}
let audioCtx = null
let audioQueue = []
let currentSource = null
let currentMediaRecorder = null
let currentAudioStream = null
let audioChunks = []
let typingTimer = null

function typeTextIntoInput(text) {
  if (typingTimer) {
    clearInterval(typingTimer)
  }
  inputText.value = ''
  let index = 0
  typingTimer = setInterval(() => {
    if (index < text.length) {
      inputText.value += text[index]
      index++
    } else {
      clearInterval(typingTimer)
      typingTimer = null
    }
  }, 30)
}


const showFeedbackModal = ref(false)
const audioVolume = ref(0)
let analyserNode = null
let animationFrameId = null
const feedbackRating = ref(5)
const feedbackSuggestion = ref('')
const submittingFeedback = ref(false)
const feedbackMsg = ref(null)

const hints = [
  '🏛️ 这个景区有哪些必看景点？',
  '📖 介绍一下这里的历史文化',
  '🗺️ 推荐一条半日游路线',
  '🌸 现在有什么花可以看？'
]

onBeforeUnmount(() => {
  stopAudio()
  window.removeEventListener('open-preference-modal', openPreferenceModal)
  if (currentAudioStream) {
    try {
      currentAudioStream.getTracks().forEach(t => t.stop())
    } catch {}
    currentAudioStream = null
  }
})

onMounted(async () => {
  window.addEventListener('open-preference-modal', openPreferenceModal)
  
  // 拉取数字人配置
  try {
    const [cfgRes, outfitRes] = await Promise.all([
      api.getConfig(),
      api.getOutfits()
    ])
    if (cfgRes.code === 200 && cfgRes.data) {
      digitalHumanConfig.value.name = cfgRes.data.name || '小导'
      digitalHumanConfig.value.title = cfgRes.data.title || '智能导游'
      digitalHumanConfig.value.character_id = cfgRes.data.character || 'guide1'
      digitalHumanConfig.value.outfit_id = cfgRes.data.outfit || 'outfit1'
      digitalHumanConfig.value.speed = cfgRes.data.speed || 1.0

      if (outfitRes.code === 200 && outfitRes.data) {
        const matchedOutfit = outfitRes.data.find(o => o.id === digitalHumanConfig.value.outfit_id)
        if (matchedOutfit) {
          digitalHumanConfig.value.outfit_color = matchedOutfit.color
        }
      }
    }
  } catch (e) {
    console.warn('Failed to load digital human config:', e)
  }

  // Set active preference value from storage key
  activePreference.value = localStorage.getItem(getPreferenceStorageKey()) || ''

  const querySid = route.query.session_id
  if (querySid) {
    sessionId.value = querySid
    sessionStorage.setItem('session_id', querySid)
  } else {
    try {
      const res = await api.getSessions()
      if (res.code === 200 && res.data && res.data.length > 0) {
        const validSession = res.data.find(s => s.id && s.id.trim() !== '')
        if (validSession) {
          sessionId.value = validSession.id
          sessionStorage.setItem('session_id', sessionId.value)
        } else {
          sessionId.value = startNewSession()
        }
      } else {
        sessionId.value = startNewSession()
      }
    } catch (e) {
      sessionId.value = getSessionId() || startNewSession()
    }
  }

  // Once sessionId is guaranteed to be set, show preference modal if activePreference is empty
  if (!activePreference.value) {
    showPreferenceModal.value = true
  }

  try {
    const res = await api.getHistory(sessionId.value)
    if (res.code === 200 && res.data?.length) {
      messages.value = res.data.map(m => ({
        id: ++msgId,
        text: m.content,
        role: m.role,
        emotion: m.emotion || '',
        time: m.time || '',
      }))
      scrollToBottom()
    }
  } catch (e) {
    console.warn('Failed to load history:', e)
  }

  // 提前申请并缓存麦克风通道，实现零录音启动延迟
  try {
    currentAudioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
  } catch (e) {
    console.warn('Microphone pre-initialization failed:', e)
  }
})

function handleNewChat() {
  stopAudio()
  sessionId.value = startNewSession()
  messages.value = []
  window.history.replaceState({}, document.title, '/chat')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function addMessage(text, role, emotion = '') {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  messages.value.push({ id: ++msgId, text, role, emotion, time })
  scrollToBottom()
}

function sendHint(text) {
  inputText.value = text
  sendText()
}

async function sendText() {
  if (typingTimer) {
    clearInterval(typingTimer)
    typingTimer = null
  }
  const text = inputText.value.trim()
  if (!text || loading.value) return
  stopAudio()
  ensureAudioCtx()
  addMessage(text, 'user')
  inputText.value = ''
  await doChat(text)
}

async function doChat(message) {
  loading.value = true
  digitalHumanState.value = 'thinking'
  currentEmotion.value = 'neutral'
  try {
    const response = await api.chatTextStream(message, sessionId.value, true, activePreference.value)
    if (!response.ok) {
      const res = await response.json()
      if (res.code === 200 && res.data) {
        currentEmotion.value = res.data.emotion || 'neutral'
        digitalHumanState.value = 'speaking'
        addMessage(res.data.reply, 'assistant', res.data.emotion)
        playAudio(res.data.audio_base64)
      } else {
        addMessage('抱歉，我暂时无法回答，请稍后再试。', 'assistant')
        digitalHumanState.value = 'idle'
      }
      loading.value = false
      return
    }

    const assistantId = ++msgId
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    messages.value.push({ id: assistantId, text: '', role: 'assistant', emotion: '', time })
    scrollToBottom()

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullReply = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'delta') {
            fullReply += data.text
            const msg = messages.value.find(m => m.id === assistantId)
            if (msg) msg.text = fullReply
            scrollToBottom()
          } else if (data.type === 'speech') {
            digitalHumanState.value = 'speaking'
            playAudio(data.audio_base64)
          } else if (data.type === 'done') {
            const msg = messages.value.find(m => m.id === assistantId)
            if (msg) {
              msg.text = data.reply
              msg.emotion = data.emotion || ''
            }
            currentEmotion.value = data.emotion || 'neutral'
          }
        }
      }
    }
  } catch (e) {
    addMessage('网络连接失败，请检查后端服务是否运行。', 'assistant')
    digitalHumanState.value = 'idle'
  } finally {
    loading.value = false
  }
}

function ensureAudioCtx() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    analyserNode = audioCtx.createAnalyser()
    analyserNode.fftSize = 256
    analyserNode.connect(audioCtx.destination)
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume()
  }
  return audioCtx
}

function stopAudio() {
  if (currentSource) {
    try { currentSource.stop() } catch {}
    currentSource = null
  }
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  audioVolume.value = 0
  audioQueue = []
  digitalHumanState.value = 'idle'
}

function updateVolumeMeter() {
  if (!analyserNode || digitalHumanState.value !== 'speaking') {
    audioVolume.value = 0
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }
    return
  }
  const array = new Uint8Array(analyserNode.frequencyBinCount)
  analyserNode.getByteFrequencyData(array)
  let sum = 0
  for (let i = 0; i < array.length; i++) {
    sum += array[i]
  }
  const average = sum / array.length
  audioVolume.value = Math.min(Math.round((average / 128) * 100), 100)
  animationFrameId = requestAnimationFrame(updateVolumeMeter)
}

function playQueuedAudio() {
  if (!audioQueue.length) {
    digitalHumanState.value = 'idle'
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }
    audioVolume.value = 0
    return
  }
  const buffer = audioQueue.shift()
  digitalHumanState.value = 'speaking'
  if (!animationFrameId) {
    animationFrameId = requestAnimationFrame(updateVolumeMeter)
  }
  try {
    currentSource = audioCtx.createBufferSource()
    currentSource.buffer = buffer
    currentSource.connect(analyserNode)
    currentSource.onended = () => {
      if (currentSource) playQueuedAudio()
    }
    currentSource.start()
  } catch (e) {
    console.warn('AudioBufferSource failed:', e)
    playQueuedAudio()
  }
}

async function handleReplayAudio(text) {
  stopAudio()
  digitalHumanState.value = 'speaking'
  try {
    const res = await api.synthesizeTTS(text)
    if (res.code === 200 && res.data?.audio_base64) {
      playAudio(res.data.audio_base64)
    } else {
      digitalHumanState.value = 'idle'
    }
  } catch (e) {
    console.warn('Failed to replay audio:', e)
    digitalHumanState.value = 'idle'
  }
}

async function playAudio(base64) {
  if (!base64) return
  try {
    const binary = atob(base64)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
    const ctx = ensureAudioCtx()
    const buffer = await ctx.decodeAudioData(bytes.buffer)
    audioQueue.push(buffer)
    if (audioQueue.length === 1) playQueuedAudio()
  } catch {
    try {
      const binary = atob(base64)
      const bytes = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
      const blob = new Blob([bytes], { type: 'audio/wav' })
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)
      audio.onended = () => { URL.revokeObjectURL(url) }
      audio.play()
    } catch (e) {
      console.warn('Audio fallback failed:', e)
    }
  }
}

async function onVoiceStart() {
  stopAudio()
  ensureAudioCtx()
  digitalHumanState.value = 'listening'
  audioChunks = []
  try {
    if (!currentAudioStream) {
      currentAudioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    }
    currentMediaRecorder = new MediaRecorder(currentAudioStream)
    currentMediaRecorder.ondataavailable = e => {
      if (e.data && e.data.size > 0) {
        audioChunks.push(e.data)
      }
    }
    currentMediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/wav' })
      digitalHumanState.value = 'thinking'
      try {
        const res = await api.transcribeVoice(blob)
        if (res.code === 200 && res.data) {
          const text = (res.data.text || '').trim()
          if (text) {
            typeTextIntoInput(text)
          } else {
            addMessage('未听清您说了什么，请重试。', 'assistant')
          }
        } else {
          addMessage('语音识别未成功，请重试。', 'assistant')
        }
      } catch (e) {
        addMessage('语音识别失败，请重试。', 'assistant')
      } finally {
        digitalHumanState.value = 'idle'
      }
    }
    currentMediaRecorder.start()
  } catch (e) {
    addMessage('无法访问麦克风，请检查权限。', 'assistant')
    digitalHumanState.value = 'idle'
  }
}

function onVoiceEnd() {
  if (currentMediaRecorder && currentMediaRecorder.state !== 'inactive') {
    currentMediaRecorder.stop()
  }
}

function takePhoto() {
  photoInput.value?.click()
}

async function onPhotoTaken(e) {
  const file = e.target.files?.[0]
  if (!file) return
  digitalHumanState.value = 'thinking'
  try {
    const base64 = await fileToBase64(file)
    const res = await api.chatImage(base64.replace(/^data:image\/\w+;base64,/, ''), sessionId.value, activePreference.value)
    if (res.code === 200 && res.data) {
      currentEmotion.value = res.data.emotion || 'neutral'
      digitalHumanState.value = 'speaking'
      addMessage(`📷 [图片识别] ${res.data.reply}`, 'assistant', res.data.emotion)
      playAudio(res.data.audio_base64)
      setTimeout(() => {
        if (digitalHumanState.value === 'speaking') digitalHumanState.value = 'idle'
      }, 2000)
    }
  } catch (e) {
    addMessage('图片识别失败。', 'assistant')
    digitalHumanState.value = 'idle'
  }
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function toggleGPS() {
  gpsActive.value = !gpsActive.value
  if (!gpsActive.value) return
  navigator.geolocation.getCurrentPosition(async pos => {
    try {
      const res = await api.reverseGeocode(pos.coords.latitude, pos.coords.longitude)
      if (res.code === 200 && res.data?.address) {
        addMessage(`📍 当前位置：${res.data.address}`, 'assistant')
      } else {
        addMessage(`📍 已获取位置（${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}）`, 'assistant')
      }
    } catch {
      addMessage(`📍 已获取位置（${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}）`, 'assistant')
    }
  }, () => {
    gpsActive.value = false
    addMessage('无法获取位置，请检查定位权限。', 'assistant')
  })
}

async function submitFeedback() {
  if (submittingFeedback.value) return
  submittingFeedback.value = true
  feedbackMsg.value = null
  try {
    const res = await api.submitFeedback(
      feedbackRating.value,
      feedbackSuggestion.value,
      sessionId.value
    )
    if (res.code === 200) {
      feedbackMsg.value = { type: 'success', text: '感谢您的评价！' }
      setTimeout(() => {
        showFeedbackModal.value = false
        feedbackSuggestion.value = ''
        feedbackRating.value = 5
        feedbackMsg.value = null
      }, 1500)
    } else {
      feedbackMsg.value = { type: 'error', text: '提交失败，请重试' }
    }
  } catch (e) {
    feedbackMsg.value = { type: 'error', text: '网络连接异常' }
  } finally {
    submittingFeedback.value = false
  }
}
</script>

<style scoped>
.chat-view { height: calc(100vh - 108px); }
.chat-layout { display: flex; gap: 24px; height: 100%; }
.digital-human-panel {
  width: 320px; flex-shrink: 0;
  background: white; border-radius: var(--radius); box-shadow: var(--shadow);
  padding: 32px 20px 24px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.interaction-hints { display: flex; flex-direction: column; gap: 8px; width: 100%; margin-top: 20px; }
.hint-item {
  padding: 10px 14px; border-radius: 10px;
  background: #F8FAFC; border: 1px solid var(--border);
  font-size: 13px; cursor: pointer; transition: all 0.2s; text-align: center;
}
.hint-item:hover { border-color: var(--primary); background: #EEF2FF; color: var(--primary); }
.chat-panel {
  flex: 1; display: flex; flex-direction: column;
  background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden;
}
.chat-messages { flex: 1; overflow-y: auto; padding: 24px; }
.welcome-msg {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; text-align: center; color: var(--text-secondary);
}
.welcome-icon { font-size: 48px; margin-bottom: 16px; }
.welcome-title { font-size: 20px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.welcome-desc { font-size: 14px; max-width: 400px; line-height: 1.7; }
.chat-input-area { border-top: 1px solid var(--border); padding: 16px 20px; background: #FAFBFC; }
.input-row { display: flex; gap: 10px; align-items: center; }
.chat-input { flex: 1; padding: 12px 16px; border-radius: 24px; font-size: 14px; }
.action-btn {
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: white; border: 1px solid var(--border);
  color: var(--text-secondary); transition: all 0.2s; flex-shrink: 0;
}
.action-btn:hover { border-color: var(--primary); color: var(--primary); }
.send-btn { background: var(--primary); color: white; border-color: var(--primary); }
.send-btn:hover { background: var(--primary-dark); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.camera-btn:hover { border-color: var(--success); color: var(--success); }
.input-extras { display: flex; align-items: center; gap: 12px; margin-top: 10px; padding-left: 4px; }
.gps-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 20px; width: auto; height: auto; font-size: 12px; font-weight: 500;
}
.gps-text { font-size: 12px; }

/* Feedback Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.feedback-modal {
  width: 400px;
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.feedback-modal h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}
.feedback-desc {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
  margin-top: 6px;
  margin-bottom: 20px;
}
.rating-stars {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.rating-stars .star {
  font-size: 36px;
  color: #E2E8F0;
  cursor: pointer;
  transition: color 0.15s;
}
.rating-stars .star.active {
  color: #F59E0B;
}
.feedback-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  margin-bottom: 20px;
  outline: none;
  transition: border-color 0.2s;
}
.feedback-input:focus {
  border-color: var(--primary);
}
.feedback-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  width: 100%;
}
.feedback-msg {
  margin-top: 14px;
  font-size: 13px;
  font-weight: 500;
  text-align: center;
}
.feedback-msg.success { color: #10B981; }
.feedback-msg.error { color: #EF4444; }

.feedback-toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  width: auto;
  height: auto;
  font-size: 12px;
  font-weight: 500;
}

/* Glassmorphic Preference Modal Styles */
.preference-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease-out;
}
.preference-modal {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1),
              inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  width: 90%;
  max-width: 600px;
  padding: 32px;
  text-align: center;
  animation: scaleUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.pref-title-glow {
  font-size: 40px;
  margin-bottom: 12px;
  animation: float 3s ease-in-out infinite;
}
.pref-title {
  font-size: 22px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 8px;
}
.pref-desc {
  font-size: 14px;
  color: #64748B;
  margin-bottom: 24px;
}
.pref-options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.pref-option-card {
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 20px 16px;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.01);
}
.pref-option-card:hover {
  background: rgba(255, 255, 255, 0.85);
  border-color: #6366F1;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.15);
  transform: translateY(-4px);
}
.pref-option-card.selected {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
  border-color: #6366F1;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
}
.pref-icon {
  font-size: 32px;
  margin-bottom: 4px;
}
.pref-label {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
}
.pref-sub-desc {
  font-size: 11px;
  color: #94A3B8;
  line-height: 1.4;
}
.start-tour-btn {
  width: 100%;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}
.start-tour-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}



@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes scaleUp {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
</style>
