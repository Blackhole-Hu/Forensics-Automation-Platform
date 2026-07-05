<template>
  <div class="findings">
    <h1>🔎 发现列表</h1>

    <div class="card">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>类型</th>
              <th>严重等级</th>
              <th>标题</th>
              <th>内容</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in allFindings" :key="item.id">
              <td>{{ item.finding_type }}</td>
              <td>
                <span class="badge" :class="'badge-' + item.severity">
                  {{ severityMap[item.severity] || item.severity }}
                </span>
              </td>
              <td>{{ item.title }}</td>
              <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                :title="item.content">
                {{ item.content }}
              </td>
              <td>{{ formatDate(item.created_at) }}</td>
            </tr>
            <tr v-if="allFindings.length === 0">
              <td colspan="5" style="text-align: center; color: var(--gray-400);">暂无发现，请先执行分析</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useEvidenceStore } from '@/stores/evidence'
import { evidenceAPI } from '@/services/api'

const store = useEvidenceStore()

const allFindings = ref([])

const severityMap = {
  info: '信息',
  warning: '警告',
  critical: '关键'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const fetchAllFindings = async () => {
  const evidenceList = store.evidenceList
  const findings = []
  for (const ev of evidenceList) {
    try {
      const res = await evidenceAPI.getFindings(ev.id)
      findings.push(...res.data)
    } catch (e) {
      // ignore
    }
  }
  allFindings.value = findings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

onMounted(async () => {
  await store.fetchEvidenceList()
  await fetchAllFindings()
})
</script>
