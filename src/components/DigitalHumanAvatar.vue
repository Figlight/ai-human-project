<template>
  <div class="digital-human-wrapper" :class="[state, emotion]">
    <div class="status-badge">{{ stateLabel }}</div>

    <div class="avatar-container">
      <!-- Glow ring -->
      <div class="glow-ring"></div>
      <div class="glow-ring-2"></div>

      <!-- Body -->
      <div class="body">
        <div class="outfit" :style="{ background: outfitColor }">
          <div class="collar"></div>
        </div>
      </div>

      <!-- Head -->
      <div class="head">
        <!-- Hair -->
        <div class="hair">
          <div class="hair-bangs left"></div>
          <div class="hair-bangs right"></div>
          <div class="hair-top"></div>
        </div>

        <!-- Face -->
        <div class="face">
          <!-- Eyebrows -->
          <div class="eyebrows">
            <div class="eyebrow left" :class="{ raised: state === 'listening' || state === 'thinking', lowered: state === 'speaking' && emotion === 'sad' }"></div>
            <div class="eyebrow right" :class="{ raised: state === 'listening' || state === 'thinking', lowered: state === 'speaking' && emotion === 'sad' }"></div>
          </div>

          <!-- Eyes -->
          <div class="eyes">
            <div class="eye left">
              <div class="pupil"></div>
              <div class="eyelid" :class="{ closed: state === 'thinking' }"></div>
            </div>
            <div class="eye right">
              <div class="pupil"></div>
              <div class="eyelid" :class="{ closed: state === 'thinking' }"></div>
            </div>
          </div>

          <!-- Blush -->
          <div class="blush left"></div>
          <div class="blush right"></div>

          <!-- Mouth -->
          <div class="mouth-area">
            <div class="mouth" :class="mouthClass" :style="mouthStyle"></div>
          </div>
        </div>
      </div>

      <!-- Listening wave -->
      <div v-if="state === 'listening'" class="listening-waves">
        <div class="wave" v-for="i in 3" :key="i"></div>
      </div>

      <!-- Speaking emotion indicator -->
      <div v-if="state === 'speaking'" class="emotion-indicator">
        {{ emotionIcon }}
      </div>
    </div>

    <div class="avatar-name">{{ name }}</div>
    <div class="avatar-title">{{ title }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  state: { type: String, default: 'idle' },
  emotion: { type: String, default: 'neutral' },
  name: { type: String, default: '小导' },
  title: { type: String, default: 'AI导游' },
  outfitColor: { type: String, default: 'linear-gradient(135deg, #4F6CF7, #8B5CF6)' },
  volume: { type: Number, default: 0 }
})

const stateLabel = computed(() => {
  const map = { idle: '待机中', listening: '聆听中', thinking: '思考中', speaking: '讲解中' }
  return map[props.state] || '待机中'
})

const emotionIcon = computed(() => {
  const map = { happy: '😊', surprised: '😮', sad: '😢', neutral: '😌', excited: '🤩' }
  return map[props.emotion] || '😌'
})

const mouthClass = computed(() => {
  if (props.state === 'speaking') return 'speaking'
  if (props.emotion === 'happy' || props.emotion === 'excited') return 'smile'
  if (props.emotion === 'surprised') return 'surprised'
  if (props.emotion === 'sad') return 'sad'
  return 'neutral'
})

const mouthStyle = computed(() => {
  if (props.state === 'speaking' && props.volume > 0) {
    const scaleY = 0.3 + (props.volume / 100) * 1.3
    const scaleX = 0.8 + (props.volume / 100) * 0.4
    return {
      transform: `scale(${scaleX}, ${scaleY})`,
      height: '10px',
      width: '12px',
      background: '#D4737A',
      borderRadius: '50%',
      animation: 'none'
    }
  }
  return {}
})
</script>

<style scoped>
.digital-human-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
}

