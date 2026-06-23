<template>
  <div class="login-container">
    <div class="glass-card">
      <div class="logo-area">
        <span class="logo-icon">🏔️</span>
        <h2 class="logo-text">景区导览服务 AI 数字人</h2>
      </div>

      <div class="tab-header">
        <button 
          :class="['tab-btn', { active: activeTab === 'login' }]" 
          @click="activeTab = 'login'"
        >
          账号登录
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'register' }]" 
          @click="activeTab = 'register'"
        >
          免费注册
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="form-body">
        <div class="input-group">
          <label for="username">用户名</label>
          <div class="input-wrapper">
            <span class="icon">👤</span>
            <input 
              type="text" 
              id="username" 
              v-model="form.username" 
              placeholder="请输入用户名 (至少3位)" 
              required
            />
          </div>
        </div>

        <div class="input-group">
          <label for="password">密码</label>
          <div class="input-wrapper">
            <span class="icon">🔑</span>
            <input 
              type="password" 
              id="password" 
              v-model="form.password" 
              placeholder="请输入密码 (至少4位)" 
              required
            />
          </div>
        </div>

        <div v-if="errorMsg" class="error-alert">
          ⚠️ {{ errorMsg }}
        </div>
        <div v-if="successMsg" class="success-alert">
          ✅ {{ successMsg }}
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '处理中...' : (activeTab === 'login' ? '登 录' : '注 册') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api.js'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)

const form = reactive({
  username: '',
  password: '',
  role: 'user'
})

async function handleSubmit() {
  errorMsg.value = null
  successMsg.value = null
  
  if (form.username.trim().length < 3) {
    errorMsg.value = '用户名长度不能少于3位'
    return
  }
  if (form.password.length < 4) {
    errorMsg.value = '密码长度不能少于4位'
    return
  }

  loading.value = true
  try {
    if (activeTab.value === 'login') {
      const res = await api.login(form.username.trim(), form.password)
      if (res.code === 200 && res.data) {
        successMsg.value = '登录成功，正在跳转...'
        
        // Isolate tokens based on role prefix
        const keyPrefix = res.data.role === 'admin' ? 'admin' : 'user'
        sessionStorage.setItem(`${keyPrefix}_token`, res.data.token)
        sessionStorage.setItem(`${keyPrefix}_user`, JSON.stringify({
          username: res.data.username,
          role: res.data.role
        }))
        
        // Only clear active session for tourist users, not admin
        if (res.data.role !== 'admin') {
          sessionStorage.removeItem('session_id')
        }
        
        setTimeout(() => {
          if (res.data.role === 'admin') {
            router.push('/admin')
          } else {
            router.push('/chat')
          }
        }, 1000)
      } else {
        errorMsg.value = res.message || '登录失败，请检查用户名或密码'
      }
    } else {
      const res = await api.register(form.username.trim(), form.password, 'user')
      if (res.code === 200) {
        successMsg.value = '注册成功！请切换到登录页进行登录'
        form.username = ''
        form.password = ''
        setTimeout(() => {
          activeTab.value = 'login'
          successMsg.value = null
        }, 1500)
      } else {
        errorMsg.value = res.message || '注册失败，用户名可能已存在'
      }
    }
  } catch (e) {
    errorMsg.value = '服务器连接失败，请检查后端运行状态'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 30%, #312E81 100%);
  font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 20px;
}

.glass-card {
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  padding: 40px;
  display: flex;
  flex-direction: column;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 44px;
  margin-bottom: 12px;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}

.logo-text {
  font-size: 20px;
  font-weight: 800;
  text-align: center;
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.tab-header {
  display: flex;
  background: #F1F5F9;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #64748B;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: white;
  color: #4F46E5;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  padding-left: 4px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 4px 12px;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-wrapper:focus-within {
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.input-wrapper .icon {
  font-size: 16px;
  margin-right: 8px;
  color: #94A3B8;
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 0;
  font-size: 14px;
  color: #1E293B;
  outline: none;
}

.error-alert {
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  color: #DC2626;
  padding: 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}

.success-alert {
  background: #ECFDF5;
  border: 1px solid #6EE7B7;
  color: #059669;
  padding: 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}

.submit-btn {
  background: linear-gradient(135deg, #6366F1, #4F46E5);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
