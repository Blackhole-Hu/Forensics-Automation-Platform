<template>
  <div class="analysis">
    <h1>🔬 分析任务</h1>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">启动分析</h2>
      </div>
      <div class="form-group">
        <label>选择证据</label>
        <select v-model="selectedEvidence" class="form-control">
          <option value="">-- 请选择证据 --</option>
          <option v-for="item in evidenceList" :key="item.id" :value="item.id">
            {{ item.original_name }} ({{ item.evidence_type }})
          </option>
        </select>
      </div>
      <div class="form-group">
        <label>选择工具</label>
        <select v-model="selectedTool" class="form-control">
          <option value="">-- 请选择工具 --</option>
          <option v-for="tool in availableTools" :key="tool.name" :value="tool.name">
            {{ tool.description }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label>参数 (JSON, 可选)</label>
        <textarea v-model="paramsStr" class="form-control" rows="3"
          placeholder='{"profile": "Win10", "plugins": ["pslist", "netscan"]}'></textarea>
      </div>
      <button class="btn btn-primary" @click="run" :disabled="!selectedEvidence || !selectedTool">
        开始分析
      </button>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">任务列表</h2>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>工具</th>
              <th>状态</th>
              <th>进度</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id">
              <td>{{ task.tool }}</td>
              <td>
                <span class="badge" :class="'badge-' + task.status">
                  {{ task.status }}
                </span>
              </td>
              <td>
                <div class="progress-bar" style="width: 100px;">
                  <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
                </div>
                <span style="font-size: 0.75rem;">{{ task.progress }}%</span>
              </td>
              <td>{{ formatDate(task.created_at) }}</td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="4" style="text-align: center; color: var(--gray-400);">暂无任务</td>
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
const { evidenceList, tasks, availableTools } = store

const selectedEvidence = ref('')
const selectedTool = ref('')
const paramsStr = ref('')

const run = async () => {
  let params = {}
  if (paramsStr.value.trim()) {
    try {
      params = JSON.parse(paramsStr.value)
    } catch (e) {
      alert('参数 JSON 格式错误')
      return
    }
  }
  await store.runAnalysis(Number(selectedEvidence.value), selectedTool.value, params)
  selectedEvidence.value = ''
  selectedTool.value = ''
  paramsStr.value = ''
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  store.fetchEvidenceList()
  store.fetchTools()
})
</script>
