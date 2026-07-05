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
          <option v-for="item in completedEvidence" :key="item.id" :value="item.id">
            {{ item.original_name }}
          </option>
        </select>
      </div>

      <button class="btn btn-primary" @click="generate" :disabled="!selectedEvidence">
        生成报告
      </button>

      <div v-if="report" class="report-content" style="margin-top: 1.5rem;">
        <h3>报告内容</h3>
        <div style="white-space: pre-wrap; background: var(--gray-50); padding: 1rem; border-radius: 0.5rem;">
          {{ report }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEvidenceStore } from '@/stores/evidence'

const store = useEvidenceStore()

const selectedEvidence = ref('')
const report = ref('')

const completedEvidence = computed(() =>
  store.evidenceList.filter(e => e.status === 'completed')
)

const generate = async () => {
  // TODO: 调用后端报告生成 API
  report.value = `# 取证分析报告\n\n## 证据: ${store.evidenceList.find(e => e.id === Number(selectedEvidence.value))?.original_name}\n\n## 发现\n${store.findings.map(f => `- [${f.severity}] ${f.title}: ${f.content}`).join('\n')}\n\n## 证据链\n${store.evidenceChain.map(c => `- ${c.description}`).join('\n')}\n\n---\n*本报告由 CTF 电子取证平台自动生成*`
}

onMounted(() => {
  store.fetchEvidenceList()
})
</script>
