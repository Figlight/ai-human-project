const BASE = '/api'

function getToken(path = '') {
  const isAdmin = path.includes('/knowledge') || 
                  path.includes('/digital-human') || 
                  path.includes('/analytics') || 
                  window.location.pathname.startsWith('/admin')
  return sessionStorage.getItem(isAdmin ? 'admin_token' : 'user_token')
}

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  
  // Inject Authorization token based on path context
  const token = getToken(path)
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config = {
    headers,
    ...options,
  }
  
  const res = await fetch(url, config)
  
  // Handle 401 Unauthorized globally
  if (res.status === 401 && !path.includes('/auth/login') && !path.includes('/auth/register')) {
    const isAdmin = path.includes('/knowledge') || 
                    path.includes('/digital-human') || 
                    path.includes('/analytics') || 
                    window.location.pathname.startsWith('/admin')
    const keyPrefix = isAdmin ? 'admin' : 'user'
    sessionStorage.removeItem(`${keyPrefix}_token`)
    sessionStorage.removeItem(`${keyPrefix}_user`)
    window.location.href = '/login'
    return
  }
  
  return res.json()
}

export function startNewSession() {
  const sid = 'user_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  sessionStorage.setItem('session_id', sid)
  return sid
}

export function getSessionId() {
  let sid = sessionStorage.getItem('session_id')
  if (!sid || sid.trim() === '') {
    sid = startNewSession()
  }
  return sid
}

export const api = {
  // ========== Auth ==========
  login(username, password) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },

  register(username, password, role = 'user') {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, role }),
    })
  },

  getMe() {
    return request('/auth/me')
  },

  // ========== Chat ==========
  chatText(message, sessionId, useRag = true, preference = null) {
    return request('/chat/text', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, message, use_rag: useRag, preference }),
    })
  },

  chatTextStream(message, sessionId, useRag = true, preference = null) {
    const body = JSON.stringify({ session_id: sessionId, message, use_rag: useRag, preference })
    const token = getToken('/chat/text/stream')
    const headers = { 'Content-Type': 'application/json' }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    return fetch('/api/chat/text/stream', {
      method: 'POST',
      headers,
      body,
    })
  },

  async chatVoice(audioBlob, sessionId, preference = null) {
    const form = new FormData()
    form.append('file', audioBlob, 'voice.wav')
    form.append('session_id', sessionId)
    if (preference) {
      form.append('preference', preference)
    }
    const token = getToken('/chat/voice')
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    const res = await fetch(`${BASE}/chat/voice`, { method: 'POST', headers, body: form })
    return res.json()
  },

  async transcribeVoice(audioBlob) {
    const form = new FormData()
    form.append('file', audioBlob, 'voice.wav')
    const token = getToken('/chat/asr')
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    const res = await fetch(`${BASE}/chat/asr`, { method: 'POST', headers, body: form })
    return res.json()
  },


  async chatImage(imageBase64, sessionId, preference = null) {
    const form = new FormData()
    form.append('image_base64', imageBase64)
    form.append('session_id', sessionId)
    if (preference) {
      form.append('preference', preference)
    }
    const token = getToken('/chat/image')
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    const res = await fetch(`${BASE}/chat/image`, { method: 'POST', headers, body: form })
    return res.json()
  },

  getSessions() {
    return request('/chat/sessions')
  },

  deleteSession(sessionId) {
    return request(`/chat/session/${sessionId}`, {
      method: 'DELETE',
    })
  },

  getHistory(sessionId) {
    return request(`/chat/history/${sessionId}`)
  },

  synthesizeTTS(text) {
    return request('/chat/tts', {
      method: 'POST',
      body: JSON.stringify({ message: text })
    })
  },

  // ========== Knowledge ==========
  listQA(search, category) {
    return request(`/knowledge/qa?${search ? `search=${search}` : ''}${category ? `&category=${category}` : ''}`)
  },

  createQA(question, answer, category) {
    return request('/knowledge/qa', {
      method: 'POST',
      body: JSON.stringify({ question, answer, category }),
    })
  },

  updateQA(id, data) {
    return request(`/knowledge/qa/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteQA(id) {
    return request(`/knowledge/qa/${id}`, { method: 'DELETE' })
  },

  async uploadDocument(file) {
    const form = new FormData()
    form.append('file', file)
    const token = getToken('/knowledge/upload')
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    const res = await fetch(`${BASE}/knowledge/upload`, { method: 'POST', headers, body: form })
    return res.json()
  },

  listDocuments() {
    return request('/knowledge/documents')
  },

  deleteDocument(id) {
    return request(`/knowledge/documents/${id}`, { method: 'DELETE' })
  },

  // ========== Digital Human ==========
  getConfig() {
    return request('/digital-human/config')
  },

  updateConfig(config) {
    return request('/digital-human/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    })
  },

  getCharacters() {
    return request('/digital-human/characters')
  },

  getVoices() {
    return request('/digital-human/voices')
  },

  getOutfits() {
    return request('/digital-human/outfits')
  },

  // ========== Analytics ==========
  getSummary() {
    return request('/analytics/summary')
  },

  getEmotionTrend(days = 7) {
    return request(`/analytics/emotion-trend?days=${days}`)
  },

  getKeywords() {
    return request('/analytics/keywords')
  },

  getSuggestions() {
    return request('/analytics/suggestions')
  },

  getConversationSamples() {
    return request('/analytics/conversation-samples')
  },

  getTopQuestions(limit = 10) {
    return request(`/analytics/top-questions?limit=${limit}`)
  },

  submitFeedback(satisfaction, suggestion, sessionId) {
    return request('/analytics/feedback', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, satisfaction, suggestion }),
    })
  },

  // ========== Attractions ==========
  listAttractions() {
    return request('/attractions')
  },

  listTags() {
    return request('/attractions/tags')
  },

  listRoutes() {
    return request('/attractions/routes')
  },

  recommendRoutes(tags) {
    return request('/attractions/routes/recommend', {
      method: 'POST',
      body: JSON.stringify({ tags }),
    })
  },

  getSpotDescription(name) {
    return request(`/attractions/spot-description/${encodeURIComponent(name)}`)
  },

  // ========== Geocode ==========
  reverseGeocode(latitude, longitude) {
    return request('/geocode/reverse', {
      method: 'POST',
      body: JSON.stringify({ latitude, longitude }),
    })
  },
}
