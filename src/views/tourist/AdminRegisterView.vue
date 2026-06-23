<template>
  <div class="login-container">
    <div class="glass-card">
      <div class="logo-area">
        <span class="logo-icon">⚙️</span>
        <h2 class="logo-text">管理后台端注册</h2>
        <p class="logo-sub">注册景区导览服务后台管理员账号</p>
      </div>

      <form @submit.prevent="handleSubmit" class="form-body">
        <div class="input-group">
          <label for="username">管理员用户名</label>
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
          <label for="password">安全密码</label>
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
          {{ loading ? '注册中...' : '注册管理员' }}
        </button>

        <div class="back-link">
          <router-link to="/login">已有账号？返回登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api.js'

const router = useRouter()
const loading = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)

const form = reactive({
  username: '',
  password: ''
})

async function handleSubmit() {
  errorMsg.value = null
  successMsg.value = null
  
  if (form.username.trim().length < 3) {
    errorMsg.value = '管理员用户名长度不能少于3位'
    return
  }
  if (form.password.length < 4) {
    errorMsg.value = '安全密码长度不能少于4位'
    return
  }

  loading.value = true
  try {
    // Hardcode role as 'admin' for this page
    const res = await api.register(form.username.trim(), form.password, 'admin')
    if (res.code === 200) {
      successMsg.value = '管理员账号注册成功！正在跳转至登录页面...'
      form.username = ''
      form.password = ''
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      errorMsg.value = res.message || '注册失败，用户名已存在'
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
  background: linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #020617 100%);
  font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 20px;
}

.glass-card {
  width: 100%;
  max-width: 440px;
  background: rgba(30, 41, 59, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
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
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
}

.logo-text {
  font-size: 20px;
  font-weight: 800;
  text-align: center;
  color: white;
  margin: 0;
}

.logo-sub {
  font-size: 13px;
  color: #94A3B8;
  margin-top: 6px;
  margin-bottom: 0;
  text-align: center;
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
  color: #CBD5E1;
  padding-left: 4px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 4px 12px;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-wrapper:focus-within {
  border-color: #818CF8;
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.25);
}

.input-wrapper .icon {
  font-size: 16px;
  margin-right: 8px;
  color: #64748B;
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 0;
  font-size: 14px;
  color: #F8FAFC;
  outline: none;
}

.error-alert {
  background: rgba(220, 38, 38, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #F87171;
  padding: 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}

.success-alert {
  background: rgba(5, 150, 105, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34D399;
  padding: 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}

.submit-btn {
  background: linear-gradient(135deg, #818CF8, #4F46E5);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.45);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-link {
  text-align: center;
  margin-top: 10px;
}

.back-link a {
  color: #818CF8;
  font-size: 13px;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.back-link a:hover {
  color: #A5B4FC;
  text-decoration: underline;
}
</style>
