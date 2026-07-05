import { defineStore } from 'pinia'
import { ref } from 'vue'
import { evidenceAPI, analysisAPI, dashboardAPI } from '@/services/api'

export const useEvidenceStore = defineStore('evidence', () => {
  const evidenceList = ref([])
  const currentEvidence = ref(null)
  const findings = ref([])
  const evidenceChain = ref([])
  const tasks = ref([])
  const availableTools = ref([])
  const dashboard = ref(null)
  const loading = ref(false)

  async function fetchDashboard() {
    try {
      const res = await dashboardAPI.get()
      dashboard.value = res.data
    } catch (e) {
      console.error('Failed to fetch dashboard:', e)
    }
  }

  async function fetchEvidenceList(params = {}) {
    loading.value = true
    try {
      const res = await evidenceAPI.list(params)
      evidenceList.value = res.data
    } catch (e) {
      console.error('Failed to fetch evidence:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchEvidenceDetail(id) {
    loading.value = true
    try {
      const res = await evidenceAPI.get(id)
      currentEvidence.value = res.data

      const [findingsRes, chainRes, tasksRes] = await Promise.all([
        evidenceAPI.getFindings(id),
        evidenceAPI.getChain(id),
        analysisAPI.getTasks(id)
      ])

      findings.value = findingsRes.data
      evidenceChain.value = chainRes.data
      tasks.value = tasksRes.data
    } catch (e) {
      console.error('Failed to fetch evidence detail:', e)
    } finally {
      loading.value = false
    }
  }

  async function uploadEvidence(file, description) {
    try {
      const res = await evidenceAPI.upload(file, description)
      await fetchEvidenceList()
      return res.data
    } catch (e) {
      console.error('Failed to upload evidence:', e)
      throw e
    }
  }

  async function deleteEvidence(id) {
    try {
      await evidenceAPI.delete(id)
      await fetchEvidenceList()
    } catch (e) {
      console.error('Failed to delete evidence:', e)
      throw e
    }
  }

  async function runAnalysis(evidenceId, tool, params = {}) {
    try {
      const res = await analysisAPI.run(evidenceId, tool, params)
      await fetchEvidenceDetail(evidenceId)
      return res.data
    } catch (e) {
      console.error('Failed to run analysis:', e)
      throw e
    }
  }

  async function fetchTools() {
    try {
      const res = await analysisAPI.listTools()
      availableTools.value = res.data
    } catch (e) {
      console.error('Failed to fetch tools:', e)
    }
  }

  return {
    evidenceList,
    currentEvidence,
    findings,
    evidenceChain,
    tasks,
    availableTools,
    dashboard,
    loading,
    fetchDashboard,
    fetchEvidenceList,
    fetchEvidenceDetail,
    uploadEvidence,
    deleteEvidence,
    runAnalysis,
    fetchTools
  }
})
