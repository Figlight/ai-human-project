<template>
  <div class="knowledge-view">
    <div class="page-header">
      <div>
        <h1>📚 知识库管理</h1>
        <p class="subtitle">管理景区知识文档和问答对，作为数字人的知识基础</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="showUpload = !showUpload">📄 上传文档</button>
        <button class="btn btn-primary" @click="openAddQA">✏️ 添加问答</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else>
      <div v-if="showUpload" class="upload-section card">
        <h3>上传知识文档</h3>
        <p class="upload-desc">支持 PDF、Word、TXT、Markdown 格式，系统将自动解析并向量化入库</p>
        <div class="upload-zone" @drop.prevent="onDrop" @dragover.prevent>
          <div class="upload-icon">📁</div>
          <p>拖拽文件到此处，或 <span class="upload-link" @click="$refs.fileInput.click()">点击选择文件</span></p>
          <input type="file" accept=".pdf,.doc,.docx,.txt,.md" style="display:none" ref="fileInput" @change="onFileSelect" />
        </div>
        <div v-if="uploadMsg" class="upload-msg" :class="uploadMsg.type">{{ uploadMsg.text }}</div>
      </div>

      <div class="search-bar"><input v-model="searchQuery" class="input-field" placeholder="搜索知识条目..." @input="loadQA" /></div>
      <div class="tabs-row">
        <button class="tab-btn" :class="{ active: activeTab === 'qa' }" @click="activeTab = 'qa'">📝 问答条目 ({{ qaItems.length }})</button>
        <button class="tab-btn" :class="{ active: activeTab === 'docs' }" @click="activeTab = 'docs'; loadDocs()">📄 文档列表</button>
      </div>

      <div v-if="activeTab === 'qa'" class="qa-table card">
        <div class="table-header"><span class="col-q">问题</span><span class="col-a">答案</span><span class="col-tag">分类</span><span class="col-actions">操作</span></div>
        <div v-for="item in qaItems" :key="item.id" class="table-row">
          <div class="col-q">{{ item.question }}</div>
          <div class="col-a">{{ item.answer }}</div>
          <div class="col-tag"><span class="tag">{{ item.category }}</span></div>
          <div class="col-actions">
            <button class="btn-sm" @click="editItem(item)">✏️</button>
            <button class="btn-sm danger" @click="deleteItem(item.id)">🗑️</button>
          </div>
        </div>
        <div v-if="!qaItems.length" class="empty-state"><p>暂无知识条目</p></div>
      </div>

      <div v-if="activeTab === 'docs'" class="docs-list card">
        <div v-for="doc in documents" :key="doc.id" class="doc-item">
          <div class="doc-icon">📄</div>
          <div class="doc-info">
            <div class="doc-name">{{ doc.name }}</div>
            <div class="doc-meta">
              <span>{{ doc.file_size }}</span><span>·</span><span>{{ doc.status === 'indexed' ? '已索引' : '索引中' }}</span><span>·</span><span>{{ doc.created_at?.slice(0,10) }}</span>
            </div>
          </div>
          <button class="btn-sm danger" @click="deleteDoc(doc.id)">🗑️</button>
        </div>
        <div v-if="!documents.length" class="empty-state"><p>暂无文档</p></div>
      </div>
    </template>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal card">
        <h3>{{ editingId ? '编辑问答' : '添加问答' }}</h3>
        <div class="modal-form">
          <label>问题</label>
          <input v-model="formQuestion" class="input-field" placeholder="输入问题" />
          <label>答案</label>
          <textarea v-model="formAnswer" class="input-field" rows="4" placeholder="输入答案"></textarea>
          <label>分类</label>
          <input v-model="formCategory" class="input-field" placeholder="景区概况" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="saveQA">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api.js'

const searchQuery = ref('')
const activeTab = ref('qa')
const showUpload = ref(false)
const showModal = ref(false)
const editingId = ref(null)
const formQuestion = ref('')
const formAnswer = ref('')
const formCategory = ref('景区概况')
const fileInput = ref(null)
const uploadMsg = ref(null)
const loading = ref(true)
const qaItems = ref([])
const documents = ref([])

onMounted(() => loadQA())

async function loadQA() {
  try {
    const res = await api.listQA(searchQuery.value)
    if (res.code === 200) qaItems.value = res.data || []
  } catch (e) {
    console.warn('Failed to load QA:', e)
  } finally {
    loading.value = false
  }
}

async function loadDocs() {
  try {
    const res = await api.listDocuments()
    if (res.code === 200) documents.value = res.data || []
  } catch (e) {
    console.warn('Failed to load docs:', e)
  }
}

