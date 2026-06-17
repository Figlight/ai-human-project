const BASE = '/api'

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  }
  const res = await fetch(url, config)
  return res.json()
}

export function getSessionId() {
  let sid = localStorage.getItem('session_id')
  if (!sid) {
    sid = 'user_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
    localStorage.setItem('session_id', sid)
  }
  return sid
}

export const api = {
  // ========== Chat ==========
  chatText(message, sessionId, useRag = true) {
    return request('/chat/text', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, message, use_rag: useRag }),
    })
  },

  chatTextStream(message, sessionId, useRag = true) {
    const body = JSON.stringify({ session_id: sessionId, message, use_rag: useRag })
    return fetch('/api/chat/text/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    })
  },

  async chatVoice(audioBlob, sessionId) {
    const form = new FormData()
    form.append('file', audioBlob, 'voice.wav')
    form.append('session_id', sessionId)
    const res = await fetch(`${BASE}/chat/voice`, { method: 'POST', body: form })
    return res.json()
  },

  async chatImage(imageBase64, sessionId) {
    const form = new FormData()
    form.append('image_base64', imageBase64)
    form.append('session_id', sessionId)
    const res = await fetch(`${BASE}/chat/image`, { method: 'POST', body: form })
    return res.json()
  },

  getHistory(sessionId) {
    return request(`/chat/history/${sessionId}`)
  },

  // ========== Knowledge ==========
  listQA(search, category) {
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (category) params.set('category', category)
    return request(`/knowledge/qa?${params}`)
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
    const res = await fetch(`${BASE}/knowledge/upload`, { method: 'POST', body: form })
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
