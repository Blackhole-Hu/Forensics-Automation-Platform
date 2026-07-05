import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 证据 API
export const evidenceAPI = {
  upload(file, description) {
    const formData = new FormData()
    formData.append('file', file)
    if (description) formData.append('description', description)
    return api.post('/evidence/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  list(params = {}) {
    return api.get('/evidence/', { params })
  },

  get(id) {
    return api.get(`/evidence/${id}`)
  },

  delete(id) {
    return api.delete(`/evidence/${id}`)
  },

  getFindings(evidenceId, params = {}) {
    return api.get(`/evidence/${evidenceId}/findings`, { params })
  },

  getChain(evidenceId) {
    return api.get(`/evidence/${evidenceId}/chain`)
  }
}

// 分析 API
export const analysisAPI = {
  run(evidenceId, tool, params) {
    const formData = new FormData()
    formData.append('evidence_id', evidenceId)
    formData.append('tool', tool)
    if (params) formData.append('params', JSON.stringify(params))
    return api.post('/analysis/run', formData)
  },

  listTools() {
    return api.get('/analysis/tools')
  },

  getTasks(evidenceId) {
    return api.get(`/analysis/${evidenceId}`)
  },

  getTask(taskId) {
    return api.get(`/analysis/task/${taskId}`)
  }
}

// Dashboard API
export const dashboardAPI = {
  get() {
    return api.get('/dashboard')
  }
}

// WebSocket
export class EvidenceWebSocket {
  constructor(evidenceId) {
    this.evidenceId = evidenceId
    this.ws = null
    this.reconnectTimer = null
    this.pingTimer = null
  }

  connect(onMessage) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    this.ws = new WebSocket(`${protocol}//${host}/ws/${this.evidenceId}`)

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }

    this.ws.onclose = () => {
      this.reconnect()
    }

    this.startPing()
  }

  reconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect(onMessage)
    }, 3000)
  }

  startPing() {
    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  disconnect() {
    if (this.pingTimer) clearInterval(this.pingTimer)
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    if (this.ws) this.ws.close()
  }
}

export default api
