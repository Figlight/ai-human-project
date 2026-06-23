<template>
  <div class="digital-human-config">
    <div class="page-header">
      <h1>🤖 数字人配置</h1>
      <p class="subtitle">配置数字人的外观、服装、声音等，使其更贴合景区文化特色</p>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else>
      <div class="config-layout">
        <div class="preview-panel card">
          <h3>实时预览</h3>
          <div class="preview-container">
            <DigitalHumanAvatar :state="previewState" :emotion="'happy'" :name="config.name" :title="config.title" :outfitColor="currentOutfit" :characterId="config.character_id" />
          </div>
          <div class="preview-controls">
            <button v-for="s in states" :key="s.key" class="preview-btn" :class="{ active: previewState === s.key }" @click="previewState = s.key">{{ s.label }}</button>
          </div>
        </div>

        <div class="settings-panel">
          <div class="card setting-section">
            <h3>👤 形象选择</h3>
            <div class="character-grid">
              <div v-for="char in characters" :key="char.id" class="character-card" :class="{ selected: config.character_id === char.id }" @click="config.character_id = char.id">
                <div class="char-avatar" :style="{ background: char.bg }"><span class="char-emoji">{{ char.emoji }}</span></div>
                <span class="char-name">{{ char.name }}</span>
              </div>
            </div>
          </div>

          <div class="card setting-section">
            <h3>👗 服装颜色</h3>
            <div class="outfit-grid">
              <div v-for="outfit in outfits" :key="outfit.id" class="outfit-swatch" :class="{ selected: selectedOutfit === outfit.id }" @click="selectOutfit(outfit)">
                <div class="swatch" :style="{ background: outfit.color }"></div>
                <span class="outfit-name">{{ outfit.name }}</span>
              </div>
            </div>
          </div>

          <div class="card setting-section">
            <h3>🔊 声音选择</h3>
            <div class="voice-list">
              <div v-for="voice in voices" :key="voice.id" class="voice-item" :class="{ selected: config.voice_id === voice.id }" @click="config.voice_id = voice.id">
                <div class="voice-icon">{{ voice.gender === 'female' ? '👩' : '👨' }}</div>
                <div class="voice-info">
                  <div class="voice-name">{{ voice.name }}</div>
                  <div class="voice-style">{{ voice.style }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="card setting-section">
            <h3>⚡ 语速调节</h3>
            <div class="speed-control">
              <span class="speed-label">慢</span>
              <input type="range" v-model.number="config.speed" min="0.5" max="2.0" step="0.1" class="speed-slider" />
              <span class="speed-label">快</span>
              <span class="speed-value">{{ config.speed.toFixed(1) }}x</span>
            </div>
          </div>

          <div class="card setting-section">
            <h3>✏️ 基本信息</h3>
            <div class="name-control">
              <label>数字人名称</label>
              <input v-model="config.name" class="input-field" />
              <label>称号</label>
              <input v-model="config.title" class="input-field" />
            </div>
          </div>

          <button class="btn btn-primary save-btn" @click="saveConfig">💾 保存配置</button>
        </div>
      </div>
    </template>

    <!-- Confirm Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="confirm-modal card">
        <div class="modal-header">
          <span class="modal-icon">⚠️</span>
          <h3>确认保存配置</h3>
        </div>
        <div class="modal-body">
          <p>您确定要保存当前的数字人配置吗？保存后，游客端的数字人外观、声音及语速将同步更新。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showConfirmModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="confirmSave">确认保存</button>
        </div>
      </div>
    </div>

    <!-- Toast message for success/failure -->
    <div v-if="toast" class="toast-message" :class="toast.type">
      <span class="toast-icon">{{ toast.type === 'success' ? '✅' : '❌' }}</span>
      <span class="toast-text">{{ toast.text }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import DigitalHumanAvatar from '../../components/DigitalHumanAvatar.vue'
import { api } from '../../api.js'

const loading = ref(true)
const previewState = ref('idle')
const characters = ref([])
const voices = ref([])
const outfits = ref([])
const selectedOutfit = ref('outfit1')
const currentOutfit = ref('linear-gradient(135deg, #4F6CF7, #8B5CF6)')

const config = reactive({ name: '小导', title: '智能导游', character_id: 'guide1', voice_id: 'zh-CN-XiaoxiaoNeural', speed: 1.0 })

const states = [{ key: 'idle', label: '待机' }, { key: 'listening', label: '聆听' }, { key: 'thinking', label: '思考' }, { key: 'speaking', label: '讲解' }]

const showConfirmModal = ref(false)
const saving = ref(false)
const toast = ref(null)

function showToast(text, type = 'success') {
  toast.value = { text, type }
  setTimeout(() => {
    toast.value = null
  }, 3000)
}

onMounted(async () => {
  try {
    const [charRes, voiceRes, outfitRes] = await Promise.all([api.getCharacters(), api.getVoices(), api.getOutfits()])
    if (charRes.code === 200) characters.value = charRes.data
    if (voiceRes.code === 200) voices.value = voiceRes.data
    if (outfitRes.code === 200) { outfits.value = outfitRes.data; if (outfitRes.data.length) { selectedOutfit.value = outfitRes.data[0].id; currentOutfit.value = outfitRes.data[0].color } }
    const cfgRes = await api.getConfig()
    if (cfgRes.code === 200 && cfgRes.data) {
      Object.assign(config, {
        name: cfgRes.data.name || '小导',
        title: cfgRes.data.title || '智能导游',
        character_id: cfgRes.data.character || 'guide1',
        voice_id: cfgRes.data.voice || 'zh-CN-XiaoxiaoNeural',
        speed: cfgRes.data.speed || 1.0,
      })
      if (cfgRes.data.outfit && outfits.value.length) {
        const matched = outfits.value.find(o => o.id === cfgRes.data.outfit)
        if (matched) {
          selectedOutfit.value = matched.id
          currentOutfit.value = matched.color
        }
      }
    }
  } catch (e) {
    console.warn('Failed to load config:', e)
  } finally {
    loading.value = false
  }
})

function selectOutfit(outfit) {
  selectedOutfit.value = outfit.id
  currentOutfit.value = outfit.color
}

function saveConfig() {
  showConfirmModal.value = true
}

async function confirmSave() {
  saving.value = true
  try {
    const res = await api.updateConfig({
      name: config.name,
      title: config.title,
      character_id: config.character_id,
      voice_id: config.voice_id,
      outfit_id: selectedOutfit.value,
      speed: config.speed
    })
    if (res.code === 200) {
      showToast('配置已成功保存！', 'success')
      showConfirmModal.value = false
    } else {
      showToast('保存失败：' + (res.message || '未知错误'), 'error')
    }
  } catch (e) {
    showToast('保存失败，请检查网络连接', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.digital-human-config { display: flex; flex-direction: column; gap: 20px; }
.page-header h1 { font-size: 24px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 2px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.config-layout { display: grid; grid-template-columns: 360px 1fr; gap: 20px; align-items: start; }
.preview-panel { position: sticky; top: 24px; }
.preview-panel h3 { margin-bottom: 16px; }
.preview-container { display: flex; justify-content: center; padding: 20px 0; background: #F8FAFC; border-radius: 12px; min-height: 320px; }
.preview-controls { display: flex; gap: 6px; margin-top: 16px; }
.preview-btn { flex: 1; padding: 6px 0; border-radius: 6px; font-size: 12px; font-weight: 500; background: #F1F5F9; color: var(--text-secondary); transition: all 0.2s; }
.preview-btn.active { background: var(--primary); color: white; }
.settings-panel { display: flex; flex-direction: column; gap: 16px; }
.setting-section h3 { font-size: 16px; margin-bottom: 14px; }
.character-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.character-card { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 8px; border-radius: 12px; border: 2px solid var(--border); cursor: pointer; transition: all 0.2s; }
.character-card:hover { border-color: var(--primary-light); }
.character-card.selected { border-color: var(--primary); background: #EEF2FF; }
.char-avatar { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.char-emoji { font-size: 30px; }
.char-name { font-size: 13px; font-weight: 500; }
.outfit-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.outfit-swatch { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; padding: 8px; border-radius: 10px; border: 2px solid transparent; transition: all 0.2s; }
.outfit-swatch:hover { border-color: var(--border); }
.outfit-swatch.selected { border-color: var(--primary); background: #EEF2FF; }
.swatch { width: 40px; height: 40px; border-radius: 50%; border: 2px solid rgba(0,0,0,0.06); }
.outfit-name { font-size: 12px; color: var(--text-secondary); }
.voice-list { display: flex; flex-direction: column; gap: 8px; }
.voice-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border); cursor: pointer; transition: all 0.2s; }
.voice-item:hover { border-color: var(--primary-light); }
.voice-item.selected { border-color: var(--primary); background: #EEF2FF; }
.voice-icon { font-size: 24px; }
.voice-info { flex: 1; }
.voice-name { font-weight: 600; font-size: 14px; }
.voice-style { font-size: 12px; color: var(--text-secondary); }
.speed-control { display: flex; align-items: center; gap: 12px; }
.speed-label { font-size: 12px; color: var(--text-secondary); }
.speed-slider { flex: 1; -webkit-appearance: none; height: 6px; border-radius: 3px; background: #E2E8F0; outline: none; }
.speed-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: var(--primary); cursor: pointer; }
.speed-value { font-size: 14px; font-weight: 600; color: var(--primary); min-width: 36px; text-align: right; }
.name-control { display: flex; flex-direction: column; gap: 8px; }
.name-control label { font-size: 13px; font-weight: 500; }
.save-btn { width: 100%; padding: 14px; font-size: 16px; }

/* 模态框与 Toast 样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.25s ease-out;
}

.confirm-modal {
  width: 420px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.modal-icon {
  font-size: 24px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}

.modal-body {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-footer .btn {
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 8px;
  font-weight: 500;
}

/* Toast 提示 */
.toast-message {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 1100;
  animation: slideDown 0.3s ease-out;
}

.toast-message.success {
  border-left: 4px solid #10B981;
}

.toast-message.error {
  border-left: 4px solid #EF4444;
}

.toast-icon {
  font-size: 18px;
}

.toast-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes slideDown {
  from { transform: translate(-50%, -20px); opacity: 0; }
  to { transform: translate(-50%, 0); opacity: 1; }
}
</style>
