<template>
  <div class="evidence-list">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h1>📁 证据管理</h1>
      <button class="btn btn-primary" @click="showUpload = true">上传证据</button>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
      <div class="modal">
        <h2>上传证据文件</h2>
        <div class="upload-area"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="handleDrop"
          @click="$refs.fileInput.click()">
          <p v-if="!selectedFile">📂 点击或拖拽文件到此处</p>
          <p v-else>✅ {{ selectedFile?.name }} ({{ formatSize(selectedFile?.size) }})</p>
          <input ref="fileInput" type="file" style="display: none" @change="handleFileSelect" />
        </div>
        <div class="form-group" style="margin-top: 1rem;">
          <label>描述 (可选)</label>
          <textarea v-model="description" class="form-control" rows="3"
            placeholder="简要描述这个证据文件..."></textarea>
        </div>
        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
          <button class="btn" @click="showUpload = false">取消</button>
          <button class="btn btn-primary" @click="upload" :disabled="!selectedFile || uploading">
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Evidence Table -->
    <div class="card">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>文件名</th>
              <th>类型</th>
              <th>大小</th>
              <th>MD5</th>
              <th>状态</th>
              <th>上传时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in evidenceList" :key="item.id">
              <td>{{ item.original_name }}</td>
              <td>{{ item.evidence_type }}</td>
              <td>{{ formatSize(item.file_size) }}</td>
              <td style="font-family: monospace; font-size: 0.75rem;">{{ item.md5?.slice(0, 8) }}...</td>
              <td>
                <span class="badge" :class="'badge-' + item.status">
                  {{ statusMap[item.status] || item.status }}
                </span>
              </td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td>
                <router-link :to="`/evidence/${item.id}`" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                  查看
                </router-link>
                <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"
                  @click="deleteEvidence(item.id)">删除</button>
              </td>
            </tr>
            <tr v-if="evidenceList.length === 0">
              <td colspan="7" style="text-align: center; color: var(--gray-400);">暂无证据，请先上传</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEvidenceStore } from '@/stores/evidence'

const store = useEvidenceStore()
const { evidenceList } = store

const showUpload = ref(false)
const selectedFile = ref(null)
const description = ref('')
const uploading = ref(false)
const isDragging = ref(false)

const statusMap = {
  pending: '等待分析',
  analyzing: '分析中',
  completed: '已完成',
  error: '错误'
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0]
}

const handleDrop = (e) => {
  isDragging.value = false
  selectedFile.value = e.dataTransfer.files[0]
}

const upload = async () => {
  uploading.value = true
  try {
    await store.uploadEvidence(selectedFile.value, description.value)
    showUpload.value = false
    selectedFile.value = null
    description.value = ''
  } catch (e) {
    alert('上传失败: ' + e.message)
  } finally {
    uploading.value = false
  }
}

const deleteEvidence = async (id) => {
  if (!confirm('确定要删除这个证据吗？')) return
  await store.deleteEvidence(id)
}

onMounted(() => {
  store.fetchEvidenceList()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
}

.modal h2 {
  margin-bottom: 1rem;
}
</style>