function openAddQA() {
  editingId.value = null; formQuestion.value = ''; formAnswer.value = ''; formCategory.value = '景区概况'; showModal.value = true
}

function editItem(item) {
  editingId.value = item.id; formQuestion.value = item.question; formAnswer.value = item.answer; formCategory.value = item.category; showModal.value = true
}

async function saveQA() {
  if (!formQuestion.value.trim() || !formAnswer.value.trim()) return
  try {
    if (editingId.value) {
      await api.updateQA(editingId.value, { question: formQuestion.value, answer: formAnswer.value, category: formCategory.value })
    } else {
      await api.createQA(formQuestion.value, formAnswer.value, formCategory.value)
    }
    showModal.value = false
    await loadQA()
  } catch (e) {
    console.warn('Save QA failed:', e)
  }
}

async function deleteItem(id) {
  try { await api.deleteQA(id); await loadQA() } catch (e) { console.warn(e) }
}

async function deleteDoc(id) {
  try { await api.deleteDocument(id); await loadDocs() } catch (e) { console.warn(e) }
}

async function onFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadMsg.value = { type: 'info', text: '上传中...' }
  try {
    const res = await api.uploadDocument(file)
    if (res.code === 200) {
      uploadMsg.value = { type: 'success', text: `上传成功！${res.data.name}，共 ${res.data.chunks} 个知识片段` }
    } else {
      uploadMsg.value = { type: 'error', text: '上传失败' }
    }
  } catch (e) {
    uploadMsg.value = { type: 'error', text: '上传失败: ' + e.message }
  }
}

function onDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) onFileSelect({ target: { files: [file] } })
}
</script>

<style scoped>
.knowledge-view { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; }
.page-header h1 { font-size: 24px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 2px; }
.header-actions { display: flex; gap: 8px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.upload-section h3 { margin-bottom: 4px; }
.upload-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.upload-zone { border: 2px dashed var(--border); border-radius: 12px; padding: 32px; text-align: center; color: var(--text-secondary); transition: all 0.2s; }
.upload-zone:hover { border-color: var(--primary); background: #F8FAFF; }
.upload-icon { font-size: 40px; margin-bottom: 8px; }
.upload-link { color: var(--primary); cursor: pointer; font-weight: 500; }
.upload-msg { margin-top: 12px; padding: 10px 14px; border-radius: 8px; font-size: 14px; }
.upload-msg.success { background: #DCFCE7; color: #16A34A; }
.upload-msg.error { background: #FEE2E2; color: #DC2626; }
.upload-msg.info { background: #DBEAFE; color: #2563EB; }
.tabs-row { display: flex; gap: 8px; }
.tab-btn { padding: 8px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; background: white; border: 1px solid var(--border); color: var(--text-secondary); transition: all 0.2s; }
.tab-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
.tab-btn:hover:not(.active) { border-color: var(--primary); color: var(--primary); }
.qa-table { padding: 0; }
.table-header, .table-row { display: grid; grid-template-columns: 2fr 3fr 100px 100px; gap: 12px; padding: 12px 20px; align-items: center; }
.table-header { font-size: 13px; font-weight: 600; color: var(--text-secondary); border-bottom: 1px solid var(--border); background: #F8FAFC; }
.table-row { font-size: 14px; border-bottom: 1px solid #F1F5F9; transition: background 0.2s; }
.table-row:hover { background: #FAFBFC; }
.col-q, .col-a { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-actions { display: flex; gap: 4px; }
.btn-sm { width: 32px; height: 32px; border-radius: 6px; border: 1px solid var(--border); background: white; display: flex; align-items: center; justify-content: center; font-size: 14px; transition: all 0.2s; }
.btn-sm:hover { border-color: var(--primary); }
.btn-sm.danger:hover { border-color: var(--danger); color: var(--danger); }
.doc-item { display: flex; align-items: center; gap: 14px; padding: 14px 0; border-bottom: 1px solid #F1F5F9; }
.doc-item:last-child { border-bottom: none; }
.doc-icon { font-size: 28px; }
.doc-info { flex: 1; }
.doc-name { font-weight: 600; font-size: 14px; margin-bottom: 2px; }
.doc-meta { font-size: 12px; color: var(--text-secondary); display: flex; gap: 6px; }
.empty-state { padding: 32px; text-align: center; color: var(--text-secondary); }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { width: 540px; max-height: 80vh; overflow-y: auto; }
.modal h3 { margin-bottom: 16px; }
.modal-form { display: flex; flex-direction: column; gap: 12px; }
.modal-form label { font-size: 14px; font-weight: 500; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px; }
</style>
