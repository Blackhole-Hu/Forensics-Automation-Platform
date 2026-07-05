<template>
  <div class="dashboard">
    <h1>📊 仪表盘</h1>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">证据总数</div>
        <div class="stat-value">{{ dashboard?.evidence?.total || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">等待分析</div>
        <div class="stat-value">{{ dashboard?.evidence?.pending || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">分析中</div>
        <div class="stat-value">{{ dashboard?.evidence?.analyzing || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已完成</div>
        <div class="stat-value">{{ dashboard?.evidence?.completed || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">发现总数</div>
        <div class="stat-value">{{ dashboard?.findings?.total || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">关键发现</div>
        <div class="stat-value">{{ dashboard?.findings?.critical || 0 }}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">最近上传</h2>
        <router-link to="/evidence" class="btn btn-primary">查看全部</router-link>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>文件名</th>
              <th>类型</th>
              <th>大小</th>
              <th>状态</th>
              <th>上传时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in evidenceList.slice(0, 5)" :key="item.id">
              <td>{{ item.original_name }}</td>
              <td>{{ item.evidence_type }}</td>
              <td>{{ formatSize(item.file_size) }}</td>
              <td>
                <span class="badge" :class="'badge-' + item.status">
                  {{ statusMap[item.status] || item.status }}
                </span>
              </td>
              <td>{{ formatDate(item.created_at) }}</td>
            </tr>
            <tr v-if="evidenceList.length === 0">
              <td colspan="5" style="text-align: center; color: var(--gray-400);">暂无证据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEvidenceStore } from '@/stores/evidence'

const store = useEvidenceStore()
const { dashboard, evidenceList } = store

const statusMap = {
  pending: '等待分析',
  analyzing: '分析中',
  completed: '已完成',
  error: '错误'
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  store.fetchDashboard()
  store.fetchEvidenceList()
})
</script>
