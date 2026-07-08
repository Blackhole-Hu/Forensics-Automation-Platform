<template>
  <div class="report">
    <h1>📝 报告生成</h1>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">生成取证分析报告</h2>
      </div>
      <p style="color: var(--gray-500); margin-bottom: 1rem;">
        选择已完成的证据，系统将自动汇总分析结果生成报告。
      </p>

      <div class="form-group">
        <label>选择证据</label>
        <select v-model="selectedEvidence" class="form-control">
          <option value="">-- 请选择证据 --</option>
          <option v-for="item in evidenceList" :key="item.id" :value="item.id">
            {{ item.original_name }} ({{ item.status }})
          </option>
        </select>
      </div>

      <button class="btn btn-primary" @click="generate" :disabled="!selectedEvidence || generating">
        {{ generating ? '生成中...' : '生成报告' }}
      </button>

      <div v-if="reportData" class="report-content" style="margin-top: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3>📄 取证分析报告</h3>
          <button class="btn" @click="copyReport">📋 复制</button>
        </div>
        <pre style="white-space: pre-wrap; background: var(--gray-50); padding: 1.5rem; border-radius: 0.5rem; font-family: monospace; font-size: 0.875rem; max-height: 600px; overflow-y: auto;">{{ reportData.report }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEvidenceStore } from '@/stores/evidence'
import api from '@/services/api'

const store = useEvidenceStore()
const { evidenceList } = store

const selectedEvidence = ref('')
const reportData = ref(null)
const generating = ref(false)

const generate = async () => {
  generating.value = true
  try {
    const formData = new FormData()
    formData.append('evidence_id', selectedEvidence.value)
    const res = await api.post('/report/generate', formData)
    reportData.value = res.data
  } catch (e) {
    alert('生成报告失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}

const copyReport = () => {
  if (reportData.value) {
    navigator.clipboard.writeText(reportData.value.report)
    alert('已复制到剪贴板')
  }
}

onMounted(() => {
  store.fetchEvidenceList()
})
</script>