.status-badge {
  padding: 3px 14px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: #EEF2FF;
  color: var(--primary);
  transition: all 0.3s;
}
.speaking .status-badge { background: #DCFCE7; color: #16A34A; }
.listening .status-badge { background: #FEF3C7; color: #D97706; }
.thinking .status-badge { background: #F3E8FF; color: #9333EA; }

.avatar-container {
  position: relative;
  width: 200px;
  height: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

/* Glow rings */
.glow-ring, .glow-ring-2 {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  bottom: 10px;
  transition: all 0.5s;
}
.glow-ring {
  background: radial-gradient(circle, rgba(79,108,247,0.15) 0%, transparent 70%);
  animation: pulse-glow 3s ease-in-out infinite;
}
.speaking .glow-ring {
  background: radial-gradient(circle, rgba(16,185,129,0.2) 0%, transparent 70%);
  animation: pulse-glow 0.8s ease-in-out infinite;
}
.listening .glow-ring {
  background: radial-gradient(circle, rgba(245,158,11,0.2) 0%, transparent 70%);
  animation: pulse-glow 1s ease-in-out infinite;
}
.glow-ring-2 {
  width: 260px;
  height: 260px;
  opacity: 0.5;
  animation: pulse-glow 4s ease-in-out infinite 0.5s;
}
@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 1; }
}

/* Body */
.body {
  width: 100px;
  height: 90px;
  border-radius: 20px 20px 30px 30px;
  position: relative;
  z-index: 2;
}
.outfit {
  width: 100%;
  height: 100%;
  border-radius: 20px 20px 30px 30px;
  position: relative;
}
.collar {
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 12px;
  background: white;
  border-radius: 0 0 8px 8px;
}

/* Head */
.head {
  width: 130px;
  height: 145px;
  position: relative;
  z-index: 3;
  animation: float 3s ease-in-out infinite;
}
.listening .head { animation: tilt-head 2s ease-in-out infinite; }
.speaking .head { animation: nod 2s ease-in-out infinite; }
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
@keyframes tilt-head {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(5deg); }
}
@keyframes nod {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* Hair */
.hair {
  position: absolute;
  top: -5px;
  left: 0;
  width: 100%;
  height: 65px;
  z-index: 4;
}
.hair-top {
  width: 100%;
  height: 100%;
  background: #4A3728;
  border-radius: 65px 65px 20px 20px;
}
.hair-bangs {
  position: absolute;
  top: 10px;
  width: 45%;
  height: 40px;
  background: #4A3728;
  border-radius: 0 0 50% 50%;
}
.hair-bangs.left { left: 5px; }
.hair-bangs.right { right: 5px; }

/* Face */
.face {
  position: absolute;
  top: 10px;
  left: 0;
  width: 100%;
  height: 135px;
  background: #FFD5C2;
  border-radius: 50% 50% 45% 45%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Eyebrows */
.eyebrows {
  display: flex;
  gap: 28px;
  margin-top: 32px;
}
.eyebrow {
  width: 24px;
  height: 4px;
  background: #4A3728;
  border-radius: 2px;
  transition: all 0.3s;
}
.eyebrow.raised { transform: translateY(-4px); }
.eyebrow.lowered { transform: translateY(3px); }

/* Eyes */
.eyes {
  display: flex;
  gap: 22px;
  margin-top: 8px;
}
.eye {
  width: 22px;
  height: 24px;
  background: white;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.pupil {
  width: 10px;
  height: 10px;
  background: #2D1B69;
  border-radius: 50%;
  transition: all 0.3s;
  animation: look-around 4s ease-in-out infinite;
}
@keyframes look-around {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(3px, -1px); }
  50% { transform: translate(-2px, 1px); }
  75% { transform: translate(1px, 2px); }
}
.eyelid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #FFD5C2;
  transform: translateY(-100%);
  transition: transform 0.2s;
}
.eyelid.closed { transform: translateY(0); }
.thinking .pupil { transform: translateY(-3px) !important; animation: none; }

/* Blush */
.blush {
  position: absolute;
  top: 68px;
  width: 16px;
  height: 10px;
  background: rgba(255, 150, 150, 0.4);
  border-radius: 50%;
}
.blush.left { left: 18px; }
.blush.right { right: 18px; }

/* Mouth */
.mouth-area {
  margin-top: 6px;
  display: flex;
  justify-content: center;
}
.mouth {
  transition: all 0.15s;
}
.mouth.neutral {
  width: 14px;
  height: 4px;
  border-bottom: 2px solid #D4737A;
  border-radius: 0 0 4px 4px;
}
.mouth.smile {
  width: 18px;
  height: 8px;
  border-bottom: 3px solid #D4737A;
  border-radius: 0 0 10px 10px;
}
.mouth.sad {
  width: 16px;
  height: 8px;
  border-top: 3px solid #D4737A;
  border-radius: 10px 10px 0 0;
  margin-top: 4px;
}
.mouth.surprised {
  width: 10px;
  height: 10px;
  border: 2px solid #D4737A;
  border-radius: 50%;
  background: #FFE4E6;
}
.mouth.speaking {
  width: 12px;
  height: 10px;
  background: #D4737A;
  border-radius: 50%;
  animation: speak-mouth 0.2s ease-in-out infinite alternate;
}
@keyframes speak-mouth {
  0% { height: 4px; width: 10px; }
  100% { height: 12px; width: 14px; }
}

/* Listening waves */
.listening-waves {
  position: absolute;
  bottom: 30px;
  right: -40px;
  display: flex;
  gap: 4px;
  align-items: center;
}
.wave {
  width: 4px;
  height: 12px;
  background: var(--secondary);
  border-radius: 2px;
  animation: wave-anim 0.6s ease-in-out infinite;
}
.wave:nth-child(2) { animation-delay: 0.15s; height: 18px; }
.wave:nth-child(3) { animation-delay: 0.3s; height: 14px; }
@keyframes wave-anim {
  0%, 100% { height: 8px; }
  50% { height: 20px; }
}

/* Emotion indicator */
.emotion-indicator {
  position: absolute;
  top: -15px;
  right: -10px;
  font-size: 28px;
  animation: pop-in 0.3s ease-out;
}
@keyframes pop-in {
  0% { transform: scale(0); }
  100% { transform: scale(1); }
}

/* Name & Title */
.avatar-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}
.avatar-title {
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
